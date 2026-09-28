# 4. Separate ML package with deterministic patient-level splits

- **Status:** Accepted
- **Date:** 2026-09-28

## Context

- Dataset tooling now, and training later, need heavy libraries (PyTorch) and run on different
  machines (a laptop, hosted GPU notebooks) from the API.
- One patient often has several X-rays. If a patient appears in both training and evaluation data,
  metrics are inflated (data leakage).
- Splits must be exactly reproducible by anyone, on any machine.
- The datasets are licensed. MURA's Research Use Agreement does not allow redistribution, and
  NIH asks for citation and acknowledgement.

## Decision

- `ml/` is its own uv project and an installable package, `radassist-ml` (src layout, hatchling
  build backend). It supports Python 3.11 and newer so it can be installed on hosted notebooks.
- Every dataset is converted to one manifest schema: one CSV row per image.
- Official test sets are kept as our test sets: NIH's `test_list.txt`, and MURA's public `valid`
  split (MURA's official test set is not public).
- The remaining patients are split into train/val by a SHA-256 hash of a salted patient ID
  (salt `radassist-split-v1`, 10% validation by default).
- Raw data, manifests and processed images are never committed. Reproducibility comes from the code
  plus documented commands. Dataset cards in `docs/datasets/` record sources, terms and statistics.

## Alternatives considered

| Option | Why not (for now) |
|---|---|
| scikit-learn `GroupShuffleSplit` | Result depends on the random generator, the row order and the library version |
| Committing manifest CSVs | Redistributes licensed metadata (patient IDs, labels) |
| DVC for data versioning | Needs a shared private storage remote; revisit in Step 16 |

## Consequences

- A patient's split never changes, even when more data is downloaded later.
- The validation share is approximate and splits are not stratified by label, so
  `radassist-data validate` prints the prevalence of each split and fails on empty splits.
- Changing the salt changes every split, so the salt is fixed and recorded here.
