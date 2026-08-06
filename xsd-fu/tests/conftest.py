"""Shared pytest configuration for the test suite."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

import xsd_fu
from xsd_fu.java import JavaConfiguration
from xsd_fu.settings import GenerationSettings


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Apply broad test markers from the test directory layout.

    Tests in ``tests/unit`` are marked as unit tests, tests in
    ``tests/integration`` are marked as integration tests.
    """
    del config

    tests_root = Path(__file__).parent
    unit_root = tests_root / "unit"
    integration_root = tests_root / "integration"

    for item in items:
        item_path = Path(str(item.path))

        if item_path.is_relative_to(unit_root):
            item.add_marker(pytest.mark.unit)
        elif item_path.is_relative_to(integration_root):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def repository_root() -> Path:
    """Return the repository root independent of the test working directory."""
    return Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def template_dir() -> Path:
    """Return the packaged Java template directory."""
    package_file = xsd_fu.__file__
    if package_file is None:
        raise RuntimeError("xsd_fu has no filesystem package location")
    return Path(package_file).parent / "templates" / "java"


@pytest.fixture
def settings_factory(
    template_dir: Path,
) -> Callable[[tuple[Path, ...], Path], GenerationSettings]:
    """Build isolated generation settings for a test."""

    def factory(schema_paths: tuple[Path, ...], output_dir: Path) -> GenerationSettings:
        return GenerationSettings(
            schema_paths=schema_paths,
            output_dir=output_dir,
            java=JavaConfiguration(template_dir),
        )

    return factory
