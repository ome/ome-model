from __future__ import annotations

import re
from typing import Final

METADATA_OBJECT_IGNORE: Final = ("External", "MapPairs", "M", "BinData")
METADATA_COUNT_IGNORE: Final[dict[str, tuple[str, ...]]] = {"Annotation": ("AnnotationRef",)}
EXPLICIT_DEFINE_OVERRIDE: Final = ("EmissionFilterRef", "ExcitationFilterRef")

BACK_REFERENCE_OVERRIDE: Final = {
    "Annotation": ("Annotation",),
    "Event": ("Event",),
}
BACK_REFERENCE_LINK_OVERRIDE: Final = {
    "AnnotationRef": ("Annotation",),
    "FolderRef": ("Folder",),
    "Pump": ("Laser",),
}
BACK_REFERENCE_NAME_OVERRIDE: Final = {
    "FilterSet.ExcitationFilter": "filterSetExcitationFilter",
    "FilterSet.EmissionFilter": "filterSetEmissionFilter",
    "LightPath.ExcitationFilter": "lightPathExcitationFilter",
    "LightPath.EmissionFilter": "lightPathEmissionFilter",
    "Folder.Folder": "childFolder",
}
BACK_REFERENCE_CLASS_NAME_OVERRIDE: Final = {
    "FilterSet.ExcitationFilter": "FilterSetExcitationFilterLink",
    "FilterSet.EmissionFilter": "FilterSetEmissionFilterLink",
    "LightPath.ExcitationFilter": "LightPathExcitationFilterLink",
    "LightPath.EmissionFilter": "LightPathEmissionFilterLink",
}

COMPLEX_OVERRIDE: Final = ("Transform",)
ANNOTATION_OVERRIDE: Final = ("AnnotationRef",)

PACKAGE_NAMESPACE_RE: Final = re.compile(r"http://www.openmicroscopy.org/Schemas/(\w+)/\d+-\w+")
REF_REGEX: Final = re.compile(r"Ref$|RefNode$")
BACKREF_REGEX: Final = re.compile(r"_BackReference")
PREFIX_CASE_REGEX: Final = re.compile(
    r"^([A-Z])[a-z0-9]+|([A-Z0-9]+)[A-Z][a-z]+|([A-Z]+)[0-9]*|([a-z]+$)"
)

ENUM_HANDLERS: Final = {
    "AcquisitionMode": (
        (r".*Widefield.*", "WideField"),
        (r"^Laser Scan Confocal$", "LaserScanningConfocalMicroscopy"),
        (r"^Swept Field Confocal$", "SweptFieldConfocal"),
    ),
    "Correction": (
        (r".*Pl.*Apo.*", "PlanApo"),
        (r".*Pl.*Flu.*", "PlanFluor"),
        (r"^\s*Vio.*Corr.*", "VioletCorrected"),
        (r".*S.*Flu.*", "SuperFluor"),
        (r".*Neo.*flu.*", "Neofluar"),
        (r".*Flu.*tar.*", "Fluotar"),
        (r".*Fluo.*", "Fluor"),
        (r".*Flua.*", "Fluar"),
        (r"^\s*Apo.*", "Apo"),
    ),
    "DetectorType": (
        (r".*EM.*CCD.*", "EM-CCD"),
        (r".*CCD.*", "CCD"),
        (r".*CMOS.*", "CMOS"),
    ),
    "Immersion": (
        (r"^\s*Dry\s*", "Air"),
        (r"^\s*OI\s*", "Oil"),
        (r".*Oil.*", "Oil"),
        (r".*Oel.*", "Oil"),
        (r".*Wasser.*", "Water"),
        (r".*Gly.*", "Glycerol"),
        (r"^\s*Wl\s*", "Water"),
        (r"^\s*W\s*", "Water"),
    ),
}
