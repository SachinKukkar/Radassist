import hashlib
from typing import Literal

TrainOrVal = Literal["train", "val"]


def assign_split(patient_id: str, val_fraction: float, salt: str) -> TrainOrVal:
    """Deterministically assign a patient to "train" or "val".

    The decision depends only on a SHA-256 hash of (salt, patient_id), so the same patient
    lands in the same split on every machine, every run and every Python version.
    """
    if not 0.0 < val_fraction < 1.0:
        raise ValueError(f"val_fraction must be between 0 and 1, got {val_fraction}")
    digest = hashlib.sha256(f"{salt}:{patient_id}".encode()).digest()
    position = int.from_bytes(digest[:8], "big") / 2**64  # uniform in [0, 1)
    return "val" if position < val_fraction else "train"
