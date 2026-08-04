from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from xml.etree.ElementTree import Element

from xsd_fu import config
from xsd_fu.errors import ModelProcessingError
from xsd_fu.schema import (
    SchemaAttribute,
    SchemaElement,
    SchemaGraph,
    SimpleType,
)
from xsd_fu.settings import GenerationSettings

logger = logging.getLogger(__name__)


class PropertyKind(Enum):
    """Origin of a model property."""

    ELEMENT = auto()
    ATTRIBUTE = auto()
    BACK_REFERENCE = auto()


def _annotation_flag(root: Element | None, name: str) -> bool:
    return root is not None and root.find(name) is not None


def _annotation_text(root: Element | None, name: str) -> str | None:
    return None if root is None else root.findtext(name)


def _lower_case_prefix(value: str | None, owner: str) -> str:
    if value is None:
        raise ModelProcessingError(f"Cannot lower-case {value!r} on {owner}")
    match = config.PREFIX_CASE_REGEX.match(value)
    if match is None:
        raise ModelProcessingError(f"No case prefix match for {value!r} on {owner}")
    prefix = next(group for group in match.groups() if group)
    return f"{prefix.lower()}{value[len(prefix) :]}"


@dataclass(slots=True)
class ModelProperty:
    """Template-facing Java property derived from an XSD declaration."""

    model: Model
    parent: ModelObject
    kind: PropertyKind
    element: SchemaElement | None = None
    attribute: SchemaAttribute | None = None
    reference_name: str | None = None
    reference_type: str | None = None
    reference_plural: str | None = None
    reference_min_occurs: int = 0
    reference_max_occurs: int = 9_999
    key: str | None = None
    has_base_attribute: bool = False
    is_parent_ordered: bool = False
    is_child_ordered: bool = False
    is_ordered: bool = False
    is_unique: bool = False
    is_immutable: bool = False
    is_injected: bool = False
    many_to_many: bool = False
    global_type: bool = False
    plural: str | None = None
    _reference: bool = False
    _enum_properties: dict[str, dict[str, str]] | None = field(default=None, init=False)
    _enum_documentation: dict[str, str | None] | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        annotations = self._annotations
        self.plural = self.reference_plural or _annotation_text(annotations, "plural")
        self.many_to_many = _annotation_flag(annotations, "manytomany")
        self.is_parent_ordered = _annotation_flag(annotations, "parentordered")
        self.is_child_ordered = _annotation_flag(annotations, "childordered")
        self.is_ordered = _annotation_flag(annotations, "ordered")
        self.is_unique = _annotation_flag(annotations, "unique")
        self.is_immutable = _annotation_flag(annotations, "immutable")
        self.is_injected = _annotation_flag(annotations, "injected")
        self.global_type = _annotation_flag(annotations, "global")

    @classmethod
    def from_element(
        cls, element: SchemaElement, parent: ModelObject, model: Model
    ) -> ModelProperty:
        return cls(model=model, parent=parent, kind=PropertyKind.ELEMENT, element=element)

    @classmethod
    def from_attribute(
        cls, attribute: SchemaAttribute, parent: ModelObject, model: Model
    ) -> ModelProperty:
        return cls(
            model=model,
            parent=parent,
            kind=PropertyKind.ATTRIBUTE,
            attribute=attribute,
        )

    @classmethod
    def back_reference(
        cls,
        *,
        name: str,
        data_type: str,
        parent: ModelObject,
        model: Model,
        plural: str | None = None,
        min_occurs: int = 0,
        max_occurs: int = 9_999,
    ) -> ModelProperty:
        return cls(
            model=model,
            parent=parent,
            kind=PropertyKind.BACK_REFERENCE,
            reference_name=name,
            reference_type=data_type,
            reference_plural=plural,
            reference_min_occurs=min_occurs,
            reference_max_occurs=max_occurs,
        )

    @property
    def _annotations(self) -> Element | None:
        if self.element is not None:
            return self.element.annotations
        if self.attribute is not None:
            return self.attribute.annotations
        return None

    @property
    def is_attribute(self) -> bool:
        return self.kind is PropertyKind.ATTRIBUTE

    @property
    def is_back_reference(self) -> bool:
        return self.kind is PropertyKind.BACK_REFERENCE

    @property
    def is_choice(self) -> bool:
        return self.element is not None and self.element.choice is not None

    @property
    def name(self) -> str:
        if self.reference_name is not None:
            return self.reference_name
        if self.attribute is not None:
            return self.attribute.name
        if self.element is None:
            raise ModelProcessingError("Property has no declaration")
        return self.element.name

    @property
    def data_type(self) -> str:
        if self.reference_type is not None:
            return self.reference_type
        if self.attribute is not None:
            return self.attribute.data_type
        if self.element is None:
            raise ModelProcessingError(f"Property {self.name} has no type")
        return self.element.data_type

    @property
    def max_occurs(self) -> int:
        if self.is_attribute:
            return 1
        if self.is_back_reference:
            return self.reference_max_occurs
        if self.element is None:
            return 1
        choice_max = self.element.choice.max_occurs if self.element.choice else 1
        element_max = self.element.max_occurs
        if choice_max is None or element_max is None:
            return sys.maxsize
        return max(choice_max, element_max)

    @property
    def min_occurs(self) -> int:
        if self.attribute is not None:
            return 0 if self.attribute.use == "optional" else 1
        if self.is_back_reference:
            return self.reference_min_occurs
        if self.element is None:
            return 1
        return self.element.choice.min_occurs if self.element.choice else self.element.min_occurs

    @property
    def namespace(self) -> str:
        if self.is_reference:
            reference = self.model.get_object_by_name(config.REF_REGEX.sub("", self.data_type))
            if reference is not None:
                return reference.namespace
        if self.is_attribute or self.is_back_reference:
            return self.parent.namespace
        if self.element is None:
            return self.parent.namespace
        return self.element.namespace

    @property
    def argument_name(self) -> str:
        return _lower_case_prefix(config.REF_REGEX.sub("", self.name), self.name)

    @property
    def method_name(self) -> str:
        if self.key is not None and self.key in config.BACK_REFERENCE_NAME_OVERRIDE:
            name = config.BACK_REFERENCE_NAME_OVERRIDE[self.key]
            return f"{name[0].upper()}{name[1:]}"
        return config.BACKREF_REGEX.sub("", config.REF_REGEX.sub("", self.name))

    @property
    def is_settings(self) -> bool:
        return self.name.endswith("Settings")

    @property
    def is_global(self) -> bool:
        result = self.global_type
        if self.is_back_reference:
            reference = self.model.get_object_by_name(config.BACKREF_REGEX.sub("", self.data_type))
            if reference is not None and reference.name != self.name:
                return result or reference.is_global
        if self.is_reference:
            reference = self.model.get_object_by_name(config.REF_REGEX.sub("", self.data_type))
            if reference is not None and reference.name != self.name:
                result = result or reference.is_global
        return result

    @property
    def is_many_to_many(self) -> bool:
        if self.is_back_reference:
            referenced = self.model.get_object_by_name(self.data_type)
            if referenced is not None:
                for prop in referenced.properties.values():
                    if prop.data_type == f"{self.parent.name}Ref":
                        return prop.is_many_to_many
        return self.many_to_many

    @property
    def possible_values(self) -> list[str]:
        if self.attribute is not None:
            return self.attribute.possible_values()
        if self.element is not None:
            return list(self.element.values)
        return []

    @property
    def is_enumeration(self) -> bool:
        return bool(self.possible_values)

    def _resolve_simple_type(self, type_name: str | None) -> str | None:
        while type_name is not None:
            simple_type = self.model.simple_types.get(type_name)
            if simple_type is None:
                namespaceless = type_name.split(":")[-1]
                if namespaceless != type_name:
                    type_name = namespaceless
                    continue
                return None
            if simple_type.union_of:
                union = self.model.simple_types.get(simple_type.union_of[0])
                if union is not None:
                    mapped = self.model.settings.java.mapped_type(union.base)
                    if mapped is not None:
                        return mapped
                    type_name = union.base
            mapped = self.model.settings.java.mapped_type(simple_type.base)
            if mapped is not None:
                return mapped
            type_name = simple_type.base
        return None

    @property
    def has_units_companion(self) -> bool:
        return f"{self.name}Unit" in self.parent.properties

    @property
    def units_companion(self) -> ModelProperty | None:
        return self.parent.properties.get(f"{self.name}Unit")

    @property
    def units_type(self) -> str | None:
        companion = self.units_companion
        return companion.lang_type if companion is not None else None

    @property
    def units_default(self) -> str | None:
        companion = self.units_companion
        return companion.default_xsd_value if companion is not None else None

    @property
    def lang_type(self) -> str:
        name = self.units_type if self.has_units_companion else None
        if self.is_enumeration:
            if not self._direct_values:
                name = self.data_type
            elif self.name == "Type":
                name = (
                    f"{self.parent.name}Type"
                    if self.data_type.endswith("string")
                    else self.data_type
                )
            else:
                name = self.name
        else:
            name = self.model.settings.java.mapped_type(self.data_type.replace("OME:", ""))
        if name is not None:
            return name
        if self.is_back_reference or (not self.is_attribute and self.is_complex()):
            return config.REF_REGEX.sub("", self.data_type)
        if not self.is_enumeration:
            resolved = self._resolve_simple_type(self.data_type)
            if resolved is not None:
                return resolved
        raise ModelProcessingError(f"Unable to find {self.name} type for {self.data_type}")

    @property
    def _direct_values(self) -> tuple[str, ...]:
        if self.attribute is not None:
            return self.attribute.values
        if self.element is not None:
            return self.element.values
        return ()

    @property
    def lang_type_ns(self) -> str:
        return self.lang_type

    @property
    def metadata_store_arg_type(self) -> str:
        companion = self.units_companion
        if companion is not None:
            return self.model.settings.java.unit_type(companion.metadata_store_arg_type)
        if self.name == "Transform":
            return "AffineTransform"
        if not self.is_primitive and not self.is_enumeration:
            return "String"
        return self.lang_type

    @property
    def metadata_store_ret_type(self) -> str:
        companion = self.units_companion
        if companion is not None:
            return self.model.settings.java.unit_type(companion.metadata_store_ret_type)
        if self.name == "Transform":
            return "AffineTransform"
        if not self.is_primitive and not self.is_enumeration:
            return "String"
        return self.lang_type

    @property
    def is_annotation(self) -> bool:
        if not self.is_reference:
            return False
        referenced = self.model.get_object_by_name(config.REF_REGEX.sub("", self.data_type))
        return referenced is not None and referenced.is_annotation

    @property
    def is_primitive(self) -> bool:
        return self.model.settings.java.is_primitive_type(self.lang_type)

    @property
    def is_units_enumeration(self) -> bool:
        return self.lang_type.startswith("Units")

    @property
    def is_reference(self) -> bool:
        referenced = self.model.get_object_by_name(self.data_type)
        return referenced.is_reference if referenced is not None else self._reference

    @property
    def concrete_classes(self) -> list[str]:
        if not self.model.settings.java.has_substitution_group(self.name):
            return []
        return [
            obj.name
            for obj in sorted(self.model.objects.values(), key=lambda item: item.name)
            if obj.parent_name == self.name
        ]

    @property
    def default_value(self) -> str:
        values = self.possible_values
        return "OTHER" if "OTHER" in values else values[0]

    @property
    def default_xsd_value(self) -> str | None:
        if self.attribute is not None:
            return self.attribute.default
        return self.element.default if self.element is not None else None

    @property
    def instance_variable_name(self) -> str:
        name = self.argument_name
        if self.is_many_to_many:
            if self.is_back_reference:
                referenced = self.model.get_object_by_name(self.data_type)
                if referenced is not None:
                    name = config.BACK_REFERENCE_NAME_OVERRIDE.get(
                        self.key or "", referenced.instance_variable_name
                    )
            return f"{name}Links"
        if self.max_occurs > 1:
            plural = self.plural
            if plural is None:
                related = self.model.get_object_by_name(self.method_name)
                if related is not None:
                    plural = related.plural
                    return _lower_case_prefix(plural, self.name)
        if self.is_back_reference:
            name = config.BACKREF_REGEX.sub("", name)
        return name

    @property
    def instance_variable_type(self) -> str | None:
        companion = self.units_companion
        if companion is not None:
            companion_type = companion.instance_variable_type
            if companion_type is None:
                return None
            return self.model.settings.java.unit_type(companion_type)
        if (self.is_reference or self.is_back_reference) and self.max_occurs > 1:
            return f"List<{self.lang_type_ns}>"
        if self.is_back_reference or (
            self.max_occurs == 1
            and (
                not self.parent.is_abstract
                or self.is_attribute
                or not self.is_complex()
                or not self.is_choice
            )
        ):
            return self.lang_type_ns
        if self.max_occurs > 1 and not self.parent.is_abstract:
            return f"List<{self.lang_type_ns}>"
        return None

    @property
    def instance_variable_default(self) -> str | None:
        if (self.is_reference or self.is_back_reference) and self.max_occurs > 1:
            return "ReferenceList<>"
        if self.is_back_reference or (
            self.max_occurs == 1
            and (
                not self.parent.is_abstract
                or self.is_attribute
                or not self.is_complex()
                or not self.is_choice
            )
        ):
            return None
        if self.max_occurs > 1 and not self.parent.is_abstract:
            return "ArrayList<>"
        return None

    @property
    def instance_variable_comment(self) -> str:
        if self.is_reference:
            suffix = " (occurs more than once)" if self.max_occurs > 1 else ""
            return f"{self.name} reference{suffix}"
        if self.is_back_reference:
            suffix = " (occurs more than once)" if self.max_occurs > 1 else ""
            return f"{self.name} back reference{suffix}"
        if self.max_occurs == 1 and (
            not self.parent.is_abstract
            or self.is_attribute
            or not self.is_complex()
            or not self.is_choice
        ):
            return f"{self.name} property"
        if self.max_occurs > 1 and not self.parent.is_abstract:
            return f"{self.name} property (occurs more than once)"
        return f"*** WARNING *** Unhandled or skipped property {self.name}"

    def is_complex(self) -> bool:
        """Return whether this element property has a complex content model."""
        if self.is_attribute:
            raise ModelProcessingError("An attribute has no complex content model")
        if self.name == "Description" or self.has_base_attribute:
            return False
        if self.is_back_reference:
            return True
        return self.element is not None and self.element.complex

    @property
    def is_abstract(self) -> bool:
        obj = self.model.get_object_by_name(self.name)
        return obj is not None and obj.is_abstract

    @property
    def is_abstract_substitution(self) -> bool:
        return self.is_abstract

    @property
    def source_dependencies(self) -> set[str]:
        if self.name in self.model.settings.java.model_type_map:
            return set()
        if self.model.settings.java.is_primitive_type(self.lang_type):
            return set()
        package = "ome.xml.model" if self.is_enumeration else "ome.xml.model.enums"
        return {f"{package}.{self.lang_type}"}

    @property
    def enum_properties(self) -> dict[str, dict[str, str]] | None:
        if not self.is_enumeration:
            return None
        if self._enum_properties is None:
            self._enum_properties = {}
            root = self.model.source_trees.get("ome")
            if root is None:
                return self._enum_properties
            enum: Element | None = next(
                (
                    item
                    for item in root.findall("{http://www.w3.org/2001/XMLSchema}simpleType")
                    if item.get("name") == self.lang_type
                ),
                None,
            )
            if enum is None:
                for item in root.findall(".//{http://www.w3.org/2001/XMLSchema}attribute"):
                    if item.get("name") == self.lang_type:
                        enum = item.find("{http://www.w3.org/2001/XMLSchema}simpleType")
                        if enum is not None:
                            break
            if enum is not None:
                for value in enum.findall(".//{http://www.w3.org/2001/XMLSchema}enumeration"):
                    props = value.find(".//xsdfu/enum")
                    if props is None:
                        continue
                    attributes = dict(props.attrib)
                    if "javaenum" in attributes:
                        attributes["enum"] = attributes["javaenum"]
                    symbol = value.get("value")
                    if symbol is not None:
                        self._enum_properties[symbol] = attributes
        return self._enum_properties

    @property
    def enum_documentation(self) -> dict[str, str | None] | None:
        if not self.is_enumeration:
            return None
        if self._enum_documentation is None:
            self._enum_documentation = {}
            root = self.model.source_trees.get("ome")
            if root is None:
                return self._enum_documentation
            for item in root.findall("{http://www.w3.org/2001/XMLSchema}simpleType"):
                if item.get("name") != self.lang_type:
                    continue
                for value in item.findall(".//{http://www.w3.org/2001/XMLSchema}enumeration"):
                    symbol = value.get("value")
                    documentation = value.find(".//{http://www.w3.org/2001/XMLSchema}documentation")
                    if symbol is not None:
                        self._enum_documentation[symbol] = (
                            documentation.text if documentation is not None else None
                        )
        return self._enum_documentation


