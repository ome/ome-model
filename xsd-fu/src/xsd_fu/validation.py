from __future__ import annotations

import re
from os import PathLike
from pathlib import Path

_METHOD_PATTERN = re.compile(r"(?<=[\s\.:])([gs]et[a-zA-Z0-9]+)")


def _methods(path: Path) -> set[str]:
    return set(_METHOD_PATTERN.findall(path.read_text(encoding="utf-8")))


def validate_converter(
    store: str | PathLike[str],
    retrieve: str | PathLike[str],
    converter: str | PathLike[str],
) -> list[str]:
    """Return deterministic API inconsistencies among metadata Java sources."""
    store_path = Path(store)
    retrieve_path = Path(retrieve)
    converter_path = Path(converter)
    store_methods = _methods(store_path)
    retrieve_methods = _methods(retrieve_path)
    converter_methods = _methods(converter_path)
    expected = (store_methods | retrieve_methods) - {"getRoot", "setRoot"}

    errors: list[str] = []
    for method in sorted(expected - converter_methods):
        source = "MetadataRetrieve" if method in retrieve_methods else "MetadataStore"
        errors.append(f"{method} is present in {source} but missing from MetadataConverter")
    for method in sorted(converter_methods - expected):
        target = "MetadataStore" if method.startswith("set") else "MetadataRetrieve"
        errors.append(f"{method} is present in MetadataConverter but missing from {target}")
    return errors
