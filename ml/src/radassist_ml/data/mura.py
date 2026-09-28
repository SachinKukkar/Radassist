import logging
from pathlib import Path

from radassist_ml.data.records import ManifestBuildResult, ManifestRecord, Split
from radassist_ml.data.splits import assign_split

logger = logging.getLogger(__name__)

MURA_DIR = "MURA-v1.1"
# MURA-v1.1/<official split>/XR_<BODY PART>/<patient>/<study>_<positive|negative>/<image>
EXPECTED_PATH_PARTS = 6


def build_mura_manifest(raw_dir: Path, *, val_fraction: float, salt: str) -> ManifestBuildResult:
    """Build an abnormality manifest from MURA v1.1.

    MURA's official test set is not public, so its public "valid" split becomes our test set
    and its "train" split is divided into train/val by patient.
    """
    root = raw_dir / MURA_DIR
    if not root.is_dir():
        raise FileNotFoundError(f"Expected {root}; unzip MURA-v1.1.zip into {raw_dir}")

    records: list[ManifestRecord] = []
    missing = 0
    for official_split in ("train", "valid"):
        paths_csv = root / f"{official_split}_image_paths.csv"
        for line in paths_csv.read_text(encoding="utf-8").splitlines():
            relative = line.strip()
            if not relative:
                continue
            if not (raw_dir / relative).is_file():
                missing += 1
                continue
            records.append(_to_record(relative, official_split, val_fraction, salt))
    logger.info("MURA: %d images in manifest, %d listed but not on disk", len(records), missing)
    return ManifestBuildResult(records=records, missing_images=missing)


def _to_record(
    relative: str, official_split: str, val_fraction: float, salt: str
) -> ManifestRecord:
    parts = Path(relative).parts
    if len(parts) != EXPECTED_PATH_PARTS:
        raise ValueError(f"Unexpected MURA path layout: {relative}")
    _, _, study_type, patient, study, _ = parts
    patient_id = f"mura:{patient}"
    if official_split == "valid":
        split: Split = "test"
    else:
        split = assign_split(patient_id, val_fraction, salt)
    return ManifestRecord(
        dataset="mura",
        image_id=Path(*parts[1:]).as_posix(),
        source_path=relative,
        patient_id=patient_id,
        study_id=f"mura:{Path(*parts[1:5]).as_posix()}",
        label=_study_label(study, relative),
        split=split,
        body_part=study_type.removeprefix("XR_").lower(),
    )


def _study_label(study: str, relative: str) -> int:
    """MURA stores the radiologist's study-level label in the folder name, e.g. study1_positive."""
    if study.endswith("_positive"):
        return 1
    if study.endswith("_negative"):
        return 0
    raise ValueError(f"Cannot read the label from the study folder in: {relative}")
