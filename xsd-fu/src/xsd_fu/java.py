from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from xsd_fu.errors import ModelProcessingError

SOURCE_TYPE = "source"

_JAVA_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_JAVA_KEYWORDS = frozenset(
    {
        "abstract",
        "assert",
        "boolean",
        "break",
        "byte",
        "case",
        "catch",
        "char",
        "class",
        "const",
        "continue",
        "default",
        "do",
        "double",
        "else",
        "enum",
        "extends",
        "final",
        "finally",
        "float",
        "for",
        "goto",
        "if",
        "implements",
        "import",
        "instanceof",
        "int",
        "interface",
        "long",
        "native",
        "new",
        "package",
        "private",
        "protected",
        "public",
        "return",
        "short",
        "static",
        "strictfp",
        "super",
        "switch",
        "synchronized",
        "this",
        "throw",
        "throws",
        "transient",
        "try",
        "void",
        "volatile",
        "while",
    }
)

_TEMPLATES = {
    "enum": "OMEXMLModelEnum.template",
    "enum_handler": "OMEXMLModelEnumHandler.template",
    "class": "OMEXMLModelObject.template",
    "metadata_store": "MetadataStore.template",
    "metadata_retrieve": "MetadataRetrieve.template",
    "metadata_aggregate": "AggregateMetadata.template",
    "omexml_metadata": "OMEXMLMetadataImpl.template",
    "dummy_metadata": "DummyMetadata.template",
    "filter_metadata": "FilterMetadata.template",
}


def java_package_path(package: str) -> Path:
    """Validate a dotted Java package name and return its relative path.

    Raises
    ------
    ModelProcessingError
        If the package is empty or contains a non-identifier or Java keyword.
    """
    parts = package.split(".")
    invalid = next(
        (
            part
            for part in parts
            if _JAVA_IDENTIFIER.fullmatch(part) is None or part in _JAVA_KEYWORDS
        ),
        None,
    )
    if invalid is not None:
        raise ModelProcessingError(f"Invalid Java package name: {package!r}")
    return Path(*parts)


