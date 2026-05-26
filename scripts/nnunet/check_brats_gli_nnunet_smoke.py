#!/usr/bin/env python3
"""Prepare a tiny BraTS-GLI datalist for MONAI nnUNetV2Runner.

This script intentionally avoids nnU-Net conversion, preprocessing and training.
It only checks a few case folders, writes an MSD-style datalist, and emits the
MONAI input YAML that can be used later for `convert_dataset`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = "configs/nnunet/brats_gli_2024_smoke.yaml"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value[0:1] in {"'", '"'} and value[-1:] == value[0]:
        return value[1:-1]
    if value.isdigit():
        return int(value)
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def load_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                raise ValueError(f"List item without key in {path}: {raw_line}")
            data[current_list_key].append(parse_scalar(line[4:]))
            continue
        if ":" not in line:
            raise ValueError(f"Unsupported YAML line in {path}: {raw_line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            data[key] = parse_scalar(value)
            current_list_key = None
        else:
            data[key] = []
            current_list_key = key

    return data


def write_simple_yaml(path: Path, data: dict[str, Any]) -> None:
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, str):
            needs_quotes = " " in value or value.startswith(".") or "/" in value
            rendered = json.dumps(value) if needs_quotes else value
            lines.append(f"{key}: {rendered}")
        else:
            lines.append(f"{key}: {value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def require_keys(config: dict[str, Any], keys: list[str], source: Path) -> None:
    missing = [key for key in keys if key not in config]
    if missing:
        raise ValueError(f"Missing required keys in {source}: {', '.join(missing)}")


def iter_case_dirs(root: Path):
    for entry in root.iterdir():
        if entry.is_dir() and entry.name.startswith("BraTS-GLI-"):
            yield entry


def expected_file(case_dir: Path, suffix: str) -> Path:
    return case_dir / f"{case_dir.name}-{suffix}.nii.gz"


def relative_to_root(path: Path, dataroot: Path) -> str:
    return path.relative_to(dataroot).as_posix()


def collect_cases(
    dataroot: Path,
    training_roots: list[str],
    modalities: list[str],
    label_suffix: str,
    sample_cases: int,
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    problems: list[str] = []

    for training_root in training_roots:
        root = dataroot / training_root
        if not root.is_dir():
            problems.append(f"Missing training root: {root}")
            continue

        for case_dir in iter_case_dirs(root):
            missing = [
                expected_file(case_dir, suffix)
                for suffix in [*modalities, label_suffix]
                if not expected_file(case_dir, suffix).is_file()
            ]
            if missing:
                problems.append(
                    f"{case_dir.name}: missing {', '.join(path.name for path in missing)}"
                )
                continue

            image_paths = [
                relative_to_root(expected_file(case_dir, suffix), dataroot)
                for suffix in modalities
            ]
            label_path = relative_to_root(expected_file(case_dir, label_suffix), dataroot)
            cases.append({"case_id": case_dir.name, "image": image_paths, "label": label_path})

            if len(cases) >= sample_cases:
                return cases

    if problems:
        print("Problems found while collecting cases:", file=sys.stderr)
        for problem in problems[:10]:
            print(f"- {problem}", file=sys.stderr)
    return cases


def create_stacked_source(
    cases: list[dict[str, Any]],
    dataroot: Path,
    source_root: Path,
) -> list[dict[str, Any]]:
    try:
        import nibabel as nib
        import numpy as np
    except ImportError as err:
        raise RuntimeError(
            "stack_modalities requires nibabel and numpy. "
            "Run this script inside the project .venv after installing dependencies."
        ) from err

    images_root = source_root / "images"
    labels_root = source_root / "labels"
    images_root.mkdir(parents=True, exist_ok=True)
    labels_root.mkdir(parents=True, exist_ok=True)

    stacked_cases: list[dict[str, Any]] = []
    for case in cases:
        case_id = str(case["case_id"])
        modality_paths = [dataroot / image_path for image_path in case["image"]]
        loaded_images = [nib.load(str(path)) for path in modality_paths]

        reference_shape = loaded_images[0].shape
        reference_affine = loaded_images[0].affine
        for path, image in zip(modality_paths[1:], loaded_images[1:]):
            if image.shape != reference_shape:
                raise ValueError(f"{case_id}: shape mismatch in {path}")
            if not np.allclose(image.affine, reference_affine):
                raise ValueError(f"{case_id}: affine mismatch in {path}")

        stacked_data = np.stack(
            [np.asarray(image.dataobj, dtype=np.float32) for image in loaded_images],
            axis=-1,
        )
        stacked_path = images_root / f"{case_id}.nii.gz"
        nib.save(nib.Nifti1Image(stacked_data, reference_affine), str(stacked_path))

        label_path = labels_root / f"{case_id}.nii.gz"
        shutil.copy2(dataroot / str(case["label"]), label_path)

        stacked_cases.append(
            {
                "case_id": case_id,
                "image": stacked_path.as_posix(),
                "label": label_path.as_posix(),
            }
        )

    return stacked_cases


def validate_training_roots(dataroot: Path, training_roots: list[str]) -> list[Path]:
    roots = [dataroot / training_root for training_root in training_roots]
    missing_roots = [root for root in roots if not root.is_dir()]
    if missing_roots:
        for root in missing_roots:
            print(f"Missing training root: {root}", file=sys.stderr)
        return []
    return roots


def build_datalist(cases: list[dict[str, Any]]) -> dict[str, Any]:
    test_items = [{"image": cases[0]["image"]}] if cases else []
    return {"training": cases, "test": test_items}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_simple_yaml(config_path)
    require_keys(
        config,
        [
            "dataset_root",
            "training_roots",
            "modalities",
            "label_suffix",
            "sample_cases",
            "stack_modalities",
            "stacked_source_output",
            "datalist_output",
            "generated_monai_input_output",
            "monai_template_input",
        ],
        config_path,
    )

    repo_root = Path.cwd()
    dataroot = Path(config["dataset_root"])
    sample_cases = int(config["sample_cases"])
    if sample_cases < 1:
        raise ValueError("sample_cases must be at least 1")

    print(f"Python: {sys.version.split()[0]}")
    print(f"MONAI installed: {'yes' if find_spec('monai') else 'no'}")
    print(f"nnU-Net v2 installed: {'yes' if find_spec('nnunetv2') else 'no'}")
    print(f"Dataset root: {dataroot}")

    if not dataroot.is_dir():
        print(f"Dataset root does not exist: {dataroot}", file=sys.stderr)
        return 2

    training_roots = list(config["training_roots"])
    resolved_training_roots = validate_training_roots(dataroot, training_roots)
    if not resolved_training_roots:
        return 2
    for root in resolved_training_roots:
        print(f"Training root found: {root}")

    cases = collect_cases(
        dataroot=dataroot,
        training_roots=training_roots,
        modalities=list(config["modalities"]),
        label_suffix=str(config["label_suffix"]),
        sample_cases=sample_cases,
    )
    if len(cases) < sample_cases:
        print(
            f"Only collected {len(cases)} valid case(s), expected {sample_cases}.",
            file=sys.stderr,
        )
        return 3

    datalist = build_datalist(cases)
    if bool(config["stack_modalities"]):
        source_root = repo_root / str(config["stacked_source_output"])
        stacked_cases = create_stacked_source(cases=cases, dataroot=dataroot, source_root=source_root)
        datalist = build_datalist(
            [
                {
                    "case_id": case["case_id"],
                    "image": str(Path(case["image"]).relative_to(repo_root)),
                    "label": str(Path(case["label"]).relative_to(repo_root)),
                }
                for case in stacked_cases
            ]
        )

    datalist_path = repo_root / str(config["datalist_output"])
    datalist_path.parent.mkdir(parents=True, exist_ok=True)
    datalist_path.write_text(json.dumps(datalist, indent=2) + "\n", encoding="utf-8")

    monai_template_path = repo_root / str(config["monai_template_input"])
    monai_input = load_simple_yaml(monai_template_path)
    monai_input["dataroot"] = str(repo_root)
    monai_input["datalist"] = str(datalist_path.relative_to(repo_root))
    generated_monai_input_path = repo_root / str(config["generated_monai_input_output"])
    write_simple_yaml(generated_monai_input_path, monai_input)

    print(f"Valid cases checked: {len(cases)}")
    print(f"Training items: {len(datalist['training'])}")
    print(f"Test items: {len(datalist['test'])}")
    print(f"Datalist written: {datalist_path}")
    print(f"MONAI input written: {generated_monai_input_path}")
    print("No nnU-Net conversion, preprocessing or training was executed.")
    print("Next command when the environment is ready:")
    print(
        ".venv/bin/python -m monai.apps.nnunet nnUNetV2Runner convert_dataset "
        f"--input_config {generated_monai_input_path.relative_to(repo_root)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
