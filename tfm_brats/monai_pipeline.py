"""Minimal MONAI/PyTorch training pipeline."""

from __future__ import annotations

import csv
import os
import random
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from .brats import DatasetSpec, build_case_paths, regions_to_labelmap
from .config import write_json


class BratsRegionsd:
    """Map BraTS label maps to ET/TC/WT channels inside a MONAI dictionary."""

    def __init__(self, key: str = "label") -> None:
        self.key = key

    def __call__(self, data: dict[str, Any]) -> dict[str, Any]:
        try:
            import torch
        except ImportError as err:
            raise RuntimeError("torch is required for MONAI transforms.") from err

        result = dict(data)
        label = result[self.key]
        if torch.is_tensor(label):
            source = label.squeeze(0).long()
            regions = [
                source == 3,
                (source == 1) | (source == 3) | (source == 4),
                (source == 1) | (source == 2) | (source == 3) | (source == 4),
            ]
            result[self.key] = torch.stack(regions, dim=0).float()
        else:
            source = np.asarray(label).squeeze(0).astype(np.int16, copy=False)
            regions = [
                source == 3,
                (source == 1) | (source == 3) | (source == 4),
                (source == 1) | (source == 2) | (source == 3) | (source == 4),
            ]
            result[self.key] = np.stack(regions, axis=0).astype(np.float32)
        return result


def read_split_csv(path: Path, *, max_cases: int | None = None) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if max_cases is not None:
        rows = rows[:max_cases]
    return rows


def monai_items_from_split(
    spec: DatasetSpec,
    split_csv: Path,
    *,
    max_cases: int | None = None,
) -> list[dict[str, Any]]:
    rows = read_split_csv(split_csv, max_cases=max_cases)
    items = []
    for row in rows:
        case = build_case_paths(spec, origin=row["origin"], case_id=row["case_id"])
        items.append(
            {
                "case_id": case.case_id,
                "origin": case.origin,
                "image": [path.as_posix() for path in case.images.values()],
                "label": case.label.as_posix(),
            }
        )
    return items


def build_transforms(config: dict[str, Any], *, training: bool):
    from monai.transforms import (
        Compose,
        DivisiblePadd,
        EnsureChannelFirstd,
        EnsureTyped,
        LoadImaged,
        NormalizeIntensityd,
        RandCropByPosNegLabeld,
        RandFlipd,
        SpatialPadd,
    )

    patch_size = tuple(int(value) for value in config.get("patch_size", [96, 96, 96]))
    transforms = [
        LoadImaged(keys=["image", "label"]),
        EnsureChannelFirstd(keys=["image", "label"]),
        BratsRegionsd(key="label"),
        NormalizeIntensityd(keys=["image"], nonzero=True, channel_wise=True),
    ]
    if training:
        transforms.extend(
            [
                SpatialPadd(keys=["image", "label"], spatial_size=patch_size),
                DivisiblePadd(keys=["image", "label"], k=int(config.get("divisible_k", 16))),
                RandCropByPosNegLabeld(
                    keys=["image", "label"],
                    label_key="label",
                    spatial_size=patch_size,
                    pos=float(config.get("positive_crop_ratio", 1.0)),
                    neg=float(config.get("negative_crop_ratio", 1.0)),
                    num_samples=int(config.get("samples_per_case", 2)),
                    image_key="image",
                    image_threshold=0,
                ),
                RandFlipd(keys=["image", "label"], prob=0.5, spatial_axis=0),
                RandFlipd(keys=["image", "label"], prob=0.5, spatial_axis=1),
                RandFlipd(keys=["image", "label"], prob=0.5, spatial_axis=2),
            ]
        )
    transforms.append(EnsureTyped(keys=["image", "label"]))
    return Compose(transforms)


def build_inference_transforms(config: dict[str, Any]):
    from monai.transforms import Compose, EnsureChannelFirstd, EnsureTyped, LoadImaged, NormalizeIntensityd

    return Compose(
        [
            LoadImaged(keys=["image"]),
            EnsureChannelFirstd(keys=["image"]),
            NormalizeIntensityd(keys=["image"], nonzero=True, channel_wise=True),
            EnsureTyped(keys=["image"]),
        ]
    )


