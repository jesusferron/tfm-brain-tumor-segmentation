#!/usr/bin/env python3
"""Run nnU-Net dataset integrity verification on the smoke-test conversion."""

from __future__ import annotations

import argparse
import os
from multiprocessing import freeze_support

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/private/tmp")

from monai.apps.nnunet import nnUNetV2Runner


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-config", default="outputs/nnunet_smoke/input.yaml")
    parser.add_argument("--npfp", type=int, default=1)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    runner = nnUNetV2Runner(input_config=args.input_config)
    runner.extract_fingerprints(
        npfp=args.npfp,
        verify_dataset_integrity=True,
        clean=args.clean,
        verbose=args.verbose,
    )
    print("nnU-Net smoke-test integrity verification completed.")
    return 0


if __name__ == "__main__":
    freeze_support()
    raise SystemExit(main())
