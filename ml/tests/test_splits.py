import pytest

from radassist_ml.data.splits import assign_split


def test_same_patient_always_gets_the_same_split() -> None:
    first = assign_split("nih:42", 0.1, "salt")

    assert all(assign_split("nih:42", 0.1, "salt") == first for _ in range(10))


def test_val_fraction_is_approximately_respected() -> None:
    splits = [assign_split(f"patient-{number}", 0.2, "salt") for number in range(10_000)]

    share = splits.count("val") / len(splits)

    assert 0.18 < share < 0.22


def test_changing_the_salt_reshuffles_patients() -> None:
    first = [assign_split(f"p{number}", 0.5, "one") for number in range(200)]
    second = [assign_split(f"p{number}", 0.5, "two") for number in range(200)]

    assert first != second


@pytest.mark.parametrize("fraction", [0.0, 1.0, -0.1, 1.5])
def test_invalid_fraction_is_rejected(fraction: float) -> None:
    with pytest.raises(ValueError, match="val_fraction"):
        assign_split("p", fraction, "salt")
