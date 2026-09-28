import csv
import logging
from pathlib import Path

from radassist_ml.data.records import ManifestBuildResult, ManifestRecord, Split
from radassist_ml.data.splits import assign_split

logger = logging.getLogger(__name__)

POSITIVE_FINDING = "Effusion"


def build_nih_manifest(raw_dir: Path, *, val_fraction: float, salt: str) -> ManifestBuildResult:
    """Build a pleural-effusion manifest from NIH ChestX-ray14.

    NIH's official patient-level test list is kept as our test set; the remaining patients
    are split into train/val deterministically. Images listed in the CSV but missing on disk
    are skipped and counted, so a partial download (e.g. only images_001) still works.
    """
    labels_csv = _find_one(raw_dir, "Data_Entry_2017*.csv")
    test_images = set(_find_one(raw_dir, "test_list.txt").read_text(encoding="utf-8").split())
    on_disk = {path.name: path for path in raw_dir.rglob("*.png")}

    records: list[ManifestRecord] = []
    missing = 0
    with labels_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            image_name = row["Image Index"]
            path = on_disk.get(image_name)
            if path is None:
                missing += 1
                continue
            patient_id = f"nih:{row['Patient ID']}"
            if image_name in test_images:
                split: Split = "test"
            else:
                split = assign_split(patient_id, val_fraction, salt)
            findings = row["Finding Labels"].split("|")
            records.append(
                ManifestRecord(
                    dataset="nih",
                    image_id=image_name,
                    source_path=path.relative_to(raw_dir).as_posix(),
                    patient_id=patient_id,
                    study_id=f"nih:{Path(image_name).stem}",
                    label=int(POSITIVE_FINDING in findings),
                    split=split,
                    body_part="chest",
                    view=row.get("View Position", ""),
                )
            )
    logger.info("NIH: %d images in manifest, %d listed but not on disk", len(records), missing)
    return ManifestBuildResult(records=records, missing_images=missing)


def _find_one(raw_dir: Path, pattern: str) -> Path:
    """Find a file anywhere under raw_dir; if several match, use the last in sorted order."""
    matches = sorted(raw_dir.rglob(pattern))
    if not matches:
        raise FileNotFoundError(f"No file matching {pattern!r} under {raw_dir}")
    return matches[-1]