def build_cached_dataset(
    items: list[dict[str, Any]],
    transform: Any,
    *,
    cache_mode: str = "none",
    cache_rate: float = 1.0,
    cache_num: int | None = None,
    cache_dir: str | Path | None = None,
    cache_num_workers: int | None = None,
):
    """Build a MONAI dataset with an optional caching strategy.

    The deterministic prefix of ``transform`` (load + channel-first + region
    mapping + intensity normalization, plus padding for training) is what gets
    cached; MONAI re-runs the random transforms every epoch, so augmentation is
    preserved. ``cache_mode`` decides where that prefix lives:

    - ``none`` (default): plain ``Dataset``; reads and re-normalizes every step.
      Preserves the historical behaviour and is fine when the data sit on a fast
      local SSD (no I/O bottleneck).
    - ``memory``: ``CacheDataset`` keeping the prefix in RAM (use ``cache_rate``
      or ``cache_num`` to cap it; a full BraTS-GLI train split does not fit).
    - ``persistent``: ``PersistentDataset`` writing the prefix to ``cache_dir``
      on disk. This is the fix for the Google Drive bottleneck: after the first
      epoch the NIfTI reads and normalization are served from fast local disk
      (e.g. ``/content`` on Colab) instead of Drive.
    """
    from monai.data import CacheDataset, Dataset, PersistentDataset

    mode = str(cache_mode or "none").lower()
    if mode == "none":
        return Dataset(data=items, transform=transform)
    if mode == "memory":
        kwargs: dict[str, Any] = {"data": items, "transform": transform}
        if cache_num is not None:
            kwargs["cache_num"] = int(cache_num)
        else:
            kwargs["cache_rate"] = float(cache_rate)
        if cache_num_workers is not None:
            kwargs["num_workers"] = int(cache_num_workers)
        return CacheDataset(**kwargs)
    if mode == "persistent":
        if cache_dir is None:
            raise ValueError("cache_mode 'persistent' requires 'cache_dir'.")
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        return PersistentDataset(data=items, transform=transform, cache_dir=Path(cache_dir))
    raise ValueError(f"Unsupported cache_mode: {cache_mode!r} (use none | memory | persistent).")


def build_dataloader(
    items: list[dict[str, Any]],
    transform: Any,
    *,
    batch_size: int,
    num_workers: int,
    shuffle: bool,
    pin_memory: bool = False,
    persistent_workers: bool = False,
    prefetch_factor: int | None = None,
    cache_mode: str = "none",
    cache_rate: float = 1.0,
    cache_num: int | None = None,
    cache_dir: str | Path | None = None,
    cache_num_workers: int | None = None,
):
    from monai.data import DataLoader, list_data_collate

    dataset = build_cached_dataset(
        items,
        transform,
        cache_mode=cache_mode,
        cache_rate=cache_rate,
        cache_num=cache_num,
        cache_dir=cache_dir,
        cache_num_workers=cache_num_workers,
    )
    kwargs: dict[str, Any] = {
        "batch_size": batch_size,
        "shuffle": shuffle,
        "num_workers": num_workers,
        "collate_fn": list_data_collate,
        "pin_memory": pin_memory,
    }
    if num_workers > 0:
        kwargs["persistent_workers"] = persistent_workers
        if prefetch_factor is not None:
            kwargs["prefetch_factor"] = prefetch_factor
    return DataLoader(
        dataset,
        **kwargs,
    )


def resolve_device(name: str):
    import torch

    if name == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    return torch.device(name)


def set_reproducibility(seed: int) -> None:
    import torch
    from monai.utils import set_determinism

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    set_determinism(seed=seed)


def _cuda_memory_gb() -> float | None:
    try:
        import torch
    except ImportError:
        return None
    if not torch.cuda.is_available():
        return None
    return float(torch.cuda.max_memory_allocated() / (1024**3))


def _make_grad_scaler(device: Any, enabled: bool):
    import torch

    if hasattr(torch, "amp") and hasattr(torch.amp, "GradScaler"):
        try:
            return torch.amp.GradScaler(device.type, enabled=enabled)
        except TypeError:
            return torch.amp.GradScaler(enabled=enabled)
    return torch.cuda.amp.GradScaler(enabled=enabled)


def _autocast_context(device: Any, enabled: bool):
    import torch

    if not enabled:
        return nullcontext()
    if hasattr(torch, "amp") and hasattr(torch.amp, "autocast"):
        try:
            return torch.amp.autocast(device_type=device.type, enabled=enabled)
        except TypeError:
            return torch.amp.autocast(enabled=enabled)
    return torch.cuda.amp.autocast(enabled=enabled)


