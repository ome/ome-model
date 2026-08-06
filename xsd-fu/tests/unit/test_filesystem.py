from __future__ import annotations

from pathlib import Path

import pytest

from xsd_fu.errors import ModelProcessingError
from xsd_fu.filesystem import resolve_contained_path


class TestResolveContainedPath:
    def test_resolves_relative_path_below_output_directory(self, tmp_path: Path) -> None:
        assert (
            resolve_contained_path(tmp_path, Path("ome/xml/Model.java"))
            == (tmp_path / "ome/xml/Model.java").resolve()
        )

    @pytest.mark.parametrize("path", (Path("../escape.java"), Path("/tmp/escape.java")))
    def test_rejects_paths_outside_output_directory(self, tmp_path: Path, path: Path) -> None:
        with pytest.raises(ModelProcessingError, match="output path"):
            resolve_contained_path(tmp_path, path)

    def test_rejects_symlink_that_leaves_output_directory(self, tmp_path: Path) -> None:
        output = tmp_path / "output"
        outside = tmp_path / "outside"
        output.mkdir()
        outside.mkdir()
        (output / "linked").symlink_to(outside, target_is_directory=True)

        with pytest.raises(ModelProcessingError, match="escapes output directory"):
            resolve_contained_path(output, Path("linked/Model.java"))
