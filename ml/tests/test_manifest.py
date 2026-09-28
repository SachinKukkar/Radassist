from pathlib import Path

import pytest

from radassist_ml.data.manifest import read_manifest, write_manifest
from radassist_ml.data.nih import build_nih_manifest
from radassist_ml.data.records import ManifestRecord

SALT = "radassist-split-v1"


def by_image_id(record: ManifestRecord) -> str:
    return record.image_id


def test_write_then_read_returns_the_same_records(tmp_path: Path, nih_raw_dir: Path) -> None:
    records = build_nih_manifest(nih_raw_dir, val_fraction=0.5, salt=SALT).records
    path = tmp_path / "manifests" / "nih.csv"

    written = write_manifest(records, path)

    assert written == len(records)
    assert sorted(read_manifest(path), key=by_image_id) == sorted(records, key=by_image_id)


def test_file_is_identical_whatever_the_input_order(tmp_path: Path, nih_raw_dir: Path) -> None:
    records = build_nih_manifest(nih_raw_dir, val_fraction=0.5, salt=SALT).records

    write_manifest(records, tmp_path / "a.csv")
    write_manifest(list(reversed(records)), tmp_path / "b.csv")

    assert (tmp_path / "a.csv").read_text() == (tmp_path / "b.csv").read_text()


def test_unknown_split_in_a_file_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text(
        "dataset,image_id,source_path,patient_id,study_id,label,split,body_part,view\n"
        "nih,a.png,a.png,nih:1,nih:a,0,holdout,chest,PA\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown split"):
        read_manifest(path)