def build_model(model_config: dict[str, Any]):
    import torch
    from torch import nn

    in_channels = int(model_config.get("in_channels", 4))
    out_channels = int(model_config.get("out_channels", 3))
    architecture = str(model_config.get("architecture", "residual_unet_3d")).lower()

    if architecture in ("residual_unet_3d", "fusion_unet"):
        from monai.networks.nets import UNet

        class GlobalWeightedFusion(nn.Module):
            def __init__(self, channels: int) -> None:
                super().__init__()
                self.logits = nn.Parameter(torch.zeros(channels))

            def forward(self, x):
                weights = torch.softmax(self.logits, dim=0).view(1, -1, 1, 1, 1)
                return x * weights * x.shape[1]

        class AdaptiveGatingFusion(nn.Module):
            def __init__(
                self,
                channels: int,
                hidden: int = 8,
                temperature: float = 1.0,
                stats: tuple[str, ...] = ("mean",),
            ) -> None:
                super().__init__()
                # Per-channel global descriptors fed to the gate. With only "mean" the
                # signal is nearly constant across cases (z-score-normalized inputs have
                # ~zero global mean), so the gate degenerates to a static weighting. Adding
                # "std" gives a genuine per-case signal (dispersion varies with tumor/brain
                # extent), which is what makes the gating actually adaptive.
                self.stats = tuple(stats)
                self.gate = nn.Sequential(
                    nn.Linear(channels * len(self.stats), hidden),
                    nn.ReLU(inplace=True),
                    nn.Linear(hidden, channels),
                )
                # Softmax temperature > 1 softens the gate so it cannot aggressively
                # zero out modalities.
                self.temperature = float(temperature)
                # Warmup blend: 0 = pure identity (gate off), 1 = fully gated. The
                # training loop ramps it up. Non-persistent: it is a runtime schedule,
                # not a learned parameter, so it stays out of the checkpoint.
                self.register_buffer("warmup_alpha", torch.ones(()), persistent=False)
                # Mean softmax entropy of the last forward, for optional regularization
                # (discourage collapse) and diagnostics.
                self.last_entropy = None

            def _descriptors(self, x):
                feats = []
                if "mean" in self.stats:
                    feats.append(x.mean(dim=(2, 3, 4)))
                if "std" in self.stats:
                    feats.append(x.std(dim=(2, 3, 4)))
                return torch.cat(feats, dim=1)

            def forward(self, x):
                logits = self.gate(self._descriptors(x)) / self.temperature
                weights = torch.softmax(logits, dim=1)
                self.last_entropy = -(weights * weights.clamp_min(1e-8).log()).sum(dim=1).mean()
                gated = x * weights.view(x.shape[0], -1, 1, 1, 1) * x.shape[1]
                alpha = self.warmup_alpha
                return (1.0 - alpha) * x + alpha * gated

        class FusionUNet(nn.Module):
            def __init__(self, fusion: nn.Module, unet: nn.Module) -> None:
                super().__init__()
                self.fusion = fusion
                self.unet = unet

            def forward(self, x):
                return self.unet(self.fusion(x))

        channels = tuple(int(value) for value in model_config.get("channels", [16, 32, 64, 128]))
        strides = tuple(int(value) for value in model_config.get("strides", [2, 2, 2]))
        num_res_units = int(model_config.get("num_res_units", 2))
        fusion_name = str(model_config.get("fusion", "concat"))

        if fusion_name == "concat":
            fusion = nn.Identity()
        elif fusion_name == "global_weighted":
            fusion = GlobalWeightedFusion(in_channels)
        elif fusion_name == "adaptive_gating":
            stats = tuple(str(s) for s in model_config.get("fusion_stats", ["mean"]))
            fusion = AdaptiveGatingFusion(
                in_channels,
                hidden=int(model_config.get("fusion_hidden", 8)),
                temperature=float(model_config.get("fusion_temperature", 1.0)),
                stats=stats,
            )
        else:
            raise ValueError(f"Unsupported fusion mode: {fusion_name}")

        unet = UNet(
            spatial_dims=3,
            in_channels=in_channels,
            out_channels=out_channels,
            channels=channels,
            strides=strides,
            num_res_units=num_res_units,
        )
        return FusionUNet(fusion=fusion, unet=unet)

    if architecture == "swin_unetr":
        from monai.networks.nets import SwinUNETR

        return SwinUNETR(
            in_channels=in_channels,
            out_channels=out_channels,
            feature_size=int(model_config.get("feature_size", 48)),
            depths=tuple(int(value) for value in model_config.get("depths", [2, 2, 2, 2])),
            num_heads=tuple(int(value) for value in model_config.get("num_heads", [3, 6, 12, 24])),
            drop_rate=float(model_config.get("drop_rate", 0.0)),
            attn_drop_rate=float(model_config.get("attn_drop_rate", 0.0)),
            dropout_path_rate=float(model_config.get("dropout_path_rate", 0.0)),
            use_checkpoint=bool(model_config.get("use_checkpoint", False)),
            use_v2=bool(model_config.get("use_v2", False)),
        )

    if architecture == "attention_unet":
        from monai.networks.nets import AttentionUnet

        return AttentionUnet(
            spatial_dims=3,
            in_channels=in_channels,
            out_channels=out_channels,
            channels=tuple(int(value) for value in model_config.get("channels", [16, 32, 64, 128, 256])),
            strides=tuple(int(value) for value in model_config.get("strides", [2, 2, 2, 2])),
            kernel_size=int(model_config.get("kernel_size", 3)),
            up_kernel_size=int(model_config.get("up_kernel_size", 3)),
            dropout=float(model_config.get("dropout", 0.0)),
        )

    raise ValueError(f"Unsupported architecture: {architecture}")


def _batch_region_dice(logits: Any, labels: Any) -> dict[str, float]:
    import torch

    names = ("ET", "TC", "WT")
    predictions = torch.sigmoid(logits) > 0.5
    targets = labels > 0.5
    scores: dict[str, float] = {}
    for index, name in enumerate(names):
        pred = predictions[:, index]
        ref = targets[:, index]
        pred_sum = pred.sum(dim=(1, 2, 3)).float()
        ref_sum = ref.sum(dim=(1, 2, 3)).float()
        intersection = (pred & ref).sum(dim=(1, 2, 3)).float()
        score = torch.where(
            (pred_sum + ref_sum) > 0,
            (2.0 * intersection) / (pred_sum + ref_sum),
            torch.ones_like(pred_sum),
        )
        scores[f"{name}_dice"] = float(score.mean().detach().cpu())
    return scores


