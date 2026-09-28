from radassist_ml.data.records import ManifestRecord, Split
from radassist_ml.data.validation import summarize, validate_manifest


def make(image_id: str, patient_id: str, split: Split, label: int = 0) -> ManifestRecord:
    return ManifestRecord(
        dataset="test",
        image_id=image_id,
        source_path=image_id,
        patient_id=patient_id,
        study_id=image_id,
        label=label,
        split=split,
        body_part="chest",
    )


VALID = [make("a", "p1", "train", 1), make("b", "p2", "val"), make("c", "p3", "test", 1)]


def test_a_valid_manifest_has_no_problems() -> None:
    assert validate_manifest(VALID) == []


def test_empty_manifest_is_reported() -> None:
    assert validate_manifest([]) == ["manifest is empty"]


def test_patient_leakage_is_detected() -> None:
    problems = validate_manifest([*VALID, make("d", "p1", "test")])

    assert any("more than one split" in problem for problem in problems)


def test_duplicate_image_ids_are_detected() -> None:
    problems = validate_manifest([*VALID, make("a", "p1", "train")])

    assert any("duplicate image_id" in problem for problem in problems)


def test_an_empty_split_is_reported() -> None:
    assert validate_manifest(VALID[:2]) == ["split 'test' is empty"]


def test_invalid_labels_are_reported() -> None:
    problems = validate_manifest([*VALID, make("d", "p4", "train", label=2)])

    assert any("label other than 0 or 1" in problem for problem in problems)


def test_summary_counts_images_patients_and_positives() -> None:
    summary = summarize([*VALID, make("d", "p1", "train")])

    assert summary["train"].images == 2
    assert summary["train"].patients == 1
    assert summary["train"].positives == 1
    assert summary["train"].prevalence == 0.5
    assert summary["val"].prevalence == 0.0
