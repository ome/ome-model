from __future__ import annotations

import tempfile
from pathlib import Path

from xsd_fu.errors import ModelProcessingError


def resolve_contained_path(directory: Path, relative_path: Path) -> Path:
    """Resolve an output path and require it to remain below its directory.

    Parameters
    ----------
    directory
        Root directory for generated output.
    relative_path
        Output path relative to ``directory``.

    Raises
    ------
    ModelProcessingError
        If ``relative_path`` is absolute or resolves outside ``directory``.
    """
    root = directory.resolve()
    if relative_path.is_absolute():
        raise ModelProcessingError(f"Generated output path must be relative: {relative_path}")
    destination = (root / relative_path).resolve()
    if not destination.is_relative_to(root):
        raise ModelProcessingError(
            f"Generated output path escapes output directory: {relative_path}"
        )
    return destination


def atomic_write_text(path: Path, content: str) -> None:
    """Write UTF-8 text to a path using atomic replacement.

    Parameters
    ----------
    path
        Destination file path.
    content
        Text to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            stream.write(content)
            temporary = Path(stream.name)
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
