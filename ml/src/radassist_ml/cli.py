import logging
from pathlib import Path

import click

from radassist_ml.data.manifest import read_manifest, write_manifest
from radassist_ml.data.mura import build_mura_manifest
from radassist_ml.data.nih import build_nih_manifest
from radassist_ml.data.preprocess import preprocess_manifest
from radassist_ml.data.records import ManifestRecord
from radassist_ml.data.validation import summarize, validate_manifest

DEFAULT_SALT = "radassist-split-v1"
BUILDERS = {"nih": build_nih_manifest, "mura": build_mura_manifest}

EXISTING_DIR = click.Path(exists=True, file_okay=False, path_type=Path)
EXISTING_FILE = click.Path(exists=True, dir_okay=False, path_type=Path)
OUTPUT_PATH = click.Path(path_type=Path)


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Show debug logs.")
def cli(verbose: bool) -> None:
    """RadAssist dataset tools: build manifests, validate them and preprocess images."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )


@cli.command()
@click.argument("dataset", type=click.Choice(sorted(BUILDERS)))
@click.option("--raw-dir", type=EXISTING_DIR, required=True, help="Downloaded dataset folder.")
@click.option("--out", type=OUTPUT_PATH, required=True, help="Manifest CSV to write.")
@click.option(
    "--val-fraction",
    type=click.FloatRange(0.01, 0.5),
    default=0.1,
    show_default=True,
    help="Share of training patients held out for validation.",
)
@click.option("--salt", default=DEFAULT_SALT, show_default=True, help="Changing it reshuffles.")
def manifest(dataset: str, raw_dir: Path, out: Path, val_fraction: float, salt: str) -> None:
    """Index a downloaded dataset into a manifest CSV with patient-level splits."""
    result = BUILDERS[dataset](raw_dir, val_fraction=val_fraction, salt=salt)
    _fail_if_invalid(result.records)
    count = write_manifest(result.records, out)
    click.echo(f"Wrote {count} records to {out} ({result.missing_images} images not on disk)")
    _echo_summary(result.records)


@cli.command()
@click.option("--manifest", "manifest_path", type=EXISTING_FILE, required=True)
def validate(manifest_path: Path) -> None:
    """Check a manifest for patient leakage and other problems, then print statistics."""
    records = read_manifest(manifest_path)
    _fail_if_invalid(records)
    click.echo(f"{manifest_path}: OK ({len(records)} records)")
    _echo_summary(records)


@cli.command()
@click.option("--manifest", "manifest_path", type=EXISTING_FILE, required=True)
@click.option("--raw-dir", type=EXISTING_DIR, required=True, help="Downloaded dataset folder.")
@click.option("--out-dir", type=OUTPUT_PATH, required=True, help="Folder for processed PNGs.")
@click.option("--size", type=click.IntRange(64, 2048), default=512, show_default=True)
@click.option("--workers", type=click.IntRange(min=1), default=4, show_default=True)
@click.option("--overwrite", is_flag=True, help="Redo images that already exist.")
def preprocess(
    manifest_path: Path, raw_dir: Path, out_dir: Path, size: int, workers: int, overwrite: bool
) -> None:
    """Convert every image in a manifest to a letterboxed 8-bit grayscale PNG."""
    records = read_manifest(manifest_path)
    result = preprocess_manifest(
        records, raw_dir, out_dir, size=size, workers=workers, overwrite=overwrite
    )
    click.echo(
        f"Processed {result.processed}, skipped {result.skipped} existing, "
        f"failed {len(result.failures)}"
    )
    for failure in result.failures[:20]:
        click.echo(f"FAILED: {failure}", err=True)
    if result.failures:
        raise SystemExit(1)


def _fail_if_invalid(records: list[ManifestRecord]) -> None:
    problems = validate_manifest(records)
    for problem in problems:
        click.echo(f"INVALID: {problem}", err=True)
    if problems:
        raise SystemExit(1)


def _echo_summary(records: list[ManifestRecord]) -> None:
    click.echo(f"{'split':<6} {'images':>8} {'patients':>9} {'positive':>9} {'prevalence':>11}")
    for split, stats in summarize(records).items():
        click.echo(
            f"{split:<6} {stats.images:>8} {stats.patients:>9} {stats.positives:>9} "
            f"{stats.prevalence:>11.1%}"
        )