def _mean_dice(scores: dict[str, float]) -> float:
    keys = ["ET_dice", "TC_dice", "WT_dice"]
    values = [scores[key] for key in keys if key in scores]
    return float(np.mean(values)) if values else 0.0


def _as_3tuple(values: Any, default: tuple[int, int, int]) -> tuple[int, int, int]:
    if values is None:
        return default
    if isinstance(values, int):
        return (values, values, values)
    parsed = tuple(int(value) for value in values)
    if len(parsed) != 3:
        raise ValueError(f"Expected 3 values, got {values}")
    return parsed


def _checkpoint_payload(
    *,
    model: Any,
    optimizer: Any,
    model_config: dict[str, Any],
    training_config: dict[str, Any],
    epoch: int,
    global_step: int,
    best_metric: float,
    best_epoch: int | None,
) -> dict[str, Any]:
    return {
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict() if optimizer is not None else None,
        "model_config": model_config,
        "training_config": training_config,
        "epoch": epoch,
        "global_step": global_step,
        "best_metric": best_metric,
        "best_epoch": best_epoch,
    }


def _flatten_batch_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, bytes):
        return [value.decode("utf-8", errors="replace")]
    if isinstance(value, str):
        return [value]
    if isinstance(value, np.ndarray):
        return _flatten_batch_values(value.tolist())
    if isinstance(value, (list, tuple)):
        values: list[str] = []
        for item in value:
            values.extend(_flatten_batch_values(item))
        return values
    if hasattr(value, "detach") and hasattr(value, "cpu"):
        try:
            return _flatten_batch_values(value.detach().cpu().tolist())
        except (TypeError, ValueError):
            pass
    return [str(value)]


def _format_case_ids(batch: dict[str, Any], *, max_items: int = 6) -> str:
    raw_values = _flatten_batch_values(batch.get("case_id"))
    unique_values = list(dict.fromkeys(value for value in raw_values if value))
    if len(unique_values) <= max_items:
        return "|".join(unique_values)
    shown = "|".join(unique_values[:max_items])
    return f"{shown}|...(+{len(unique_values) - max_items})"


def _append_log_row(log_path: Path, row: dict[str, Any], *, write_header: bool = False) -> None:
    fieldnames = [
        "event",
        "epoch",
        "step",
        "batch",
        "batch_total",
        "remaining_steps",
        "case_ids",
        "patches",
        "loss",
        "ET_dice",
        "TC_dice",
        "WT_dice",
        "mean_dice",
        "lr",
        "checkpoint",
        "elapsed_seconds",
        "data_wait_seconds",
        "compute_seconds",
        "step_seconds",
        "steps_per_second",
        "patches_per_second",
        "gpu_memory_gb",
        "fusion_entropy",
    ]
    with log_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        if row:
            writer.writerow(row)


def validate_with_sliding_window(
    *,
    model: Any,
    val_loader: Any,
    device: Any,
    roi_size: tuple[int, int, int],
    sw_batch_size: int,
    overlap: float,
    max_batches: int,
    amp: bool = False,
) -> dict[str, float]:
    import torch
    from monai.inferers import sliding_window_inference

    if max_batches <= 0:
        return {}

    scores: list[dict[str, float]] = []
    model.eval()
    with torch.no_grad():
        for batch_index, batch in enumerate(val_loader):
            images = batch["image"].to(device, non_blocking=True)
            labels = batch["label"].to(device, non_blocking=True).float()
            with _autocast_context(device, amp):
                logits = sliding_window_inference(
                    images,
                    roi_size=roi_size,
                    sw_batch_size=sw_batch_size,
                    predictor=model,
                    overlap=overlap,
                )
            scores.append(_batch_region_dice(logits, labels))
            if batch_index + 1 >= max_batches:
                break

    if not scores:
        return {}
    summary: dict[str, float] = {}
    for key in scores[0]:
        summary[key] = float(np.mean([score[key] for score in scores]))
    summary["mean_dice"] = _mean_dice(summary)
    return summary