@dataclass(slots=True)
class ModelObject:
    """Template-facing Java model class derived from an XSD element."""

    model: Model
    element: SchemaElement
    parent_element: SchemaElement | None
    name: str = field(init=False)
    data_type: str = field(init=False)
    base: str | None = field(init=False)
    properties: dict[str, ModelProperty] = field(default_factory=dict)
    is_abstract: bool = field(init=False)
    is_parent_ordered: bool = field(init=False)
    is_child_ordered: bool = field(init=False)
    is_ordered: bool = field(init=False)
    is_unique: bool = field(init=False)
    is_immutable: bool = field(init=False)
    global_type: bool = field(init=False)
    plural: str | None = field(init=False)
    many_to_many: bool = field(init=False, default=False)
    is_abstract_substitution: bool = field(init=False)
    is_concrete_substitution: bool = field(init=False)
    top_level_name: str = field(init=False)
    has_primitive_base: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self.name = self.element.name
        self.data_type = self.element.data_type
        self.base = self.element.base
        annotations = self.element.annotations
        self.is_abstract = _annotation_flag(annotations, "abstract")
        self.is_unique = _annotation_flag(annotations, "unique")
        self.is_immutable = _annotation_flag(annotations, "immutable")
        self.global_type = _annotation_flag(annotations, "global")
        self.is_parent_ordered = _annotation_flag(annotations, "parentordered")
        self.is_child_ordered = _annotation_flag(annotations, "childordered")
        self.is_ordered = _annotation_flag(annotations, "ordered")
        self.plural = _annotation_text(annotations, "plural")
        java = self.model.settings.java
        self.is_abstract_substitution = java.has_substitution_group(self.name)
        self.is_concrete_substitution = java.has_substitution_group(self.base or "")
        self.top_level_name = self.base or self.name if self.is_concrete_substitution else self.name

    def add_attribute(self, attribute: SchemaAttribute) -> None:
        self.properties[attribute.name] = ModelProperty.from_attribute(attribute, self, self.model)

    def add_element(self, element: SchemaElement) -> None:
        self.properties[element.name] = ModelProperty.from_element(element, self, self.model)

    def add_primitive_value(self, base: str) -> None:
        prop = ModelProperty.back_reference(
            name=base.title(),
            data_type=base,
            parent=self,
            model=self.model,
            min_occurs=1,
            max_occurs=1,
        )
        prop.has_base_attribute = True
        prop.kind = PropertyKind.ATTRIBUTE
        self.has_primitive_base = True
        self.properties[prop.name] = prop

    @property
    def namespace(self) -> str:
        return self.element.namespace

    @property
    def argument_name(self) -> str:
        return _lower_case_prefix(config.REF_REGEX.sub("", self.name), self.name)

    @property
    def method_name(self) -> str:
        return config.BACKREF_REGEX.sub("", config.REF_REGEX.sub("", self.name))

    @property
    def is_settings(self) -> bool:
        return self.name.endswith("Settings")

    @property
    def is_global(self) -> bool:
        return self.global_type

    @property
    def is_many_to_many(self) -> bool:
        return self.many_to_many

    @property
    def is_annotation(self) -> bool:
        if self.name == "Annotation":
            return True
        base: ModelObject | None = self
        while base is not None:
            if base.base == "Annotation":
                return True
            base = self.model.get_object_by_name(base.base)
        return False

    @property
    def is_reference(self) -> bool:
        if self.base == "Reference":
            return True
        type_object = self.model.get_object_by_name(self.data_type)
        return (
            type_object is not None and type_object.name != self.name and type_object.is_reference
        )

    @property
    def is_annotated(self) -> bool:
        return any(prop.name == "AnnotationRef" for prop in self.properties.values())

    @property
    def is_named(self) -> bool:
        return any(prop.name == "Name" and not prop.is_unique for prop in self.properties.values())

    @property
    def is_described(self) -> bool:
        return any(prop.name == "Description" for prop in self.properties.values())

    @property
    def model_base_type(self) -> str:
        base = self.element.base
        mapped_base = self.model.settings.java.base_type(base)
        if mapped_base is not None:
            base = mapped_base
        if base is None and self.element.attributes["type"] != self.name:
            base = self.element.attributes["type"]
        return base or self.model.settings.java.default_model_base_class

    @property
    def base_object_properties(self) -> list[ModelProperty]:
        properties: list[ModelProperty] = []
        base_name = self.base
        while (base := self.model.get_object_by_name(base_name)) is not None:
            properties.extend(base.properties.values())
            base_name = base.base
        return properties

    @property
    def lang_type(self) -> str:
        return self.name

    @property
    def lang_type_ns(self) -> str:
        java = self.model.settings.java
        return f"{java.model_package}{java.package_separator}{self.lang_type}"

    @property
    def lang_base_type(self) -> str:
        mapped = self.model.settings.java.mapped_type(self.base)
        if mapped is not None:
            return mapped
        if self.base is not None:
            if self.base in self.model.simple_types:
                probe = ModelProperty.back_reference(
                    name=self.name,
                    data_type=self.base,
                    parent=self,
                    model=self.model,
                )
                resolved = probe._resolve_simple_type(self.base)
                if resolved is not None:
                    return resolved
            parent = self.model.get_object_by_name(self.base)
            if parent is not None:
                return parent.lang_base_type
        return self.model.settings.java.base_class

    @property
    def lang_base_type_ns(self) -> str:
        return f"ome.xml.model.{self.lang_base_type}"

    @property
    def instance_variable_name(self) -> str:
        if self.is_many_to_many:
            return f"{self.argument_name}Links"
        return self.argument_name

    @property
    def instance_variables(self) -> list[list[object]]:
        result: list[list[object]] = []
        if self.lang_base_type != self.model.settings.java.base_class:
            result.append([self.lang_base_type, "value", None, "Element's text data", False])
        result.extend(
            [
                prop.instance_variable_type,
                prop.instance_variable_name,
                prop.instance_variable_default,
                prop.instance_variable_comment,
                prop.is_units_enumeration,
            ]
            for prop in self.properties.values()
            if not prop.is_units_enumeration
        )
        return result

    @property
    def source_dependencies(self) -> list[str]:
        dependencies: set[str] = set()
        for prop in self.properties.values():
            dependencies.update(prop.source_dependencies)
        return sorted(dependencies)

    @property
    def parents(self) -> dict[str, object] | None:
        return self.model.resolve_parents(self.name)

    @property
    def parent(self) -> ModelObject | None:
        parents = self.model.resolve_parents(self.name)
        return None if parents is None else self.model.get_object_by_name(next(iter(parents)))

    @property
    def parent_name(self) -> str:
        if (
            self.parent is not None
            and self.parent.is_abstract
            and self.name not in config.ANNOTATION_OVERRIDE
        ):
            return self.parent.name
        return self.model_base_type

    @property
    def is_parent_abstract(self) -> bool:
        return (
            self.parent is not None
            and self.parent.is_abstract
            and self.name not in config.ANNOTATION_OVERRIDE
        )


