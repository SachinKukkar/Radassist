# Dataset card: MURA v1.1 (musculoskeletal radiographs)

| | |
|---|---|
| Provider | Stanford ML Group / Stanford AIMI |
| Download | https://aimi.stanford.edu/datasets/mura-msk-xrays (Research Use Agreement required) |
| Paper | Rajpurkar et al., "MURA: Large Dataset for Abnormality Detection in Musculoskeletal Radiographs", arXiv:1712.06957 |
| Version | MURA-v1.1 |
| Downloaded on | <YYYY-MM-DD> |
| Task in RadAssist | Binary classification: abnormal study (1) vs. normal (0) |

## Terms of use

<!-- Summarise the Stanford Research Use Agreement in your own words: permitted use,
     redistribution, publication and attribution requirements. -->

RadAssist does not redistribute any images, labels or manifests from this dataset. Before
publishing model weights trained on MURA (Step 5), re-read the agreement.

## Contents

- 40,561 radiographs from 14,863 studies of 12,173 patients (numbers from the paper).
- Seven upper-extremity study types: elbow, finger, forearm, hand, humerus, shoulder, wrist.
- Each study was labelled normal or abnormal by board-certified Stanford radiologists at the time
  of clinical interpretation (2001-2012).
- The official test set is not public; the public release contains `train` and `valid`.

## How RadAssist uses it

- **Label:** read from the study folder name (`study1_positive` = 1, `study1_negative` = 0).
- **Splits:** the public `valid` split is our test set. `train` patients are split into
  train/val by a salted SHA-256 hash of the patient ID (see ADR 0004).
- **Preprocessing:** `load_grayscale` → `letterbox` to 512 x 512 → 8-bit PNG.

## Known issues and biases

- **Study-level labels:** every image in an abnormal study is labelled 1, even views where the
  abnormality is not visible. Image-level labels are therefore noisy; study-level evaluation
  (combining a study's images) is more faithful to how the labels were made.
- **Shortcut risk:** metal implants, plates and casts correlate with "abnormal". A model may
  learn to detect hardware rather than pathology. Check heatmaps (Step 5).
- **Single institution and period:** one hospital, 2001-2012 equipment.
- **Scope:** upper extremity only; no demographic metadata is provided.

## Our split statistics

<!-- Paste the table printed by `radassist-data validate` (Part 11). -->

| split | images | patients | positive | prevalence |
|---|---|---|---|---|
| train | | | | |
| val | | | | |
| test | | | | |

## Intended use

Education and research only. Not for clinical use.
