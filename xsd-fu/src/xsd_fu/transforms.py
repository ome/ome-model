from __future__ import annotations

import re
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from xml.sax.saxutils import quoteattr

from xsd_fu.errors import ModelProcessingError

_TRANSFORM_FILENAME = re.compile(r"^(?P<source>.+)-to-(?P<target>.+)\.xsl$")
_CATALOG_HEADER = """\
<?xml version = "1.0" encoding = "UTF-8"?>
<!--
  #%L
  OME Data Model transforms
  %%
  Copyright (C) 2012 - 2016 Open Microscopy Environment:
    - Massachusetts Institute of Technology
    - National Institutes of Health
    - University of Dundee
    - Board of Regents of the University of Wisconsin-Madison
  %%
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE
  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
  POSSIBILITY OF SUCH DAMAGE.
  #L%
  -->
"""


class TransformCatalogError(ModelProcessingError):
    """Raised when an OME transform catalog cannot be generated."""


class TransformQuality(IntEnum):
    """Quality assigned to a transform or multi-transform route."""

    POOR = 1
    FAIR = 2
    GOOD = 3
    EXCELLENT = 4

    @property
    def label(self) -> str:
        """Return the lowercase label used by ``ome-transforms.xml``."""
        return self.name.lower()


def transform_quality(source: str, target: str) -> TransformQuality:
    """Return the historical quality classification for one transform.

    Parameters
    ----------
    source
        Source schema version.
    target
        Target schema version.

    Returns
    -------
    TransformQuality
        ``EXCELLENT`` for upgrades and the historically assigned quality for
        downgrades, based on the target schema generation.
    """
    if source < target:
        return TransformQuality.EXCELLENT
    if target < "2008":
        return TransformQuality.POOR
    if target < "2010-06":
        return TransformQuality.FAIR
    return TransformQuality.GOOD


@dataclass(frozen=True, slots=True)
class TransformRoute:
    """Best available sequence of transforms between two schema versions."""

    schemas: tuple[str, ...]
    quality: TransformQuality

    @property
    def filenames(self) -> tuple[str, ...]:
        """Return the ordered XSL filenames used by this route."""
        return tuple(
            f"{source}-to-{target}.xsl"
            for source, target in zip(self.schemas, self.schemas[1:], strict=False)
        )


@dataclass(frozen=True, slots=True)
class TransformGraph:
    """Directed graph of the available OME schema transforms."""

    schemas: tuple[str, ...]
    edges: dict[str, tuple[str, ...]]

    @classmethod
    def from_directory(cls, directory: Path) -> TransformGraph:
        """Build a transform graph from top-level XSL files in a directory.

        Parameters
        ----------
        directory
            Directory containing files named ``SOURCE-to-TARGET.xsl``.

        Raises
        ------
        TransformCatalogError
            If the directory does not exist or contains no version transforms.
        """
        if not directory.exists():
            raise TransformCatalogError(f"Transform directory does not exist: {directory}")
        if not directory.is_dir():
            raise TransformCatalogError(f"Transform path is not a directory: {directory}")
        return cls.from_filenames(path.name for path in directory.iterdir() if path.is_file())

    @classmethod
    def from_filenames(cls, filenames: Iterable[str]) -> TransformGraph:
        """Build a transform graph from an iterable of candidate filenames."""
        schemas: set[str] = set()
        mutable_edges: dict[str, set[str]] = {}
        for filename in sorted(filenames):
            match = _TRANSFORM_FILENAME.fullmatch(filename)
            if match is None:
                continue
            source = match.group("source")
            target = match.group("target")
            schemas.update((source, target))
            mutable_edges.setdefault(source, set()).add(target)
        if not schemas:
            raise TransformCatalogError("No SOURCE-to-TARGET.xsl transforms were found")
        return cls(
            schemas=tuple(sorted(schemas, reverse=True)),
            edges={source: tuple(sorted(targets)) for source, targets in mutable_edges.items()},
        )

    def best_route(self, source: str, target: str) -> TransformRoute:
        """Return the highest-quality shortest route between two schemas.

        Raises
        ------
        TransformCatalogError
            If either schema is unknown or no route connects the pair.
        """
        if source not in self.schemas:
            raise TransformCatalogError(f"Unknown source schema: {source}")
        if target not in self.schemas:
            raise TransformCatalogError(f"Unknown target schema: {target}")
        if source == target:
            return TransformRoute((source,), TransformQuality.EXCELLENT)
        for minimum_quality in reversed(TransformQuality):
            schemas = self._shortest_route(source, target, minimum_quality)
            if schemas is not None:
                return TransformRoute(schemas, minimum_quality)
        raise TransformCatalogError(f"No transform path from {source} to {target}")

    def _shortest_route(
        self,
        source: str,
        target: str,
        minimum_quality: TransformQuality,
    ) -> tuple[str, ...] | None:
        pending = deque([source])
        previous: dict[str, str | None] = {source: None}
        while pending:
            current = pending.popleft()
            if current == target:
                path: list[str] = []
                step: str | None = target
                while step is not None:
                    path.append(step)
                    step = previous[step]
                return tuple(reversed(path))
            for next_schema in self.edges.get(current, ()):
                if next_schema in previous:
                    continue
                if transform_quality(current, next_schema) < minimum_quality:
                    continue
                previous[next_schema] = current
                pending.append(next_schema)
        return None


def _append_route(lines: list[str], target: str, route: TransformRoute) -> None:
    lines.append(
        f"\t\t\t<target schema={quoteattr(target)} quality={quoteattr(route.quality.label)}>"
    )
    lines.extend(f"\t\t\t\t<transform file={quoteattr(filename)}/>" for filename in route.filenames)
    lines.append("\t\t\t</target>")


def render_transform_catalog(graph: TransformGraph) -> str:
    """Render a complete ``ome-transforms.xml`` catalog.

    Parameters
    ----------
    graph
        Connected transform graph to render.

    Returns
    -------
    str
        Deterministic UTF-8 XML document content.
    """
    lines = [
        _CATALOG_HEADER.rstrip("\n"),
        "",
        f"<ome-transforms current={quoteattr(graph.schemas[0])}>",
    ]
    for source in graph.schemas:
        lines.append(f"\t<source schema={quoteattr(source)}>")
        lines.append("\t\t<upgrades>")
        for target in graph.schemas:
            if source < target:
                _append_route(lines, target, graph.best_route(source, target))
        lines.append("\t\t</upgrades>")
        lines.append("\t\t<downgrades>")
        for target in graph.schemas:
            if target < source:
                _append_route(lines, target, graph.best_route(source, target))
        lines.append("\t\t</downgrades>")
        lines.append("\t</source>")
    lines.append("</ome-transforms>")
    return "\n".join(lines) + "\n"


def generate_transform_catalog(directory: Path) -> str:
    """Scan a transform directory and render its complete route catalog."""
    return render_transform_catalog(TransformGraph.from_directory(directory))
