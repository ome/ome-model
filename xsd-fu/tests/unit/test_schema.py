from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from xml.etree import ElementTree

import pytest

from xsd_fu.errors import ModelProcessingError
from xsd_fu.schema import (
    ChoiceBounds,
    SchemaAttribute,
    SimpleType,
    load_schema,
    local_name,
)
from xsd_fu.settings import GenerationSettings


def test_local_name_handles_qname_forms() -> None:
    assert local_name(None) is None
    assert local_name("xsd:string") == "string"
    assert local_name("{urn:test}Value") == "Value"
    assert local_name("Value") == "Value"


def test_schema_loader_builds_normalized_graph(
    tmp_path: Path,
    settings_factory: Callable[[tuple[Path, ...], Path], GenerationSettings],
) -> None:
    schema = tmp_path / "model.xsd"
    schema.write_text(
        """\
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:t="urn:test"
  targetNamespace="urn:test" elementFormDefault="qualified">
  <xsd:simpleType name="Status">
    <xsd:restriction base="xsd:string">
      <xsd:enumeration value="READY"/>
    </xsd:restriction>
  </xsd:simpleType>
  <xsd:element name="Root">
    <xsd:annotation><xsd:appinfo><xsdfu xmlns=""><plural>Roots</plural></xsdfu></xsd:appinfo></xsd:annotation>
    <xsd:complexType>
      <xsd:sequence>
        <xsd:element name="Child" type="xsd:string" minOccurs="0" maxOccurs="unbounded"/>
      </xsd:sequence>
      <xsd:attribute name="Status" type="t:Status" use="required"/>
    </xsd:complexType>
  </xsd:element>
</xsd:schema>
""",
        encoding="utf-8",
    )

    graph = load_schema(settings_factory((schema,), tmp_path / "output"))

    root = graph.root_elements[0]
    assert root.name == "Root"
    assert root.annotations is not None
    assert root.annotations.findtext("plural") == "Roots"
    assert root.children[0].max_occurs is None
    assert root.attribute_definitions["Status"].possible_values() == ["READY"]
    assert graph.dependencies == frozenset({schema.resolve()})


def test_schema_loader_rejects_invalid_and_empty_inputs(
    tmp_path: Path,
    settings_factory: Callable[[tuple[Path, ...], Path], GenerationSettings],
) -> None:
    invalid = tmp_path / "invalid.xsd"
    invalid.write_text("<not-schema/>", encoding="utf-8")

    with pytest.raises(ModelProcessingError, match="Unable to parse XML Schema"):
        load_schema(settings_factory((invalid,), tmp_path / "output"))
    with pytest.raises(ModelProcessingError, match="At least one XML Schema"):
        load_schema(settings_factory((), tmp_path / "output"))


def test_schema_loader_maps_remote_imports_to_local_files(
    tmp_path: Path,
    settings_factory: Callable[[tuple[Path, ...], Path], GenerationSettings],
) -> None:
    imported = tmp_path / "imported.xsd"
    imported.write_text(
        """\
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  targetNamespace="urn:imported">
  <xsd:complexType name="Imported"><xsd:sequence/></xsd:complexType>
</xsd:schema>
""",
        encoding="utf-8",
    )
    root = tmp_path / "root.xsd"
    root.write_text(
        """\
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:imported="urn:imported" targetNamespace="urn:root">
  <xsd:import namespace="urn:imported"
    schemaLocation="https://schemas.example.test/imported.xsd"/>
  <xsd:element name="Root" type="imported:Imported"/>
</xsd:schema>
""",
        encoding="utf-8",
    )

    graph = load_schema(settings_factory((root,), tmp_path / "output"))

    assert graph.dependencies == frozenset({root.resolve(), imported.resolve()})


def test_schema_loader_rejects_unmapped_remote_imports(
    tmp_path: Path,
    settings_factory: Callable[[tuple[Path, ...], Path], GenerationSettings],
) -> None:
    root = tmp_path / "root.xsd"
    root.write_text(
        """\
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <xsd:import namespace="urn:missing"
    schemaLocation="https://schemas.example.test/missing.xsd"/>
</xsd:schema>
""",
        encoding="utf-8",
    )

    with pytest.raises(ModelProcessingError, match="no checked-in local file"):
        load_schema(settings_factory((root,), tmp_path / "output"))


def test_schema_value_objects_normalize_declarations() -> None:
    status_element = ElementTree.fromstring(
        """\
<xsd:simpleType xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="Status">
  <xsd:restriction base="xsd:string"><xsd:enumeration value="READY"/></xsd:restriction>
</xsd:simpleType>
"""
    )
    status = SimpleType.from_element(status_element)
    attribute_element = ElementTree.fromstring(
        """\
<xsd:attribute xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="State" type="Status"/>
"""
    )
    identifier_element = ElementTree.fromstring(
        """\
<xsd:attribute xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="ID" type="xsd:ID"/>
"""
    )
    choice_element = ElementTree.fromstring(
        """\
<xsd:choice xmlns:xsd="http://www.w3.org/2001/XMLSchema" minOccurs="0" maxOccurs="unbounded"/>
"""
    )

    attribute = SchemaAttribute.from_element(attribute_element, {"Status": status}, "xsd:")
    identifier = SchemaAttribute.from_element(identifier_element, {}, "xsd:")
    choice = ChoiceBounds.from_element(choice_element)

    assert status.values == ("READY",)
    assert status.base == "xsd:string"
    assert attribute.possible_values() == ["READY"]
    assert attribute.effective_type == "xsd:string"
    assert identifier.data_type == "xsd:string"
    assert choice.min_occurs == 0
    assert choice.max_occurs is None


def test_schema_value_objects_reject_missing_names() -> None:
    simple = ElementTree.fromstring(
        '<xsd:simpleType xmlns:xsd="http://www.w3.org/2001/XMLSchema"/>'
    )
    attribute = ElementTree.fromstring(
        '<xsd:attribute xmlns:xsd="http://www.w3.org/2001/XMLSchema"/>'
    )

    with pytest.raises(ModelProcessingError, match="simpleType has no name"):
        SimpleType.from_element(simple)
    with pytest.raises(ModelProcessingError, match="neither name nor ref"):
        SchemaAttribute.from_element(attribute, {}, "xsd:")
