# Dataset card: NIH ChestX-ray14

| | |
|---|---|
| Provider | NIH Clinical Center |
| Download | https://nihcc.app.box.com/v/ChestXray-NIHCC |
| Paper | Wang et al., "ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised Classification and Localization of Common Thorax Diseases", CVPR 2017 |
| Label file used | `Data_Entry_2017_v2020.csv` (or `Data_Entry_2017.csv`) |
| Downloaded on | <YYYY-MM-DD> |
| Task in RadAssist | Binary classification: pleural effusion (1) vs. not (0) |

## Terms of use

<!-- After reading README_CHESTXRAY.pdf, summarise its requirements in your own words:
     what you must cite, whom you must acknowledge, and any restrictions. -->

RadAssist does not redistribute any images, labels or manifests from this dataset.

## Contents

- 112,120 frontal-view chest X-rays from 30,805 patients.
- 8-bit grayscale PNG images, 1024 x 1024 pixels, about 42 GB in total.
- Labels for 14 findings plus "No Finding", text-mined from radiology reports with NLP.
- Metadata includes patient ID, age, sex, view position (PA/AP) and follow-up number.

## How RadAssist uses it

- **Label:** 1 if `Effusion` appears in `Finding Labels`, otherwise 0.
- **Splits:** NIH's official `test_list.txt` (patient-level) is our test set. The remaining patients
  are split into train/val by a salted SHA-256 hash of the patient ID (see ADR 0004).
- **Preprocessing:** `load_grayscale` → `letterbox` to 512 x 512 → 8-bit PNG.

## Known issues and biases

- **Label noise:** labels were mined from report text, not read from the images. The authors
  estimate over 90% accuracy, but independent reviews found many labels that do not match the
  image. Test metrics are therefore approximate.
- **Shortcut learning:** models can learn hospital artefacts (tubes, drains, text markers) instead
  of disease. A documented example is pneumothorax cases that already have a chest drain.
- **View position:** AP images are typically taken of patients who cannot stand and may be sicker,
  so the view itself can act as a proxy for findings. Evaluate results by view.
- **Single institution:** performance may not transfer to other hospitals and devices.
- **Class imbalance:** effusion is a minority class. See the prevalence per split below.

## Our split statistics

<!-- Paste the table printed by `radassist-data validate` (Part 11), and note which image
     archives were downloaded, e.g. "images_001 only". -->

| split | images | patients | positive | prevalence |
|---|---|---|---|---|
| train | | | | |
| val | | | | |
| test | | | | |

## Intended use

Education and research only. Not for clinical use.
