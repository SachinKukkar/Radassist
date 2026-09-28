from collections.abc import Callable
from pathlib import Path

import numpy as np
from PIL import Image

from radassist_ml.data.preprocess import preprocess_manifest, processed_path
from radassist_ml.data.records import ManifestRecord


def record_for(image_id: str) -> ManifestRecord:
    return ManifestRecord(
        dataset="test",
        image_id=image_id,
        source_path=image_id,
        patient_id=f"test:{image_id}",
        study_id=image_id,
        label=0,
        split="train",
        body_part="chest",
    )


def make_images(raw: Path, write_png: Callable[..., Path], count: int) -> list[ManifestRecord]:
    records = []
    for number in range(count):
        image_id = f"folder/image{number}.png"
        write_png(raw / image_id, np.full((20, 40), 255, dtype=np.uint8))
        records.append(record_for(image_id))
    return records


def test_writes_letterboxed_grayscale_pngs(tmp_path: Path, write_png: Callable[..., Path]) -> None:
    records = make_images(tmp_path / "raw", write_png, count=1)
    out_dir = tmp_path / "out"

    result = preprocess_manifest(records, tmp_path / "raw", out_dir, size=32)

    assert (result.processed, result.skipped, result.failures) == (1, 0, [])
    with Image.open(processed_path(out_dir, records[0])) as output:
        assert output.size == (32, 32)
        assert output.mode == "L"


def test_existing_outputs_are_skipped(tmp_path: Path, write_png: Callable[..., Path]) -> None:
    records = make_images(tmp_path / "raw", write_png, count=2)
    preprocess_manifest(records, tmp_path / "raw", tmp_path / "out", size=32)

    again = preprocess_manifest(records, tmp_path / "raw", tmp_path / "out", size=32)

    assert (again.processed, again.skipped) == (0, 2)


def test_overwrite_reprocesses_everything(tmp_path: Path, write_png: Callable[..., Path]) -> None:
    records = make_images(tmp_path / "raw", write_png, count=2)
    preprocess_manifest(records, tmp_path / "raw", tmp_path / "out", size=32)

    again = preprocess_manifest(
        records, tmp_path / "raw", tmp_path / "out", size=32, overwrite=True
    )

    assert (again.processed, again.skipped) == (2, 0)


def test_broken_files_are_reported_not_raised(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    (raw / "folder").mkdir(parents=True)
    (raw / "folder" / "broken.png").write_bytes(b"this is not an image")

    result = preprocess_manifest([record_for("folder/broken.png")], raw, tmp_path / "out", size=32)

    assert result.processed == 0
    assert len(result.failures) == 1


def test_parallel_workers_process_everything(
    tmp_path: Path, write_png: Callable[..., Path]
) -> None:
    raw = tmp_path / "raw"
    records = make_images(raw, write_png, count=4)
    (raw / "folder" / "broken.png").write_bytes(b"this is not an image")
    records.append(record_for("folder/broken.png"))

    result = preprocess_manifest(records, raw, tmp_path / "out", size=32, workers=2)

    assert result.processed == 4
    assert len(result.failures) == 1
    assert all(processed_path(tmp_path / "out", record).is_file() for record in records[:4])
