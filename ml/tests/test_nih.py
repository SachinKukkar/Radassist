from pathlib import Path

import pytest

from radassist_ml.data.nih import build_nih_manifest

SALT = "radassist-split-v1"


def test_only_images_on_disk_are_included(nih_raw_dir: Path) -> None:
    result = build_nih_manifest(nih_raw_dir, val_fraction=0.5, salt=SALT)

    assert len(result.records) == 11
    assert result.missing_images == 1


def test_effusion_label_comes_from_finding_labels(nih_raw_dir: Path) -> None:
    result = build_nih_manifest(nih_raw_dir, val_fraction=0.5, salt=SALT)

    positives = {record.image_id for record in result.records if record.label == 1}
    assert positives == {"00000003_000.png", "00000006_000.png", "00000009_000.png"}


def test_official_test_list_becomes_the_test_split(nih_raw_dir: Path) -> None:
    result = build_nih_manifest(nih_raw_dir, val_fraction=0.5, salt=SALT)

    test_images = {record.image_id for record in result.records if record.split == "test"}
    assert test_images == {"00000001_000.png", "00000002_000.png"}


def test_all_images_of_a_patient_share_one_split(nih_raw_dir: Path) -> None:
    result = build_nih_manifest(nih_raw_dir, val_fraction=0.5, salt=SALT)

    patient_5_splits = {record.split for record in result.records if record.patient_id == "nih:5"}
    assert len(patient_5_splits) == 1


def test_fields_are_parsed(nih_raw_dir: Path) -> None:
    result = build_nih_manifest(nih_raw_dir, val_fraction=0.5, salt=SALT)

    record = next(record for record in result.records if record.image_id == "00000001_000.png")
    assert record.source_path == "images/00000001_000.png"
    assert record.patient_id == "nih:1"
    assert record.study_id == "nih:00000001_000"
    assert record.body_part == "chest"
    assert record.view == "PA"


def test_missing_labels_file_is_reported(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Data_Entry_2017"):
        build_nih_manifest(tmp_path, val_fraction=0.1, salt=SALT)
