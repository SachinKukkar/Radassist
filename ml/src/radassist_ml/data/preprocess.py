import logging
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from radassist_ml.data.images import letterbox, load_grayscale
from radassist_ml.data.records import ManifestRecord

logger = logging.getLogger(__name__)

PROGRESS_EVERY = 1000


@dataclass(frozen=True, slots=True)
class PreprocessResult:
    processed: int
    skipped: int
    failures: list[str] = field(default_factory=list)


def processed_path(out_dir: Path, record: ManifestRecord) -> Path:
    """Where the preprocessed PNG for a record is stored. It mirrors the record's image_id."""
    return out_dir / Path(record.image_id).with_suffix(".png")


def preprocess_image(source: Path, destination: Path, size: int) -> None:
    """Load, letterbox and save one image as an 8-bit grayscale PNG."""
    image = letterbox(load_grayscale(source), size)
    destination.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(destination)


def preprocess_manifest(
    records: Sequence[ManifestRecord],
    raw_dir: Path,
    out_dir: Path,
    *,
    size: int,
    workers: int = 1,
    overwrite: bool = False,
) -> PreprocessResult:
    """Preprocess every image in a manifest. Existing outputs are skipped unless overwrite=True."""
    tasks = [
        (raw_dir / record.source_path, processed_path(out_dir, record))
        for record in records
        if overwrite or not processed_path(out_dir, record).exists()
    ]
    skipped = len(records) - len(tasks)
    failures: list[str] = []

    if workers <= 1:
        for done, (source, destination) in enumerate(tasks, start=1):
            _run_one(source, destination, size, failures)
            _log_progress(done, len(tasks))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(preprocess_image, src, dst, size): src for src, dst in tasks}
            for done, future in enumerate(as_completed(futures), start=1):
                try:
                    future.result()
                except Exception as exc:  # one bad file must not stop the whole job
                    _record_failure(futures[future], exc, failures)
                _log_progress(done, len(tasks))

    processed = len(tasks) - len(failures)
    return PreprocessResult(processed=processed, skipped=skipped, failures=failures)


def _run_one(source: Path, destination: Path, size: int, failures: list[str]) -> None:
    try:
        preprocess_image(source, destination, size)
    except Exception as exc:  # one bad file must not stop the whole job
        _record_failure(source, exc, failures)


def _record_failure(source: Path, exc: Exception, failures: list[str]) -> None:
    logger.warning("Failed to preprocess %s: %s", source, exc)
    failures.append(f"{source}: {exc}")


def _log_progress(done: int, total: int) -> None:
    if done % PROGRESS_EVERY == 0 or done == total:
        logger.info("Preprocessed %d/%d images", done, total)
