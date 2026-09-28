from collections.abc import Callable
from pathlib import Path

import numpy as np
import numpy.typing as npt
import pytest
from PIL import Image
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.pixels import set_pixel_data
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

# DICOM SOP Class "Digital X-Ray Image Storage - For Presentation"
DX_IMAGE_STORAGE = "1.2.840.10008.5.1.4.1.1.1.1"

NIH_HEADER = (
    "Image Index,Finding Labels,Follow-up #,Patient ID,Patient Age,Patient Gender,View Position"
)


def _write_png(path: Path, pixels: npt.NDArray[np.generic]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(pixels).save(path)
    return path


def _write_dicom(
    path: Path,
    pixels: npt.NDArray[np.uint16],
    photometric: str = "MONOCHROME2",
    window: tuple[int, int] | None = None,
) -> Path:
    """Write a minimal, valid, uncompressed 12-bit grayscale DICOM file."""
    dataset = Dataset()
    dataset.file_meta = FileMetaDataset()
    dataset.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    dataset.SOPClassUID = DX_IMAGE_STORAGE
    dataset.SOPInstanceUID = generate_uid()
    dataset.file_meta.MediaStorageSOPClassUID = dataset.SOPClassUID
    dataset.file_meta.MediaStorageSOPInstanceUID = dataset.SOPInstanceUID
    set_pixel_data(dataset, pixels, photometric, 12, generate_instance_uid=False)
    if window is not None:
        dataset.WindowCenter, dataset.WindowWidth = window
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset.save_as(path, enforce_file_format=True)
    return path


@pytest.fixture
def write_png() -> Callable[..., Path]:
    """Factory fixture: call write_png(path, pixels) inside a test."""
    return _write_png


@pytest.fixture
def write_dicom() -> Callable[..., Path]:
    """Factory fixture: call write_dicom(path, pixels, photometric=..., window=...)."""
    return _write_dicom


@pytest.fixture
def nih_raw_dir(tmp_path: Path) -> Path:
    """A tiny fake NIH ChestX-ray14 download.

    Patients 1-10 have one image each and patient 5 has a second one. Patients 1 and 2 are in
    the official test list; patients 3, 6 and 9 have an effusion. One listed image is missing.
    """
    raw = tmp_path / "nih"
    images = [f"{patient:08d}_000.png" for patient in range(1, 11)]
    images.append("00000005_001.png")
    rows = [NIH_HEADER]
    for image in images:
        patient = int(image[:8])
        finding = "Effusion|Mass" if patient % 3 == 0 else "No Finding"
        rows.append(f"{image},{finding},0,{patient},50,M,PA")
        _write_png(raw / "images" / image, np.zeros((8, 8), dtype=np.uint8))
    rows.append("00000011_000.png,No Finding,0,11,50,F,AP")  # listed, but not downloaded
    (raw / "Data_Entry_2017_v2020.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (raw / "test_list.txt").write_text("00000001_000.png\n00000002_000.png\n", encoding="utf-8")
    return raw


@pytest.fixture
def mura_raw_dir(tmp_path: Path) -> Path:
    """A tiny fake MURA v1.1 download.

    Train patients 1-6 (odd numbers abnormal, patient 1 has two images) and valid patients
    11185 (normal) and 11186 (abnormal). One listed valid image is missing.
    """
    raw = tmp_path / "mura"
    train = [
        f"MURA-v1.1/train/XR_SHOULDER/patient{patient:05d}/"
        f"study1_{'positive' if patient % 2 else 'negative'}/image1.png"
        for patient in range(1, 7)
    ]
    train.append("MURA-v1.1/train/XR_SHOULDER/patient00001/study1_positive/image2.png")
    valid = [
        "MURA-v1.1/valid/XR_HAND/patient11185/study1_negative/image1.png",
        "MURA-v1.1/valid/XR_WRIST/patient11186/study1_positive/image1.png",
    ]
    for relative in train + valid:
        _write_png(raw / relative, np.zeros((8, 8), dtype=np.uint8))
    not_downloaded = "MURA-v1.1/valid/XR_HAND/patient11187/study1_positive/image1.png"
    root = raw / "MURA-v1.1"
    (root / "train_image_paths.csv").write_text("\n".join(train) + "\n", encoding="utf-8")
    (root / "valid_image_paths.csv").write_text(
        "\n".join([*valid, not_downloaded]) + "\n", encoding="utf-8"
    )
    return raw
