from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from radassist_ml.data.records import SPLITS, ManifestRecord, Split


@dataclass(frozen=True, slots=True)
class SplitSummary:
    images: int
    patients: int
    positives: int

    @property
    def prevalence(self) -> float:
        return self.positives / self.images if self.images else 0.0


def validate_manifest(records: Sequence[ManifestRecord]) -> list[str]:
    """Return human-readable problems. An empty list means the manifest is valid."""
    if not records:
        return ["manifest is empty"]
    problems: list[str] = []

    counts = Counter(record.image_id for record in records)
    duplicates = sorted(image_id for image_id, count in counts.items() if count > 1)
    if duplicates:
        problems.append(f"{len(duplicates)} duplicate image_id values, e.g. {duplicates[:3]}")

    splits_by_patient: defaultdict[str, set[str]] = defaultdict(set)
    for record in records:
        splits_by_patient[record.patient_id].add(record.split)
    leaked = sorted(patient for patient, splits in splits_by_patient.items() if len(splits) > 1)
    if leaked:
        problems.append(f"{len(leaked)} patients appear in more than one split, e.g. {leaked[:3]}")

    present = {record.split for record in records}
    problems.extend(f"split '{split}' is empty" for split in SPLITS if split not in present)

    bad_labels = sum(1 for record in records if record.label not in (0, 1))
    if bad_labels:
        problems.append(f"{bad_labels} records have a label other than 0 or 1")
    return problems


def summarize(records: Sequence[ManifestRecord]) -> dict[Split, SplitSummary]:
    """Count images, patients and positives per split."""
    summary: dict[Split, SplitSummary] = {}
    for split in SPLITS:
        in_split = [record for record in records if record.split == split]
        summary[split] = SplitSummary(
            images=len(in_split),
            patients=len({record.patient_id for record in in_split}),
            positives=sum(record.label for record in in_split),
        )
    return summary
