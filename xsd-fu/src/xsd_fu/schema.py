from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import xmlschema
from xmlschema.names import (
    XSD_ALL,
    XSD_ANNOTATION,
    XSD_APPINFO,
    XSD_ATTRIBUTE,
    XSD_ATTRIBUTE_GROUP,
    XSD_CHOICE,
    XSD_COMPLEX_CONTENT,
    XSD_COMPLEX_TYPE,
    XSD_ELEMENT,
    XSD_EXTENSION,
    XSD_GROUP,
    XSD_LIST,
    XSD_RESTRICTION,
    XSD_SEQUENCE,
    XSD_SIMPLE_CONTENT,
    XSD_SIMPLE_TYPE,
    XSD_UNION,
)

from xsd_fu.errors import ModelProcessingError
from xsd_fu.settings import GenerationSettings

XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
_BUILTIN_TYPES = frozenset(
    {
        "anyURI",
        "boolean",
        "date",
        "dateTime",
        "decimal",
        "double",
        "duration",
        "float",
        "int",
        "integer",
        "long",
        "negativeInteger",
        "nonNegativeInteger",
        "nonPositiveInteger",
        "normalizedString",
        "positiveInteger",
        "short",
        "string",
        "token",
        "unsignedShort",
    }
)


def local_name(name: str | None) -> str | None:
    """Return the local component of a lexical or expanded QName."""
    if name is None:
        return None
    if name.startswith("{"):
        return name.rsplit("}", 1)[-1]
    return name.rsplit(":", 1)[-1]


def _min_occurs(value: str | None) -> int:
    return 1 if value is None else int(value)


def _max_occurs(value: str | None) -> int | None:
    if value is None:
        return 1
    return None if value == "unbounded" else int(value)


def _appinfo(element: Element) -> Element | None:
    annotation = element.find(XSD_ANNOTATION)
    if annotation is None:
        return None
    appinfo = annotation.find(XSD_APPINFO)
    if appinfo is None or len(appinfo) == 0:
        return None
    normalized = ElementTree.fromstring(ElementTree.tostring(appinfo[0]))
    for item in normalized.iter():
        item.tag = local_name(item.tag) or ""
    return normalized


@dataclass(slots=True)
class SimpleType:
    """Normalized top-level XSD simple type."""

    name: str
    values: tuple[str, ...]
    base: str | None
    union_of: tuple[str, ...]
    is_list: bool

    @classmethod
    def from_element(cls, element: Element) -> SimpleType:
        name = element.get("name")
        if name is None:
            raise ModelProcessingError("Top-level simpleType has no name")
        restriction = element.find(XSD_RESTRICTION)
        union = element.find(XSD_UNION)
        return cls(
            name=name,
            values=tuple(
                value
                for item in element.iter(f"{{{XSD_NAMESPACE}}}enumeration")
                if (value := item.get("value")) is not None
            ),
            base=restriction.get("base") if restriction is not None else None,
            union_of=tuple(union.get("memberTypes", "").split()) if union is not None else (),
            is_list=element.find(XSD_LIST) is not None,
        )


@dataclass(slots=True)
class SchemaAttribute:
    """Normalized XSD attribute declaration."""

    name: str
    data_type: str
    use: str
    default: str | None
    values: tuple[str, ...]
    union_of: tuple[str, ...]
    annotations: Element | None
    simple_types: dict[str, SimpleType] = field(repr=False)

    @classmethod
    def from_element(
        cls,
        element: Element,
        simple_types: dict[str, SimpleType],
        xsd_prefix: str,
    ) -> SchemaAttribute:
        name = element.get("name") or local_name(element.get("ref"))
        if name is None:
            raise ModelProcessingError("XSD attribute has neither name nor ref")
        data_type = element.get("type", f"{xsd_prefix}string")
        values: tuple[str, ...] = ()
        union_of: tuple[str, ...] = ()
        inline_type = element.find(XSD_SIMPLE_TYPE)
        if inline_type is not None:
            restriction = inline_type.find(f".//{XSD_RESTRICTION}")
            if restriction is not None and restriction.get("base"):
                data_type = restriction.get("base", data_type)
            values = tuple(
                value
                for item in inline_type.iter(f"{{{XSD_NAMESPACE}}}enumeration")
                if (value := item.get("value")) is not None
            )
            union = inline_type.find(f".//{XSD_UNION}")
            if union is not None:
                union_of = tuple(union.get("memberTypes", "").split())
        if data_type in {
            f"{xsd_prefix}ID",
            f"{xsd_prefix}IDREF",
            f"{xsd_prefix}IDREFS",
        }:
            data_type = f"{xsd_prefix}string"
        return cls(
            name=name,
            data_type=data_type,
            use=element.get("use", "optional"),
            default=element.get("default"),
            values=values,
            union_of=union_of,
            annotations=_appinfo(element),
            simple_types=simple_types,
        )

    def possible_values(self) -> list[str]:
        """Return direct and recursively inherited enumeration values."""
        return [*self.values, *self._inherited_values(self.data_type, set())]

    def _inherited_values(self, type_name: str, seen: set[str]) -> list[str]:
        name = local_name(type_name)
        if name is None or name in seen:
            return []
        seen.add(name)
        simple_type = self.simple_types.get(name)
        if simple_type is None:
            return []
        values = list(simple_type.values)
        for member in simple_type.union_of:
            values.extend(self._inherited_values(member, seen))
        return values

    @property
    def effective_type(self) -> str:
        simple_type = self.simple_types.get(local_name(self.data_type) or "")
        if simple_type is not None and simple_type.base is not None:
            return simple_type.base
        return self.data_type


