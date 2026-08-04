from __future__ import annotations

from pathlib import Path

import pytest

from xsd_fu.cli import main


def test_validate_converter_command_exit_codes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "store.java"
    retrieve = tmp_path / "retrieve.java"
    converter = tmp_path / "converter.java"
    store.write_text("void setValue();", encoding="utf-8")
    retrieve.write_text("Object getValue();", encoding="utf-8")
    converter.write_text("converter.setValue(); converter.getValue();", encoding="utf-8")

    arguments = [
        "validate-converter",
        "--store",
        str(store),
        "--retrieve",
        str(retrieve),
        "--converter",
        str(converter),
    ]
    assert main(arguments) == 0

    converter.write_text("converter.setValue();", encoding="utf-8")
    assert main(arguments) == 1
    assert "getValue is present" in capsys.readouterr().err


def test_generate_command_supports_dry_run_and_listing(
    repository_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    schema = repository_root / "specification/src/main/resources/released-schema/2012-06/ome.xsd"

    assert (
        main(
            [
                "generate",
                str(schema),
                "--output-dir",
                str(tmp_path),
                "--target",
                "model",
                "--dry-run",
                "--list-generated",
                "--list-dependencies",
                "--model-package",
                "example.model",
                "--enum-package",
                "example.enums",
                "--enum-handler-package",
                "example.handlers",
                "--metadata-package",
                "example.meta",
                "--metadata-implementation-package",
                "example.impl",
                "-v",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert str(tmp_path / "example/model/OME.java") in output
    assert str(schema.resolve()) in output
    assert not any(tmp_path.iterdir())


def test_generate_command_reports_configuration_errors(
    repository_root: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    schema = repository_root / "specification/src/main/resources/released-schema/2016-06/ome.xsd"

    assert (
        main(
            [
                "generate",
                str(schema),
                "--output-dir",
                str(tmp_path / "output"),
                "--template-dir",
                str(tmp_path / "missing"),
                "-vv",
            ]
        )
        == 1
    )
    record = caplog.records[-1]
    assert record.exc_info is not None
    assert "Template directory does not exist" in str(record.exc_info[1])


def test_cli_rejects_non_files(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(["generate", str(tmp_path), "--output-dir", str(tmp_path / "out")])
