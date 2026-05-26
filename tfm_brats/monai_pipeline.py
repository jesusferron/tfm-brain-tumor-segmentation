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
):
    from monai.data import DataLoader, Dataset, list_data_collate

    dataset = Dataset(data=items, transform=transform)
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
    from monai.networks.nets import UNet

    class GlobalWeightedFusion(nn.Module):
        def __init__(self, channels: int) -> None:
            super().__init__()
            self.logits = nn.Parameter(torch.zeros(channels))

        def forward(self, x):
            weights = torch.softmax(self.logits, dim=0).view(1, -1, 1, 1, 1)
            return x * weights * x.shape[1]

    class AdaptiveGatingFusion(nn.Module):
        def __init__(self, channels: int, hidden: int = 8) -> None:
            super().__init__()
            self.gate = nn.Sequential(
                nn.Linear(channels, hidden),
                nn.ReLU(inplace=True),
                nn.Linear(hidden, channels),
            )

        def forward(self, x):
            pooled = x.mean(dim=(2, 3, 4))
            weights = torch.softmax(self.gate(pooled), dim=1).view(x.shape[0], -1, 1, 1, 1)
            return x * weights * x.shape[1]

    class FusionUNet(nn.Module):
        def __init__(self, fusion: nn.Module, unet: nn.Module) -> None:
            super().__init__()
            self.fusion = fusion
            self.unet = unet

        def forward(self, x):
            return self.unet(self.fusion(x))

    in_channels = int(model_config.get("in_channels", 4))
    out_channels = int(model_config.get("out_channels", 3))
    channels = tuple(int(value) for value in model_config.get("channels", [16, 32, 64, 128]))
    strides = tuple(int(value) for value in model_config.get("strides", [2, 2, 2]))
    num_res_units = int(model_config.get("num_res_units", 2))
    fusion_name = str(model_config.get("fusion", "concat"))

    if fusion_name == "concat":
        fusion = nn.Identity()
    elif fusion_name == "global_weighted":
        fusion = GlobalWeightedFusion(in_channels)
    elif fusion_name == "adaptive_gating":
        fusion = AdaptiveGatingFusion(in_channels, hidden=int(model_config.get("fusion_hidden", 8)))
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
        "loss",
        "ET_dice",
        "TC_dice",
        "WT_dice",
        "mean_dice",
        "lr",
        "checkpoint",
        "elapsed_seconds",
        "steps_per_second",
        "gpu_memory_gb",
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
    train_loader = build_dataloader(
        train_items,
        train_transform,
        batch_size=int(training_config.get("batch_size", 1)),
        num_workers=num_workers,
        shuffle=True,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
        prefetch_factor=prefetch_factor,
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
    )

    if device.type == "cuda" and bool(training_config.get("cudnn_benchmark", False)):
        torch.backends.cudnn.benchmark = True
    amp = bool(training_config.get("amp", device.type == "cuda")) and device.type == "cuda"
    model = build_model(model_config).to(device)
    loss_fn = DiceCELoss(sigmoid=True, squared_pred=True)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(training_config.get("learning_rate", 1e-4)),
        weight_decay=float(training_config.get("weight_decay", 1e-5)),
    )
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

    global_step = 0
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
        f"persistent_workers={persistent_workers}, prefetch_factor={prefetch_factor}",
        flush=True,
    )

    model.train()
    for epoch in range(max_epochs):
        epoch_losses: list[float] = []
        train_batch_total = len(train_loader)
        for batch_index, batch in enumerate(train_loader):
            images = batch["image"].to(device, non_blocking=True)
            labels = batch["label"].to(device, non_blocking=True).float()
            optimizer.zero_grad(set_to_none=True)
            with _autocast_context(device, amp):
                logits = model(images)
                loss = loss_fn(logits, labels)
            if scaler.is_enabled():
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                optimizer.step()
            loss_value = float(loss.detach().cpu())
            losses.append(loss_value)
            epoch_losses.append(loss_value)
            global_step += 1
            batch_number = batch_index + 1
            remaining_steps = step_limit - global_step if step_limit is not None else ""
            case_ids = _format_case_ids(batch)

            if log_every_steps > 0 and (global_step == 1 or global_step % log_every_steps == 0):
                elapsed = perf_counter() - start_time
                steps_per_second = global_step / elapsed if elapsed > 0 else 0.0
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
                        "loss": loss_value,
                        "lr": optimizer.param_groups[0]["lr"],
                        "elapsed_seconds": elapsed,
                        "steps_per_second": steps_per_second,
                        "gpu_memory_gb": gpu_memory_gb if gpu_memory_gb is not None else "",
                    },
                )
                gpu_text = f", gpu_mem={gpu_memory_gb:.2f}GB" if gpu_memory_gb is not None else ""
                print(
                    f"train_step epoch={epoch + 1} batch={batch_number}/{train_batch_total} "
                    f"step={global_step} remaining={remaining_steps} case_ids={case_ids} "
                    f"loss={loss_value:.5f} speed={steps_per_second:.3f} step/s{gpu_text}",
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
        "amp": amp,
        "num_workers": num_workers,
        "pin_memory": pin_memory,
        "persistent_workers": persistent_workers,
        "prefetch_factor": prefetch_factor,
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
