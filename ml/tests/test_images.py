from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from radassist_ml.data.images import letterbox, load_grayscale

DICOM_PIXELS = np.array([[0, 1000], [2000, 4095]], dtype=np.uint16)


def test_letterbox_keeps_aspect_ratio_and_pads_with_black() -> None:
    wide = np.full((50, 100), 200, dtype=np.uint8)

    result = letterbox(wide, 64)

    assert result.shape == (64, 64)
    assert result.dtype == np.uint8
    assert result[0, 32] == 0  # top padding is black
    assert result[32, 32] == 200  # the image itself sits in the middle


def test_letterbox_rejects_colour_images() -> None:
    with pytest.raises(ValueError, match="2-D"):
        letterbox(np.zeros((10, 10, 3), dtype=np.uint8), 32)


def test_letterbox_rejects_non_positive_size() -> None:
    with pytest.raises(ValueError, match="positive"):
        letterbox(np.zeros((10, 10), dtype=np.uint8), 0)


def test_8bit_png_is_loaded_unchanged(tmp_path: Path, write_png: Callable[..., Path]) -> None:
    pixels = np.array([[0, 128], [200, 255]], dtype=np.uint8)

    result = load_grayscale(write_png(tmp_path / "gray.png", pixels))

    np.testing.assert_array_equal(result, pixels)


def test_rgb_png_is_converted_to_grayscale(tmp_path: Path, write_png: Callable[..., Path]) -> None:
    pixels = np.full((4, 4, 3), 100, dtype=np.uint8)

    result = load_grayscale(write_png(tmp_path / "rgb.png", pixels))

    assert result.shape == (4, 4)
    assert result[0, 0] == 100  # equal R, G and B values give the same grey


def test_16bit_png_is_rescaled_to_8bit(tmp_path: Path, write_png: Callable[..., Path]) -> None:
    pixels = np.array([[0, 1000], [2000, 4000]], dtype=np.uint16)

    result = load_grayscale(write_png(tmp_path / "deep.png", pixels))

    assert result.dtype == np.uint8
    assert result.min() == 0
    assert result.max() == 255


def test_flat_16bit_image_becomes_black(tmp_path: Path, write_png: Callable[..., Path]) -> None:
    pixels = np.full((4, 4), 1234, dtype=np.uint16)

    result = load_grayscale(write_png(tmp_path / "flat.png", pixels))

    assert result.max() == 0


def test_monochrome2_dicom_keeps_low_values_dark(
    tmp_path: Path, write_dicom: Callable[..., Path]
) -> None:
    result = load_grayscale(write_dicom(tmp_path / "m2.dcm", DICOM_PIXELS))

    assert result[0, 0] == 0
    assert result[1, 1] == 255


def test_monochrome1_dicom_is_inverted(tmp_path: Path, write_dicom: Callable[..., Path]) -> None:
    path = write_dicom(tmp_path / "m1.dcm", DICOM_PIXELS, photometric="MONOCHROME1")

    result = load_grayscale(path)

    assert result[0, 0] == 255
    assert result[1, 1] == 0


def test_dicom_window_is_applied(tmp_path: Path, write_dicom: Callable[..., Path]) -> None:
    path = write_dicom(tmp_path / "windowed.dcm", DICOM_PIXELS, window=(1000, 200))

    result = load_grayscale(path)

    assert result[0, 0] == 0  # below the window: black
    assert result[1, 0] == 255  # above the window: saturated white
    assert 100 < result[0, 1] < 155  # the window centre lands in the middle
