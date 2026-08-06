from __future__ import annotations

from pathlib import Path

import pytest

from xsd_fu.errors import ModelProcessingError
from xsd_fu.java import JavaConfiguration, java_package_path


def test_java_configuration_maps_types_and_paths(tmp_path: Path) -> None:
    java = JavaConfiguration(tmp_path)

    assert java.template_path("class") == tmp_path / "OMEXMLModelObject.template"
    assert java.template_name("enum") == "OMEXMLModelEnum.template"
    assert java.generated_filename("Image") == "Image.java"
    assert java.mapped_type("xsd:boolean") == "Boolean"
    assert java.primitive_type("xsd:string") == "String"
    assert java.is_primitive_type("String")
    assert java.is_primitive_base("base64Binary")
    assert java.base_type("base64Binary") == "AbstractOMEModelObject"
    assert java.unit_type("UnitsLength") == "Length"
    assert java.unit_default("UnitsTime") == "UNITS.SECOND"


def test_java_configuration_reports_invalid_names(tmp_path: Path) -> None:
    java = JavaConfiguration(tmp_path)

    with pytest.raises(ModelProcessingError, match="Unknown Java template"):
        java.template_path("missing")
    with pytest.raises(ModelProcessingError, match="Unknown Java template"):
        java.template_name("missing")
    with pytest.raises(ModelProcessingError, match="Invalid Java source type"):
        java.generated_filename("Image", "header")


@pytest.mark.parametrize(
    "package",
    ("", "/tmp/example", "example..model", "example.model-name", "example.class", ".."),
)
def test_java_package_path_rejects_invalid_packages(package: str) -> None:
    with pytest.raises(ModelProcessingError, match="Invalid Java package name"):
        java_package_path(package)


def test_java_package_path_returns_relative_directory() -> None:
    assert java_package_path("org.openmicroscopy.model") == Path("org/openmicroscopy/model")


def test_java_index_helpers(tmp_path: Path) -> None:
    java = JavaConfiguration(tmp_path)
    lower = java.index_signature("image", 99, 2)
    upper = java.index_signature("ROI", 1, 0)

    assert lower == {"type": "image", "argname": "imageIndex", "argtype": "int"}
    assert upper["argname"] == "ROIIndex"
    assert java.index_string(lower) == "int imageIndex"
    assert java.index_string(lower, dummy=True) == "int /* imageIndex */"
    assert java.index_argname(lower) == "imageIndex"
