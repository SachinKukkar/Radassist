import csv
from collections.abc import Iterable
from dataclasses import asdict, fields
from pathlib import Path

from radassist_ml.data.records import ManifestRecord, parse_split

FIELDNAMES = [field.name for field in fields(ManifestRecord)]


def write_manifest(records: Iterable[ManifestRecord], path: Path) -> int:
    """Write records to a CSV file, sorted so the file is identical on every run."""
    ordered = sorted(records, key=lambda record: (record.split, record.patient_id, record.image_id))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(asdict(record) for record in ordered)
    return len(ordered)


def read_manifest(path: Path) -> list[ManifestRecord]:
    """Read a manifest CSV written by write_manifest."""
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            ManifestRecord(
                dataset=row["dataset"],
                image_id=row["image_id"],
                source_path=row["source_path"],
                patient_id=row["patient_id"],
                study_id=row["study_id"],
                label=int(row["label"]),
                split=parse_split(row["split"]),
                body_part=row["body_part"],
                view=row["view"],
            )
            for row in csv.DictReader(handle)
        ]
