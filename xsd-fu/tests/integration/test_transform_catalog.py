from __future__ import annotations

from pathlib import Path

from xsd_fu.transforms import generate_transform_catalog


def test_transform_catalog_matches_committed_specification(repository_root: Path) -> None:
    transform_dir = repository_root / "specification/src/main/resources/transforms"

    actual = generate_transform_catalog(transform_dir)

    assert actual == (transform_dir / "ome-transforms.xml").read_text(encoding="utf-8")
