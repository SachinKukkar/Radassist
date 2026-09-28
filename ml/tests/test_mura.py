from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from radassist_ml.data.mura import build_mura_manifest

SALT = "radassist-split-v1"


def test_only_images_on_disk_are_included(mura_raw_dir: Path) -> None:
    result = build_mura_manifest(mura_raw_dir, val_fraction=0.5, salt=SALT)

    assert len(result.records) == 9
    assert result.missing_images == 1


def test_label_comes_from_the_study_folder_name(mura_raw_dir: Path) -> None:
    result = build_mura_manifest(mura_raw_dir, val_fraction=0.5, salt=SALT)

    # Train patients 1, 3, 5 (patient 1 has two images) and valid patient 11186 are abnormal.
    assert sum(record.label for record in result.records) == 5


def test_public_valid_split_becomes_our_test_split(mura_raw_dir: Path) -> None:
    result = build_mura_manifest(mura_raw_dir, val_fraction=0.5, salt=SALT)

    test_patients = {record.patient_id for record in result.records if record.split == "test"}
    assert test_patients == {"mura:patient11185", "mura:patient11186"}


def test_fields_are_parsed(mura_raw_dir: Path) -> None:
    result = build_mura_manifest(mura_raw_dir, val_fraction=0.5, salt=SALT)

    image_id = "valid/XR_WRIST/patient11186/study1_positive/image1.png"
    record = next(record for record in result.records if record.image_id == image_id)
    assert record.source_path == f"MURA-v1.1/{image_id}"
    assert record.study_id == "mura:valid/XR_WRIST/patient11186/study1_positive"
    assert record.body_part == "wrist"
    assert record.label == 1


def test_missing_mura_folder_is_reported(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"MURA-v1\.1"):
        build_mura_manifest(tmp_path, val_fraction=0.1, salt=SALT)


def test_unexpected_study_folder_name_is_rejected(
    mura_raw_dir: Path, write_png: Callable[..., Path]
) -> None:
    relative = "MURA-v1.1/train/XR_HAND/patient00099/study1_unknown/image1.png"
    write_png(mura_raw_dir / relative, np.zeros((8, 8), dtype=np.uint8))
    with (mura_raw_dir / "MURA-v1.1" / "train_image_paths.csv").open("a", encoding="utf-8") as f:
        f.write(relative + "\n")

    with pytest.raises(ValueError, match="label"):
        build_mura_manifest(mura_raw_dir, val_fraction=0.5, salt=SALT)