@dataclass(slots=True)
class _Reference:
    data_type: str
    property_name: str
    plural: str | None
    max_occurs: int
    min_occurs: int
    is_ordered: bool
    is_child_ordered: bool
    is_parent_ordered: bool
    is_injected: bool


@dataclass(slots=True)
class Model:
    """Complete OME generation model built from a normalized schema graph."""

    settings: GenerationSettings
    simple_types: dict[str, SimpleType]
    source_trees: dict[str, Element]
    objects: dict[str, ModelObject] = field(default_factory=dict)
    parents: dict[str, list[str]] = field(default_factory=dict)
    substitution_elements: dict[str, SchemaElement] = field(default_factory=dict)

    @classmethod
    def build(cls, graph: SchemaGraph, settings: GenerationSettings) -> Model:
        model = cls(settings, graph.simple_types, graph.source_trees)
        model._populate_substitution_groups(graph.root_elements)
        model._process_tree(graph.root_elements)
        model._post_process_references()
        return model

    @property
    def opts(self) -> GenerationSettings:
        return self.settings

    @property
    def metadata_object_ignore(self) -> tuple[str, ...]:
        values = list(config.METADATA_OBJECT_IGNORE)
        if self.settings.java.substitution_types() and "BinData" in values:
            values.remove("BinData")
        return tuple(values)

    def get_object_by_name(self, name: str | None) -> ModelObject | None:
        if name is None:
            return None
        return self.objects.get(name)

    def resolve_parents(self, name: str) -> dict[str, object] | None:
        direct = self.parents.get(name)
        if direct is None:
            return None
        return {parent: self.resolve_parents(parent) for parent in direct}

    def _populate_substitution_groups(self, elements: list[SchemaElement]) -> None:
        java = self.settings.java
        for element in elements:
            substitution = element.attributes.get("substitutionGroup")
            if substitution is not None and element.base is not None:
                java.abstract_type_map[substitution] = element.base
                java.substitution_group_map[element.base] = substitution
        for element in elements:
            substitution = java.substitution_group(element.name)
            if substitution is not None:
                self.substitution_elements[substitution] = element

    def _process_tree(
        self,
        elements: list[SchemaElement],
        parent: SchemaElement | None = None,
    ) -> None:
        for source_element in elements:
            if self.settings.java.has_substitution_group(source_element.name):
                continue
            element = source_element
            if element.name in self.substitution_elements:
                if parent is None:
                    continue
                element = self.substitution_elements[element.name]
            self._process_leaf(element, parent)
            if element.children:
                self._process_tree(element.children, element)

    def _process_leaf(self, element: SchemaElement, parent: SchemaElement | None) -> None:
        if parent is not None:
            self.parents.setdefault(element.name, []).append(parent.name)
        if (
            not element.explicitly_defined
            and element.name not in config.EXPLICIT_DEFINE_OVERRIDE
            and not element.top_level
        ):
            return
        if element.mixed_extension_error:
            logger.warning("Skipping mixed extension element %s", element.name)
            return
        if (
            element.data_type != element.name
            and element.name not in config.EXPLICIT_DEFINE_OVERRIDE
        ):
            return
        if element.name in self.objects:
            if element.name not in {"EmissionFilterRef", "ExcitationFilterRef"}:
                logger.warning("Skipping duplicate model object %s", element.name)
            return
        obj = ModelObject(self, element, parent)
        if self.settings.java.is_primitive_base(obj.base):
            if obj.base is None:
                raise ModelProcessingError(f"Primitive object {obj.name} has no base")
            obj.add_primitive_value(obj.base)
            obj.base = self.settings.java.default_model_base_class
        self.objects[element.name] = obj
        for attribute in element.attribute_definitions.values():
            obj.add_attribute(attribute)
        for child in element.children:
            obj.add_element(child)

    def _post_process_references(self) -> None:
        references: dict[str, list[_Reference]] = {}
        for obj in self.objects.values():
            if obj.is_settings and not obj.is_abstract:
                name = f"{obj.name.removesuffix('Settings')}Ref"
                obj.properties[name] = ModelProperty.back_reference(
                    name=name,
                    data_type=name,
                    parent=obj,
                    model=self,
                    min_occurs=1,
                    max_occurs=1,
                )
        for obj in self.objects.values():
            for prop in obj.properties.values():
                abstract_name = self.settings.java.abstract_type_map.get(prop.name)
                if abstract_name is not None:
                    prop.reference_name = abstract_name
                    prop.reference_type = abstract_name
                if not prop.is_reference and (
                    prop.is_attribute
                    or prop.max_occurs == 1
                    or obj.name == "OME"
                    or obj.is_abstract
                ):
                    continue
                short_name = config.REF_REGEX.sub("", prop.data_type)
                if obj.name in config.BACK_REFERENCE_OVERRIDE.get(short_name, ()):
                    continue
                references.setdefault(short_name, []).append(
                    _Reference(
                        data_type=obj.name,
                        property_name=prop.method_name,
                        plural=prop.plural,
                        max_occurs=9_999 if prop.is_reference else 1,
                        min_occurs=0 if prop.is_reference or prop.is_settings else 1,
                        is_ordered=prop.is_ordered,
                        is_child_ordered=prop.is_child_ordered,
                        is_parent_ordered=prop.is_parent_ordered,
                        is_injected=prop.is_injected,
                    )
                )
        for obj in self.objects.values():
            for reference in references.get(obj.name, ()):
                key = f"{reference.data_type}.{reference.property_name}"
                prop = ModelProperty.back_reference(
                    name=f"{reference.data_type}_BackReference",
                    data_type=reference.data_type,
                    parent=obj,
                    model=self,
                    plural=reference.plural,
                    min_occurs=reference.min_occurs,
                    max_occurs=reference.max_occurs,
                )
                prop.key = key
                prop.is_child_ordered = reference.is_child_ordered
                prop.is_parent_ordered = reference.is_parent_ordered
                prop.is_ordered = reference.is_ordered
                prop.is_injected = reference.is_injected
                obj.properties[key] = prop