def train_one_run(
    *,
    spec: DatasetSpec,
    model_config: dict[str, Any],
    training_config: dict[str, Any],
    split_dir: Path,
    output_dir: Path,
    max_steps: int | None = None,
    max_train_cases: int | None = None,
    max_val_cases: int | None = None,
) -> dict[str, Any]:
    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib")
    os.environ.setdefault("XDG_CACHE_HOME", "/private/tmp")

    import torch
    from monai.losses import DiceCELoss

    seed = int(training_config.get("seed", 20260526))
    set_reproducibility(seed)

    train_items = monai_items_from_split(spec, split_dir / "train.csv", max_cases=max_train_cases)
    val_items = monai_items_from_split(spec, split_dir / "val.csv", max_cases=max_val_cases)
    if not train_items:
        raise ValueError(f"No training items found in {split_dir / 'train.csv'}")

    train_transform = build_transforms(training_config, training=True)
    val_transform = build_transforms(training_config, training=False)
    device = resolve_device(str(training_config.get("device", "auto")))
    num_workers = int(training_config.get("num_workers", 0))
    pin_memory = bool(training_config.get("pin_memory", device.type == "cuda"))
    persistent_workers = bool(training_config.get("persistent_workers", num_workers > 0))
    prefetch_factor_raw = training_config.get("prefetch_factor")
    prefetch_factor = int(prefetch_factor_raw) if prefetch_factor_raw is not None else None
    cache_mode = str(training_config.get("cache_mode", "none"))
    cache_rate = float(training_config.get("cache_rate", 1.0))
    cache_num_raw = training_config.get("cache_num")
    cache_num = int(cache_num_raw) if cache_num_raw is not None else None
    cache_num_workers_raw = training_config.get("cache_num_workers")
    cache_num_workers = int(cache_num_workers_raw) if cache_num_workers_raw is not None else None
    cache_dir_base = training_config.get("cache_dir")

    def _split_cache_dir(split: str) -> str | None:
        if cache_mode.lower() != "persistent" or cache_dir_base is None:
            return None
        return (Path(cache_dir_base) / split).as_posix()

    train_loader = build_dataloader(
        train_items,
        train_transform,
        batch_size=int(training_config.get("batch_size", 1)),
        num_workers=num_workers,
        shuffle=True,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
        prefetch_factor=prefetch_factor,
        cache_mode=cache_mode,
        cache_rate=cache_rate,
        cache_num=cache_num,
        cache_dir=_split_cache_dir("train"),
        cache_num_workers=cache_num_workers,
    )
    val_loader = build_dataloader(
        val_items,
        val_transform,
        batch_size=1,
        num_workers=num_workers,
        shuffle=False,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
        prefetch_factor=prefetch_factor,
        cache_mode=cache_mode,
        cache_rate=cache_rate,
        cache_num=cache_num,
        cache_dir=_split_cache_dir("val"),
        cache_num_workers=cache_num_workers,
    )

    if device.type == "cuda" and bool(training_config.get("cudnn_benchmark", False)):
        torch.backends.cudnn.benchmark = True
    amp = bool(training_config.get("amp", device.type == "cuda")) and device.type == "cuda"
    model = build_model(model_config).to(device)
    loss_fn = DiceCELoss(sigmoid=True, squared_pred=True)
    base_lr = float(training_config.get("learning_rate", 1e-4))
    base_wd = float(training_config.get("weight_decay", 1e-5))
    fusion_lr = training_config.get("fusion_lr")
    fusion_weight_decay = training_config.get("fusion_weight_decay")
    fusion_params = [param for name, param in model.named_parameters() if name.startswith("fusion.")]
    if (fusion_lr is not None or fusion_weight_decay is not None) and fusion_params:
        # Give the fusion (gate) parameters their own lr / weight_decay group. A lower
        # gate lr is one of the mitigations for the adaptive-gating instability.
        other_params = [param for name, param in model.named_parameters() if not name.startswith("fusion.")]
        optimizer = torch.optim.AdamW(
            [
                {"params": other_params},
                {
                    "params": fusion_params,
                    "lr": float(fusion_lr) if fusion_lr is not None else base_lr,
                    "weight_decay": float(fusion_weight_decay) if fusion_weight_decay is not None else base_wd,
                },
            ],
            lr=base_lr,
            weight_decay=base_wd,
        )
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=base_lr, weight_decay=base_wd)
    scaler = _make_grad_scaler(device, amp)

    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "train_log.csv"
    if log_path.exists():
        log_path.unlink()
    _append_log_row(log_path, {}, write_header=True)

    max_epochs = int(training_config.get("max_epochs", 1))
    configured_max_steps = training_config.get("max_steps")
    step_limit = max_steps if max_steps is not None else (int(configured_max_steps) if configured_max_steps else None)
    log_every_steps = int(training_config.get("log_every_steps", 1))
    validation_interval = int(training_config.get("validation_interval", 1))
    validation_batches = int(training_config.get("validation_batches", 1))
    roi_size = _as_3tuple(
        training_config.get("sliding_window_roi_size", training_config.get("patch_size")),
        default=(96, 96, 96),
    )
    sw_batch_size = int(training_config.get("sliding_window_batch_size", 1))
    overlap = float(training_config.get("sliding_window_overlap", 0.5))

    fusion_module = getattr(model, "fusion", None)
    is_adaptive_gating = fusion_module is not None and hasattr(fusion_module, "warmup_alpha")
    fusion_warmup_steps = int(training_config.get("fusion_warmup_steps", 0))
    fusion_entropy_weight = float(training_config.get("fusion_entropy_weight", 0.0))

    # Learning-rate schedule (default 'none' = constant lr, backward compatible).
    # 'cosine' does linear warmup then cosine decay to lr_min_factor*base over the
    # full step budget, per param group (so a separate fusion_lr is respected).
    lr_scheduler_name = str(training_config.get("lr_scheduler", "none")).lower()
    lr_warmup_steps = int(training_config.get("lr_warmup_steps", 0))
    lr_min_factor = float(training_config.get("lr_min_factor", 0.01))
    base_lrs = [group["lr"] for group in optimizer.param_groups]
    total_scheduled_steps = step_limit if step_limit else max_epochs * max(1, len(train_loader))

    def _apply_lr_schedule(step: int) -> None:
        if lr_scheduler_name != "cosine":
            return
        import math

        if lr_warmup_steps > 0 and step < lr_warmup_steps:
            factor = (step + 1) / lr_warmup_steps
        else:
            denom = max(1, total_scheduled_steps - lr_warmup_steps)
            progress = min(1.0, max(0.0, (step - lr_warmup_steps) / denom))
            factor = lr_min_factor + (1.0 - lr_min_factor) * 0.5 * (1.0 + math.cos(math.pi * progress))
        for group, base in zip(optimizer.param_groups, base_lrs):
            group["lr"] = base * factor

    global_step = 0
    total_patches = 0
    losses: list[float] = []
    best_metric = -1.0
    best_epoch: int | None = None
    last_validation: dict[str, float] = {}
    stop_training = False
    start_time = perf_counter()
    print(
        "Training setup: "
        f"device={device}, amp={amp}, train_cases={len(train_items)}, val_cases={len(val_items)}, "
        f"batch_size={int(training_config.get('batch_size', 1))}, "
        f"samples_per_case={int(training_config.get('samples_per_case', 2))}, "
        f"num_workers={num_workers}, pin_memory={pin_memory}, "
        f"persistent_workers={persistent_workers}, prefetch_factor={prefetch_factor}, "
        f"cache_mode={cache_mode}"
        + (f", cache_dir={cache_dir_base}" if cache_mode.lower() == "persistent" else "")
        + (f", cache_rate={cache_rate}" if cache_mode.lower() == "memory" else ""),
        flush=True,
    )
    if is_adaptive_gating:
        print(
            "Adaptive gating knobs: "
            f"temperature={float(model_config.get('fusion_temperature', 1.0))}, "
            f"warmup_steps={fusion_warmup_steps}, entropy_weight={fusion_entropy_weight}, "
            f"fusion_lr={fusion_lr}, fusion_weight_decay={fusion_weight_decay}",
            flush=True,
        )

    model.train()
    for epoch in range(max_epochs):
        epoch_losses: list[float] = []
        train_batch_total = len(train_loader)
        previous_step_end = perf_counter()
        for batch_index, batch in enumerate(train_loader):
            batch_ready = perf_counter()
            data_wait_seconds = batch_ready - previous_step_end
            images = batch["image"].to(device, non_blocking=True)
            labels = batch["label"].to(device, non_blocking=True).float()
            patches = int(images.shape[0])
            _apply_lr_schedule(global_step)
            if is_adaptive_gating and fusion_warmup_steps > 0:
                # Ramp the gate in from identity over the warmup window.
                fusion_module.warmup_alpha.fill_(min(1.0, global_step / fusion_warmup_steps))
            optimizer.zero_grad(set_to_none=True)
            step_entropy = ""
            with _autocast_context(device, amp):
                logits = model(images)
                loss = loss_fn(logits, labels)
                if is_adaptive_gating and fusion_module.last_entropy is not None:
                    step_entropy = float(fusion_module.last_entropy.detach().cpu())
                    if fusion_entropy_weight > 0.0:
                        # Maximize gate entropy (subtract from the loss) to discourage
                        # collapse onto a single modality.
                        loss = loss - fusion_entropy_weight * fusion_module.last_entropy
            if scaler.is_enabled():
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()
            loss_value = float(loss.detach().cpu())
            step_end = perf_counter()
            compute_seconds = step_end - batch_ready
            step_seconds = step_end - previous_step_end
            previous_step_end = step_end
            losses.append(loss_value)
            epoch_losses.append(loss_value)
            global_step += 1
            total_patches += patches
            batch_number = batch_index + 1
            remaining_steps = step_limit - global_step if step_limit is not None else ""
            case_ids = _format_case_ids(batch)

            if log_every_steps > 0 and (global_step == 1 or global_step % log_every_steps == 0):
                elapsed = perf_counter() - start_time
                steps_per_second = global_step / elapsed if elapsed > 0 else 0.0
                patches_per_second = total_patches / elapsed if elapsed > 0 else 0.0
                gpu_memory_gb = _cuda_memory_gb()
                _append_log_row(
                    log_path,
                    {
                        "event": "train_step",
                        "epoch": epoch + 1,
                        "step": global_step,
                        "batch": batch_number,
                        "batch_total": train_batch_total,
                        "remaining_steps": remaining_steps,
                        "case_ids": case_ids,
                        "patches": patches,
                        "loss": loss_value,
                        "lr": optimizer.param_groups[0]["lr"],
                        "elapsed_seconds": elapsed,
                        "data_wait_seconds": data_wait_seconds,
                        "compute_seconds": compute_seconds,
                        "step_seconds": step_seconds,
                        "steps_per_second": steps_per_second,
                        "patches_per_second": patches_per_second,
                        "gpu_memory_gb": gpu_memory_gb if gpu_memory_gb is not None else "",
                        "fusion_entropy": step_entropy,
                    },
                )
                gpu_text = f", gpu_mem={gpu_memory_gb:.2f}GB" if gpu_memory_gb is not None else ""
                print(
                    f"train_step epoch={epoch + 1} batch={batch_number}/{train_batch_total} "
                    f"step={global_step} remaining={remaining_steps} case_ids={case_ids} "
                    f"patches={patches} loss={loss_value:.5f} "
                    f"data_wait={data_wait_seconds:.2f}s compute={compute_seconds:.2f}s "
                    f"speed={steps_per_second:.3f} step/s patch_rate={patches_per_second:.2f}/s{gpu_text}",
                    flush=True,
                )
            if step_limit is not None and global_step >= step_limit:
                stop_training = True
                break

        should_validate = (
            bool(val_items)
            and validation_interval > 0
            and ((epoch + 1) % validation_interval == 0 or stop_training)
        )
        if should_validate:
            validation_start = perf_counter()
            print(f"validation_start epoch={epoch + 1} step={global_step}", flush=True)
            last_validation = validate_with_sliding_window(
                model=model,
                val_loader=val_loader,
                device=device,
                roi_size=roi_size,
                sw_batch_size=sw_batch_size,
                overlap=overlap,
                max_batches=validation_batches,
                amp=amp,
            )
            validation_elapsed = perf_counter() - validation_start
            metric = float(last_validation.get("mean_dice", -1.0))
            checkpoint_path = checkpoint_dir / "last.pt"
            torch.save(
                _checkpoint_payload(
                    model=model,
                    optimizer=optimizer,
                    model_config=model_config,
                    training_config=training_config,
                    epoch=epoch + 1,
                    global_step=global_step,
                    best_metric=max(best_metric, metric),
                    best_epoch=best_epoch,
                ),
                checkpoint_path,
            )
            is_best = metric > best_metric
            if is_best:
                best_metric = metric
                best_epoch = epoch + 1
                torch.save(
                    _checkpoint_payload(
                        model=model,
                        optimizer=optimizer,
                        model_config=model_config,
                        training_config=training_config,
                        epoch=epoch + 1,
                        global_step=global_step,
                        best_metric=best_metric,
                        best_epoch=best_epoch,
                    ),
                    checkpoint_dir / "best.pt",
                )
            elapsed = perf_counter() - start_time
            gpu_memory_gb = _cuda_memory_gb()
            _append_log_row(
                log_path,
                {
                    "event": "validation",
                    "epoch": epoch + 1,
                    "step": global_step,
                    "remaining_steps": step_limit - global_step if step_limit is not None else "",
                    "loss": float(np.mean(epoch_losses)) if epoch_losses else "",
                    "ET_dice": last_validation.get("ET_dice", ""),
                    "TC_dice": last_validation.get("TC_dice", ""),
                    "WT_dice": last_validation.get("WT_dice", ""),
                    "mean_dice": last_validation.get("mean_dice", ""),
                    "lr": optimizer.param_groups[0]["lr"],
                    "checkpoint": "best.pt" if is_best else "last.pt",
                    "elapsed_seconds": elapsed,
                    "steps_per_second": global_step / elapsed if elapsed > 0 else 0.0,
                    "patches_per_second": total_patches / elapsed if elapsed > 0 else 0.0,
                    "gpu_memory_gb": gpu_memory_gb if gpu_memory_gb is not None else "",
                },
            )
            print(
                f"validation_done epoch={epoch + 1} mean_dice={last_validation.get('mean_dice', '')} "
                f"elapsed={validation_elapsed:.1f}s checkpoint={'best.pt' if is_best else 'last.pt'}",
                flush=True,
            )
            model.train()

        if stop_training:
            break

    torch.save(
        _checkpoint_payload(
            model=model,
            optimizer=optimizer,
            model_config=model_config,
            training_config=training_config,
            epoch=epoch + 1 if "epoch" in locals() else 0,
            global_step=global_step,
            best_metric=best_metric,
            best_epoch=best_epoch,
        ),
        checkpoint_dir / "last.pt",
    )

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "device": str(device),
        "split_dir": split_dir.as_posix(),
        "output_dir": output_dir.as_posix(),
        "train_cases": len(train_items),
        "val_cases": len(val_items),
        "global_step": global_step,
        "total_patches": total_patches,
        "amp": amp,
        "num_workers": num_workers,
        "pin_memory": pin_memory,
        "persistent_workers": persistent_workers,
        "prefetch_factor": prefetch_factor,
        "cache_mode": cache_mode,
        "cache_rate": cache_rate if cache_mode.lower() == "memory" else None,
        "cache_num": cache_num if cache_mode.lower() == "memory" else None,
        "cache_dir": cache_dir_base if cache_mode.lower() == "persistent" else None,
        "lr_scheduler": lr_scheduler_name,
        "lr_warmup_steps": lr_warmup_steps if lr_scheduler_name == "cosine" else None,
        "lr_min_factor": lr_min_factor if lr_scheduler_name == "cosine" else None,
        "total_scheduled_steps": total_scheduled_steps if lr_scheduler_name == "cosine" else None,
        "fusion_lr": float(fusion_lr) if fusion_lr is not None else None,
        "fusion_weight_decay": float(fusion_weight_decay) if fusion_weight_decay is not None else None,
        "fusion_warmup_steps": fusion_warmup_steps if is_adaptive_gating else None,
        "fusion_entropy_weight": fusion_entropy_weight if is_adaptive_gating else None,
        "fusion_temperature": float(model_config.get("fusion_temperature", 1.0)) if is_adaptive_gating else None,
        "loss_last": losses[-1] if losses else None,
        "loss_mean": float(np.mean(losses)) if losses else None,
        "validation": last_validation,
        "best_metric": best_metric if best_metric >= 0 else None,
        "best_epoch": best_epoch,
        "checkpoint": (checkpoint_dir / "last.pt").as_posix(),
        "best_checkpoint": (checkpoint_dir / "best.pt").as_posix()
        if (checkpoint_dir / "best.pt").is_file()
        else None,
        "log_csv": log_path.as_posix(),
    }
    write_json(output_dir / "train_summary.json", summary)
    return summary


