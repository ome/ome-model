from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xsd_fu.java import SOURCE_TYPE, JavaConfiguration


@dataclass(slots=True)
class GenerationSettings:
    """Validated settings shared by schema loading and Java rendering."""

    schema_paths: tuple[Path, ...]
    output_dir: Path
    java: JavaConfiguration
    source_type: str = SOURCE_TYPE
    dry_run: bool = False
    debug: bool = False
    list_generated: bool = False
    list_dependencies: bool = False
