"""Synthetic forward+backward benchmark of all 5 model configs on MPS.

Answers: can the M4 Pro (24 GB unified) run each architecture end-to-end at the
local patch size, and how fast? Uses random tensors (no dataset needed).
"""
import sys, time, gc, traceback
from pathlib import Path

import yaml
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))  # noop; repo on cwd
REPO = Path("/Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation")
sys.path.insert(0, str(REPO))

from tfm_brats.monai_pipeline import build_model  # noqa: E402

_p = int(sys.argv[1]) if len(sys.argv) > 1 else 96
PATCH = (_p, _p, _p)   # mac_m4_pro.yaml uses 96; colab_pro uses 128
BATCH = 1
IN_CH = 4
OUT_CH = 3
STEPS = 5              # warmup(1) + timed(4)

device = torch.device("mps")
loss_fn = torch.nn.BCEWithLogitsLoss()

configs = [
    "residual_unet_3d.yaml",
    "residual_unet_3d_global_weighted.yaml",
    "residual_unet_3d_adaptive_gating.yaml",
    "attention_unet_3d.yaml",
    "swin_unetr.yaml",
]

def count_params(m):
    return sum(p.numel() for p in m.parameters())

print(f"device=mps  patch={PATCH}  batch={BATCH}  in={IN_CH} out={OUT_CH}\n")
print(f"{'model':<42} {'params':>10} {'fwd+bwd s/step':>15} {'status':>10}")
print("-" * 82)

for cfg_name in configs:
    cfg_path = REPO / "configs" / "model" / cfg_name
    cfg = yaml.safe_load(cfg_path.read_text())
    model_cfg = cfg.get("model", cfg)
    name = model_cfg.get("name", cfg_name.replace(".yaml", ""))
    try:
        torch.mps.empty_cache()
        gc.collect()
        model = build_model(model_cfg).to(device)
        n = count_params(model)
        opt = torch.optim.Adam(model.parameters(), lr=1e-4)
        x = torch.randn(BATCH, IN_CH, *PATCH, device=device)
        y = torch.randint(0, 2, (BATCH, OUT_CH, *PATCH), device=device).float()

        times = []
        for step in range(STEPS):
            t0 = time.perf_counter()
            opt.zero_grad(set_to_none=True)
            out = model(x)
            loss = loss_fn(out, y)
            loss.backward()
            opt.step()
            torch.mps.synchronize()
            dt = time.perf_counter() - t0
            if step > 0:  # skip warmup
                times.append(dt)
        avg = sum(times) / len(times)
        mem = torch.mps.current_allocated_memory() / 1e9
        print(f"{name:<42} {n:>10,} {avg:>13.3f}s   ok (mem~{mem:.2f}GB)")
        del model, opt, x, y, out, loss
    except Exception as e:  # noqa: BLE001
        print(f"{name:<42} {'-':>10} {'-':>15}   FAIL")
        print("    " + " ".join(traceback.format_exception_only(type(e), e)).strip())
    finally:
        torch.mps.empty_cache()
        gc.collect()

print("\nNote: synthetic random tensors; measures compute+memory feasibility only.")