@dataclass(frozen=True, slots=True)
class ChoiceBounds:
    """Occurrence bounds inherited from an enclosing XSD choice."""

    attributes: dict[str, str]
    min_occurs: int
    max_occurs: int | None

    @classmethod
    def from_element(cls, element: Element) -> ChoiceBounds:
        return cls(
            attributes=dict(element.attrib),
            min_occurs=_min_occurs(element.get("minOccurs")),
            max_occurs=_max_occurs(element.get("maxOccurs")),
        )


@dataclass(slots=True, eq=False)
class SchemaElement:
    """Normalized XSD element or named complex type."""

    name: str
    namespace: str
    attributes: dict[str, str]
    children: list[SchemaElement] = field(default_factory=list)
    attribute_definitions: dict[str, SchemaAttribute] = field(default_factory=dict)
    top_level: bool = False
    explicitly_defined: bool = False
    abstract: bool = False
    default: str | None = None
    min_occurs: int = 1
    max_occurs: int | None = 1
    base: str | None = None
    data_type: str = "NoneType"
    complex: bool = False
    mixed_extension_error: bool = False
    choice: ChoiceBounds | None = None
    values: tuple[str, ...] = ()
    annotations: Element | None = None


@dataclass(slots=True)
class SchemaGraph:
    """Validated, normalized schema graph consumed by the OME model builder."""

    root_elements: list[SchemaElement]
    simple_types: dict[str, SimpleType]
    source_trees: dict[str, Element]
    dependencies: frozenset[Path]