def load_model_checkpoint(
    *,
    checkpoint_path: Path,
    model_config: dict[str, Any],
    device: Any,
):
    import torch

    model = build_model(model_config).to(device)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    state_dict = checkpoint.get("model_state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
    model.load_state_dict(state_dict)
    model.eval()
    return model, checkpoint


def predict_split(
    *,
    spec: DatasetSpec,
    model_config: dict[str, Any],
    inference_config: dict[str, Any],
    split_csv: Path,
    checkpoint_path: Path,
    output_dir: Path,
    max_cases: int | None = None,
    device_name: str | None = None,
) -> dict[str, Any]:
    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib")
    os.environ.setdefault("XDG_CACHE_HOME", "/private/tmp")

    import nibabel as nib
    import torch
    from monai.inferers import sliding_window_inference

    seed = int(inference_config.get("seed", 20260526))
    set_reproducibility(seed)

    device = resolve_device(device_name or str(inference_config.get("device", "auto")))
    roi_size = _as_3tuple(
        inference_config.get("sliding_window_roi_size", inference_config.get("patch_size")),
        default=(96, 96, 96),
    )
    sw_batch_size = int(inference_config.get("sliding_window_batch_size", 1))
    overlap = float(inference_config.get("sliding_window_overlap", 0.5))
    threshold = float(inference_config.get("prediction_threshold", 0.5))

    items = monai_items_from_split(spec, split_csv, max_cases=max_cases)
    transform = build_inference_transforms(inference_config)
    model, checkpoint = load_model_checkpoint(
        checkpoint_path=checkpoint_path,
        model_config=model_config,
        device=device,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    with torch.no_grad():
        for index, item in enumerate(items, start=1):
            transformed = transform(item)
            image = transformed["image"].unsqueeze(0).to(device)
            logits = sliding_window_inference(
                image,
                roi_size=roi_size,
                sw_batch_size=sw_batch_size,
                predictor=model,
                overlap=overlap,
            )
            probabilities = torch.sigmoid(logits)[0].detach().cpu().numpy()
            label_map = regions_to_labelmap(probabilities, threshold=threshold)

            reference = nib.load(str(item["image"][0]))
            header = reference.header.copy()
            header.set_data_dtype(np.uint8)
            prediction_path = output_dir / f"{item['case_id']}.nii.gz"
            nib.save(nib.Nifti1Image(label_map, reference.affine, header), str(prediction_path))

            rows.append(
                {
                    "case_id": item["case_id"],
                    "origin": item["origin"],
                    "prediction": prediction_path.as_posix(),
                    "label": item["label"],
                }
            )
            print(f"Predicted {index}/{len(items)} cases: {item['case_id']}", flush=True)

    manifest_csv = output_dir / "predictions.csv"
    with manifest_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["case_id", "origin", "prediction", "label"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "device": str(device),
        "split_csv": split_csv.as_posix(),
        "checkpoint": checkpoint_path.as_posix(),
        "checkpoint_epoch": checkpoint.get("epoch") if isinstance(checkpoint, dict) else None,
        "checkpoint_step": checkpoint.get("global_step") if isinstance(checkpoint, dict) else None,
        "output_dir": output_dir.as_posix(),
        "manifest_csv": manifest_csv.as_posix(),
        "cases": len(rows),
        "threshold": threshold,
        "sliding_window_roi_size": list(roi_size),
        "sliding_window_batch_size": sw_batch_size,
        "sliding_window_overlap": overlap,
    }
    write_json(output_dir / "prediction_summary.json", summary)
    return summary