@dataclass(slots=True)
class JavaConfiguration:
    """Java naming, package, template, and XML type mappings."""

    template_dir: Path
    xsd_prefix: str = "xsd:"
    model_package: str = "ome.xml.model"
    enum_package: str = "ome.xml.model.enums"
    enum_handler_package: str = "ome.xml.model.enums.handlers"
    metadata_package: str = "ome.xml.meta"
    metadata_implementation_package: str = "ome.xml.meta"
    package_separator: str = "."
    source_suffix: str = ".java"
    base_class: str = "Object"
    default_model_base_class: str = "AbstractOMEModelObject"
    units_package: str = "ome.units"
    units_implementation: str = "ome"
    units_implementation_imports: str = "import ome.units.quantity.*;\nimport ome.units.*;"
    primitive_type_map: dict[str, str] = field(init=False)
    type_map: dict[str, str] = field(init=False)
    model_type_map: dict[str, None] = field(init=False)
    base_type_map: dict[str, str] = field(init=False)
    abstract_type_map: dict[str, str] = field(default_factory=dict)
    substitution_group_map: dict[str, str] = field(default_factory=dict)
    unit_type_map: dict[str, str] = field(init=False)
    unit_default_map: dict[str, str] = field(init=False)

    def __post_init__(self) -> None:
        prefix = self.xsd_prefix
        self.primitive_type_map = {
            "PositiveInt": "PositiveInteger",
            "NonNegativeInt": "NonNegativeInteger",
            "PositiveLong": "PositiveLong",
            "NonNegativeLong": "NonNegativeLong",
            "PositiveFloat": "PositiveFloat",
            "NonNegativeFloat": "NonNegativeFloat",
            "PercentFraction": "PercentFraction",
            "Color": "Color",
            "Text": "Text",
            f"{prefix}dateTime": "Timestamp",
            f"{prefix}boolean": "Boolean",
            f"{prefix}string": "String",
            f"{prefix}integer": "Integer",
            f"{prefix}int": "Integer",
            f"{prefix}long": "Long",
            f"{prefix}float": "Double",
            f"{prefix}double": "Double",
            f"{prefix}anyURI": "String",
            f"{prefix}hexBinary": "String",
            "base64Binary": "byte[]",
            "Map": "List<MapPair>",
        }
        self.type_map = dict(self.primitive_type_map)
        self.type_map.update(
            {
                "Leader": "Experimenter",
                "Contact": "Experimenter",
                "Pump": "LightSource",
                "MIMEtype": "String",
            }
        )
        self.model_type_map = {"Map": None, "M": None, "K": None, "V": None}
        self.base_type_map = {
            "UniversallyUniqueIdentifier": self.default_model_base_class,
            "base64Binary": self.default_model_base_class,
        }
        self.unit_type_map = {
            "UnitsLength": "Length",
            "UnitsTime": "Time",
            "UnitsPressure": "Pressure",
            "UnitsAngle": "Angle",
            "UnitsTemperature": "Temperature",
            "UnitsElectricPotential": "ElectricPotential",
            "UnitsPower": "Power",
            "UnitsFrequency": "Frequency",
        }
        self.unit_default_map = {
            "UnitsLength": "UNITS.METRE",
            "UnitsTime": "UNITS.SECOND",
            "UnitsPressure": "UNITS.PASCAL",
            "UnitsAngle": "UNITS.RADIAN",
            "UnitsTemperature": "UNITS.KELVIN",
            "UnitsElectricPotential": "UNITS.VOLT",
            "UnitsPower": "UNITS.WATT",
            "UnitsFrequency": "UNITS.HERTZ",
        }

    def validate(self) -> None:
        """Validate all Java package configuration used by generated sources."""
        for package in (
            self.model_package,
            self.enum_package,
            self.enum_handler_package,
            self.metadata_package,
            self.metadata_implementation_package,
            self.units_package,
        ):
            java_package_path(package)

    def template_path(self, template: str) -> Path:
        """Return the configured path for a named built-in template."""
        try:
            filename = _TEMPLATES[template]
        except KeyError as exc:
            raise ModelProcessingError(f"Unknown Java template: {template}") from exc
        return self.template_dir / filename

    def template_name(self, template: str) -> str:
        """Return the filename for a named built-in template."""
        try:
            return _TEMPLATES[template]
        except KeyError as exc:
            raise ModelProcessingError(f"Unknown Java template: {template}") from exc

    def generated_filename(self, name: str, source_type: str = SOURCE_TYPE) -> str:
        """Return a Java source filename for a logical type name."""
        if source_type != SOURCE_TYPE:
            raise ModelProcessingError(
                f"Invalid Java source type: {source_type!r}; expected {SOURCE_TYPE!r}"
            )
        return f"{name}{self.source_suffix}"

    def mapped_type(self, xsd_type: str | None) -> str | None:
        """Return the Java type mapped from an XML Schema type."""
        if xsd_type is None:
            return None
        return self.type_map.get(xsd_type)

    def primitive_type(self, xsd_type: str | None) -> str | None:
        """Return a Java primitive-wrapper mapping, if present."""
        if xsd_type is None:
            return None
        return self.primitive_type_map.get(xsd_type)

    def is_primitive_type(self, java_type: str | None) -> bool:
        """Return whether a Java type is generated as a primitive-like value."""
        return java_type in self.primitive_type_map.values()

    def is_primitive_base(self, xsd_type: str | None) -> bool:
        """Return whether a base type is represented as a value attribute."""
        return xsd_type == "base64Binary"

    def base_type(self, xsd_type: str | None) -> str | None:
        """Return an overridden Java base class, if configured."""
        if xsd_type is None:
            return None
        return self.base_type_map.get(xsd_type)

    def unit_type(self, units_type: str) -> str:
        """Return the Java quantity class for a units enumeration."""
        return self.unit_type_map[units_type]

    def unit_default(self, units_type: str) -> str:
        """Return the default Java units constant for a units enumeration."""
        return self.unit_default_map[units_type]

    def has_substitution_group(self, name: str) -> bool:
        """Return whether a type participates in a substitution mapping."""
        return name in self.substitution_group_map

    def substitution_group(self, name: str) -> str | None:
        """Return the substitution mapping for a type."""
        return self.substitution_group_map.get(name)

    def substitution_types(self) -> list[str]:
        """Return substitution group keys in declaration order."""
        return list(self.substitution_group_map)

    def index_signature(
        self,
        name: str,
        max_occurs: int,
        level: int,
        dummy: bool = False,
    ) -> dict[str, str]:
        """Build the index-template context expected by metadata templates."""
        del max_occurs, level, dummy
        argument = f"{name}Index" if name[:2].isupper() else f"{name[:1].lower()}{name[1:]}Index"
        return {"type": name, "argname": argument, "argtype": "int"}

    @staticmethod
    def index_string(signature: dict[str, str], dummy: bool = False) -> str:
        """Render an index parameter declaration."""
        if dummy:
            return f"{signature['argtype']} /* {signature['argname']} */"
        return f"{signature['argtype']} {signature['argname']}"

    @staticmethod
    def index_argname(signature: dict[str, str], dummy: bool = False) -> str:
        """Return the argument name from an index signature."""
        del dummy
        return signature["argname"]
