from dataclasses import dataclass
from typing import Final, Literal

Split = Literal["train", "val", "test"]
SPLITS: Final[tuple[Split, ...]] = ("train", "val", "test")


@dataclass(frozen=True, slots=True)
class ManifestRecord:
    """One image in a dataset manifest. Every dataset is converted to this common schema."""

    dataset: str
    image_id: str
    source_path: str
    patient_id: str
    study_id: str
    label: int
    split: Split
    body_part: str
    view: str = ""


@dataclass(frozen=True, slots=True)
class ManifestBuildResult:
    """Records built from a raw dataset, plus how many listed images were not found on disk."""

    records: list[ManifestRecord]
    missing_images: int


def parse_split(value: str) -> Split:
    """Convert a string read from a file into a Split, rejecting unknown values."""
    for split in SPLITS:
        if value == split:
            return split
    raise ValueError(f"Unknown split {value!r}; expected one of {SPLITS}")
