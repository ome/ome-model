from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

import pytest

from xsd_fu.render import generate
from xsd_fu.settings import GenerationSettings

SCHEMA_VERSIONS = ("2012-06", "2013-06", "2015-01", "2016-06")


def _manifest(path: Path) -> dict[Path, str]:
    entries: dict[Path, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative_path = line.split(maxsplit=1)
        entries[Path(relative_path)] = digest
    return entries


@pytest.mark.parametrize("version", SCHEMA_VERSIONS)
def test_generated_java_matches_frozen_contract(
    version: str,
    repository_root: Path,
    tmp_path: Path,
    settings_factory: Callable[[tuple[Path, ...], Path], GenerationSettings],
) -> None:
    schema = (
        repository_root
        / "specification"
        / "src"
        / "main"
        / "resources"
        / "released-schema"
        / version
        / "ome.xsd"
    )
    expected = _manifest(
        repository_root / "xsd-fu" / "tests" / "fixtures" / "parity" / f"{version}.sha256"
    )

    result = generate(settings_factory((schema,), tmp_path))

    actual_paths = {item.relative_path for item in result.files}
    assert actual_paths == set(expected)
    for relative_path, digest in expected.items():
        with (tmp_path / relative_path).open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == digest