class _GraphBuilder:
    def __init__(self, schemas: list[xmlschema.XMLSchema10], xsd_prefix: str) -> None:
        self.schemas = schemas
        self.xsd_prefix = xsd_prefix
        self.simple_types: dict[str, SimpleType] = {}
        self.elements_by_name: dict[str, SchemaElement] = {}
        self.attribute_groups: dict[str, Element] = {}
        self.model_groups: dict[str, Element] = {}

    def build(self) -> tuple[list[SchemaElement], dict[str, SimpleType]]:
        self._load_globals()
        roots = [
            self._build_element(element, schema.target_namespace, top_level=True)
            for schema in self.schemas
            for element in schema.source.root
            if element.tag in {XSD_ELEMENT, XSD_COMPLEX_TYPE}
        ]
        for root in roots:
            self._collect(root)
        for root in roots:
            self._resolve_tree(root)
        return roots, self.simple_types

    def _load_globals(self) -> None:
        for schema in self.schemas:
            self.attribute_groups.update(
                (name, component.elem) for name, component in schema.attribute_groups.items()
            )
            self.model_groups.update(
                (name, component.elem) for name, component in schema.groups.items()
            )
            for element in schema.source.root:
                if element.tag == XSD_SIMPLE_TYPE and element.get("name"):
                    simple_type = SimpleType.from_element(element)
                    self.simple_types[simple_type.name] = simple_type

    def _build_element(
        self, element: Element, namespace: str, *, top_level: bool = False
    ) -> SchemaElement:
        name = local_name(element.get("name") or element.get("ref") or element.get("type") or "")
        if name is None:
            raise ModelProcessingError("Unable to determine XSD element name")
        attributes = dict(element.attrib)
        attributes["name"] = name
        for key in ("type", "ref"):
            if key in attributes and not attributes[key].startswith(self.xsd_prefix):
                attributes[key] = local_name(attributes[key]) or ""
        node = SchemaElement(
            name=name,
            namespace=namespace,
            attributes=attributes,
            top_level=top_level,
            explicitly_defined="type" not in element.attrib and "ref" not in element.attrib,
            abstract=element.get("abstract", "false").lower() in {"1", "true"},
            default=element.get("default"),
            min_occurs=_min_occurs(element.get("minOccurs")),
            max_occurs=_max_occurs(element.get("maxOccurs")),
            annotations=_appinfo(element),
        )
        self._populate_content(node, element, namespace)
        self._populate_attributes(node, element)
        return node

    def _populate_content(
        self,
        target: SchemaElement,
        container: Element,
        namespace: str,
        choice: ChoiceBounds | None = None,
    ) -> None:
        for child in container:
            if child.tag in {XSD_ANNOTATION, XSD_SIMPLE_TYPE, XSD_ATTRIBUTE}:
                continue
            if child.tag == XSD_ELEMENT:
                node = self._build_element(child, namespace)
                node.choice = choice
                if choice is not None:
                    if "minOccurs" not in child.attrib:
                        node.min_occurs = choice.min_occurs
                    if "maxOccurs" not in child.attrib:
                        node.max_occurs = choice.max_occurs
                target.children.append(node)
            elif child.tag == XSD_CHOICE:
                self._populate_content(target, child, namespace, ChoiceBounds.from_element(child))
            elif child.tag in {
                XSD_SEQUENCE,
                XSD_ALL,
                XSD_COMPLEX_TYPE,
                XSD_COMPLEX_CONTENT,
                XSD_SIMPLE_CONTENT,
            }:
                self._populate_content(target, child, namespace, choice)
            elif child.tag == XSD_EXTENSION:
                base = child.get("base")
                if base and not base.startswith(self.xsd_prefix):
                    target.base = local_name(base)
                self._populate_content(target, child, namespace, choice)
            elif child.tag == XSD_GROUP and child.get("ref"):
                group = self.model_groups.get(local_name(child.get("ref")) or "")
                if group is not None:
                    self._populate_content(target, group, namespace, choice)

    def _populate_attributes(self, target: SchemaElement, container: Element) -> None:
        for child in container:
            if child.tag == XSD_ELEMENT:
                continue
            if child.tag == XSD_ATTRIBUTE:
                attribute = SchemaAttribute.from_element(child, self.simple_types, self.xsd_prefix)
                target.attribute_definitions[attribute.name] = attribute
            elif child.tag == XSD_ATTRIBUTE_GROUP and child.get("ref"):
                group = self.attribute_groups.get(local_name(child.get("ref")) or "")
                if group is not None:
                    self._populate_attributes(target, group)
            elif child.tag not in {XSD_ANNOTATION, XSD_SIMPLE_TYPE}:
                self._populate_attributes(target, child)

    def _collect(self, element: SchemaElement) -> None:
        if element.top_level or element.children or element.attribute_definitions or element.base:
            self.elements_by_name[element.name] = element
        for child in element.children:
            self._collect(child)

    def _is_builtin(self, type_name: str) -> bool:
        return (
            type_name.startswith(self.xsd_prefix)
            and type_name.removeprefix(self.xsd_prefix) in _BUILTIN_TYPES
        )

    @staticmethod
    def _initial_type(element: SchemaElement) -> str:
        return (
            element.attributes.get("type")
            or element.attributes.get("ref")
            or element.attributes.get("name")
            or ""
        )

    def _resolve_type(self, element: SchemaElement) -> str:
        element.complex = bool(element.attribute_definitions)
        type_name = self._initial_type(element)
        if type_name in self.elements_by_name:
            resolved_name = type_name
            iteration = 0
            while True:
                resolved = self.elements_by_name[resolved_name]
                element.values = resolved.values
                next_name = self._initial_type(resolved)
                simple_type = self.simple_types.get(local_name(next_name) or "")
                if simple_type is not None:
                    resolved_name = simple_type.base or next_name
                    break
                if next_name == resolved_name and iteration != 0:
                    break
                if next_name not in self.elements_by_name:
                    resolved_name = next_name
                    break
                resolved_name = next_name
                iteration += 1
            if self._is_builtin(resolved_name):
                type_name = resolved_name
            else:
                element.complex = True
        elif not self._is_builtin(type_name):
            type_name = f"{self.xsd_prefix}string"
        return type_name

    def _resolve_tree(self, element: SchemaElement) -> None:
        element.data_type = self._resolve_type(element)
        element.attributes["type"] = element.data_type
        for child in element.children:
            self._resolve_tree(child)


def load_schema(settings: GenerationSettings) -> SchemaGraph:
    """Validate and normalize configured OME XML Schema sources."""
    schemas: list[xmlschema.XMLSchema10] = []
    source_trees: dict[str, Element] = {}
    try:
        for path in settings.schema_paths:
            resolved = path.resolve()
            schema = xmlschema.XMLSchema10(
                resolved,
                validation="strict",
                use_fallback=False,
            )
            schemas.append(schema)
            root = ElementTree.parse(resolved).getroot()
            if root is None:
                raise ModelProcessingError(f"XML Schema has no document element: {path}")
            source_trees[path.stem] = root
    except (OSError, ElementTree.ParseError, xmlschema.XMLSchemaException) as exc:
        raise ModelProcessingError(f"Unable to parse XML Schema: {exc}") from exc
    if not schemas:
        raise ModelProcessingError("At least one XML Schema path is required")
    roots, simple_types = _GraphBuilder(schemas, settings.java.xsd_prefix).build()
    if not roots:
        raise ModelProcessingError("No model objects found in XML Schema sources")
    dependencies = frozenset(path.resolve() for path in settings.schema_paths)
    return SchemaGraph(roots, simple_types, source_trees, dependencies)
