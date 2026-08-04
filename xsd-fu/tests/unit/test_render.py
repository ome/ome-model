from __future__ import annotations

from pathlib import Path

import pytest

from xsd_fu.java import JavaConfiguration
from xsd_fu.render import TemplateContext, build_plan, enum_value_name
from xsd_fu.settings import GenerationSettings


@pytest.mark.parametrize(
    ("value", "units", "expected"),
    [
        ("3D", False, "THREED"),
        ("Laser Scan", False, "LASERSCAN"),
        ("MHz", True, "MEGAHZ"),
        ("µm", True, "MICROM"),
        ("°", True, "DEGREE"),
        ("Å", True, "ANGSTROM"),
    ],
)
def test_enum_value_name(value: str, units: bool, expected: str) -> None:
    assert enum_value_name(value, units) == expected


def test_template_override_helpers() -> None:
    context = TemplateContext()

    assert context.link_overridden("FolderRef", "Folder")
    assert not context.link_overridden("FolderRef", "Image")
    assert (
        context.back_reference_overridden("ExcitationFilterRef", "FilterSet")
        == "filterSetExcitationFilter"
    )
    assert not context.back_reference_overridden("Unknown", "Image")


def test_build_plan_rejects_unknown_target(tmp_path: Path) -> None:
    settings = GenerationSettings((), tmp_path, JavaConfiguration(tmp_path))
    with pytest.raises(ValueError, match="Unsupported generation target"):
        build_plan(settings, "unknown")
