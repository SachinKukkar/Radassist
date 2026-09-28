from pathlib import Path

from click.testing import CliRunner

from radassist_ml.cli import cli

# The fake dataset has only 8 train/val patients, so use a large validation share.
HALF_VAL = ["--val-fraction", "0.5"]


def test_manifest_validate_and_preprocess_end_to_end(tmp_path: Path, nih_raw_dir: Path) -> None:
    runner = CliRunner()
    manifest = tmp_path / "manifests" / "nih.csv"
    out_dir = tmp_path / "processed"

    built = runner.invoke(
        cli, ["manifest", "nih", "--raw-dir", str(nih_raw_dir), "--out", str(manifest), *HALF_VAL]
    )
    checked = runner.invoke(cli, ["validate", "--manifest", str(manifest)])
    processed = runner.invoke(
        cli,
        [
            "preprocess",
            "--manifest",
            str(manifest),
            "--raw-dir",
            str(nih_raw_dir),
            "--out-dir",
            str(out_dir),
            "--size",
            "64",
            "--workers",
            "1",
        ],
    )

    assert built.exit_code == 0, built.output
    assert "Wrote 11 records" in built.output
    assert checked.exit_code == 0, checked.output
    assert processed.exit_code == 0, processed.output
    assert (out_dir / "00000001_000.png").is_file()


def test_manifest_with_an_empty_split_is_rejected(tmp_path: Path, nih_raw_dir: Path) -> None:
    out = tmp_path / "nih.csv"

    # The default 10% validation share of 8 patients happens to select nobody.
    result = CliRunner().invoke(
        cli, ["manifest", "nih", "--raw-dir", str(nih_raw_dir), "--out", str(out)]
    )

    assert result.exit_code == 1
    assert "split 'val' is empty" in result.output
    assert not out.exists()
