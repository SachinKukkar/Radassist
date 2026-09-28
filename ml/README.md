# radassist-ml

Dataset tooling for RadAssist: build manifests with patient-level splits, validate them, and
preprocess images. Training (Step 4) and model export (Step 5) will be added here.

> Education and research only. Not for clinical use.

## Setup

```bash
cd ml
uv sync
uv run radassist-data --help
```

## Getting the data

Download instructions, terms of use and known issues are in the dataset cards:
[NIH ChestX-ray14](../docs/datasets/nih-chestxray14.md) and [MURA](../docs/datasets/mura.md).
Everything under `ml/data/` is gitignored and must never be committed.

```
ml/data/
├── raw/nih/          Data_Entry_2017_v2020.csv, test_list.txt, images/…
├── raw/mura/         MURA-v1.1/…
├── manifests/        nih.csv, mura.csv            (created by `manifest`)
└── processed/        nih-512/, mura-512/          (created by `preprocess`)
```

## Usage

Run from the `ml/` folder:

```bash
# 1. Index a dataset (validates before writing)
uv run radassist-data manifest nih  --raw-dir data/raw/nih  --out data/manifests/nih.csv
uv run radassist-data manifest mura --raw-dir data/raw/mura --out data/manifests/mura.csv

# 2. Re-check a manifest and print split statistics
uv run radassist-data validate --manifest data/manifests/nih.csv

# 3. Convert images to 512 x 512 letterboxed 8-bit grayscale PNGs
uv run radassist-data preprocess --manifest data/manifests/nih.csv \
    --raw-dir data/raw/nih --out-dir data/processed/nih-512 --size 512 --workers 4
```

Exit code 0 means success; 1 means the manifest is invalid or some images failed.

## Reproducibility

- Train/val splits come from a salted SHA-256 hash of each patient ID (default salt
  `radassist-split-v1`), so the same data always gives the same splits. See ADR 0004.
- Official test sets are kept: NIH `test_list.txt`, and MURA's public `valid` split.
- `preprocess` skips images that already exist; use `--overwrite` to redo them.

## Development

```bash
make ml-check     # from the repository root: lint, type check, tests
```
