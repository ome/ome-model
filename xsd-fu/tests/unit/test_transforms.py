from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

import pytest

from xsd_fu.transforms import (
    TransformCatalogError,
    TransformGraph,
    TransformQuality,
    generate_transform_catalog,
    render_transform_catalog,
    transform_quality,
)


class TestTransformQuality:
    def test_classifies_upgrades_and_historical_downgrades(self) -> None:
        assert transform_quality("2015-01", "2016-06") is TransformQuality.EXCELLENT
        assert transform_quality("2016-06", "2015-01") is TransformQuality.GOOD
        assert transform_quality("2010-06", "2008-09") is TransformQuality.FAIR
        assert transform_quality("2010-06", "2007-06") is TransformQuality.POOR
        assert TransformQuality.EXCELLENT.label == "excellent"


class TestTransformGraph:
    def test_selects_deterministic_shortest_routes(self) -> None:
        graph = TransformGraph.from_filenames(
            [
                "2015-01-to-2016-06.xsl",
                "2015-01-to-2013-06.xsl",
                "2013-06-to-2016-06.xsl",
                "2016-06-to-2015-01.xsl",
                "2013-06-to-2015-01.xsl",
                "README.txt",
            ]
        )

        route = graph.best_route("2015-01", "2016-06")

        assert graph.schemas == ("2016-06", "2015-01", "2013-06")
        assert route.schemas == ("2015-01", "2016-06")
        assert route.filenames == ("2015-01-to-2016-06.xsl",)
        assert route.quality is TransformQuality.EXCELLENT
        assert graph.best_route("2015-01", "2015-01").filenames == ()

    def test_rejects_unknown_and_disconnected_schemas(self) -> None:
        graph = TransformGraph.from_filenames(["2015-01-to-2016-06.xsl", "2013-06-to-2012-06.xsl"])

        with pytest.raises(TransformCatalogError, match="Unknown source schema"):
            graph.best_route("missing", "2016-06")
        with pytest.raises(TransformCatalogError, match="Unknown target schema"):
            graph.best_route("2015-01", "missing")
        with pytest.raises(TransformCatalogError, match="No transform path"):
            graph.best_route("2015-01", "2012-06")

    def test_rejects_missing_empty_and_non_directory_inputs(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing"
        regular_file = tmp_path / "file"
        regular_file.write_text("not a directory", encoding="utf-8")

        with pytest.raises(TransformCatalogError, match="does not exist"):
            TransformGraph.from_directory(missing)
        with pytest.raises(TransformCatalogError, match="not a directory"):
            TransformGraph.from_directory(regular_file)
        with pytest.raises(TransformCatalogError, match="No SOURCE-to-TARGET"):
            TransformGraph.from_directory(tmp_path)


class TestRenderTransformCatalog:
    def test_renders_well_formed_xml_with_escaped_names(self) -> None:
        graph = TransformGraph(
            schemas=("B&2", "A&1"),
            edges={"B&2": ("A&1",), "A&1": ("B&2",)},
        )

        content = render_transform_catalog(graph)
        root = ElementTree.fromstring(content)
        first_source = root.find("./source")
        downgrade = root.find("./source[1]/downgrades/target")

        assert root.tag == "ome-transforms"
        assert root.get("current") == "B&2"
        assert first_source is not None
        assert first_source.get("schema") == "B&2"
        assert first_source.find("./upgrades/target") is None
        assert downgrade is not None
        assert downgrade.get("schema") == "A&1"


class TestGenerateTransformCatalog:
    def test_scans_only_top_level_transform_files(self, tmp_path: Path) -> None:
        (tmp_path / "2015-01-to-2016-06.xsl").touch()
        (tmp_path / "2016-06-to-2015-01.xsl").touch()
        nested = tmp_path / "internal"
        nested.mkdir()
        (nested / "unrelated-to-version.xsl").touch()

        content = generate_transform_catalog(tmp_path)

        assert '<ome-transforms current="2016-06">' in content
        assert "unrelated" not in content
