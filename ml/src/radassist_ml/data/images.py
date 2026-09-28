from pathlib import Path
from typing import Final

import numpy as np
import numpy.typing as npt
import pydicom
from PIL import Image
from pydicom.pixels.processing import apply_modality_lut, apply_voi_lut

DICOM_SUFFIXES: Final = frozenset({".dcm", ".dicom"})
HIGH_BIT_DEPTH_MODES: Final = frozenset({"I", "I;16", "I;16B", "I;16L", "F"})

GrayImage = npt.NDArray[np.uint8]


def load_grayscale(path: Path) -> GrayImage:
    """Load a DICOM or raster image as an 8-bit grayscale array in which 0 is black.

    This is the single entry point for reading images. Preprocessing uses it now and
    inference will use it in Step 5, so training and serving read images identically.
    """
    if path.suffix.lower() in DICOM_SUFFIXES:
        return _load_dicom(path)
    return _load_raster(path)


def letterbox(image: GrayImage, size: int) -> GrayImage:
    """Resize to fit a size x size square without distortion, padding the rest with black."""
    if image.ndim != 2:
        raise ValueError(f"Expected a 2-D grayscale image, got shape {image.shape}")
    if size <= 0:
        raise ValueError(f"size must be positive, got {size}")
    height, width = image.shape
    scale = size / max(height, width)
    new_width = max(1, round(width * scale))
    new_height = max(1, round(height * scale))
    resized = Image.fromarray(image).resize((new_width, new_height), Image.Resampling.BILINEAR)
    canvas = np.zeros((size, size), dtype=np.uint8)
    top = (size - new_height) // 2
    left = (size - new_width) // 2
    canvas[top : top + new_height, left : left + new_width] = np.asarray(resized, dtype=np.uint8)
    return canvas


def _to_uint8(values: npt.NDArray[np.float64]) -> GrayImage:
    """Linearly rescale any numeric range to 0-255."""
    low, high = float(values.min()), float(values.max())
    if high <= low:
        return np.zeros(values.shape, dtype=np.uint8)
    scaled = (values - low) / (high - low)
    return np.asarray(np.round(scaled * 255.0), dtype=np.uint8)


def _load_dicom(path: Path) -> GrayImage:
    dataset = pydicom.dcmread(path)
    raw = dataset.pixel_array
    if raw.ndim != 2:
        raise ValueError(f"{path}: expected one grayscale frame, got shape {raw.shape}")
    # Order matters: the modality LUT (rescale slope/intercept) first, then VOI LUT/windowing.
    values = apply_voi_lut(apply_modality_lut(raw, dataset), dataset)
    image = _to_uint8(np.asarray(values, dtype=np.float64))
    if dataset.get("PhotometricInterpretation") == "MONOCHROME1":
        # MONOCHROME1 stores low values as white; invert so 0 is always black.
        image = np.asarray(255 - image, dtype=np.uint8)
    return image


def _load_raster(path: Path) -> GrayImage:
    with Image.open(path) as picture:
        if picture.mode in HIGH_BIT_DEPTH_MODES:
            return _to_uint8(np.asarray(picture, dtype=np.float64))
        return np.asarray(picture.convert("L"), dtype=np.uint8)
