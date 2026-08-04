from __future__ import annotations

from pathlib import Path

import pytest

from xsd_fu.errors import ModelProcessingError
from xsd_fu.java import JavaConfiguration
from xsd_fu.model import Model, ModelProperty, PropertyKind
from xsd_fu.schema import load_schema
from xsd_fu.settings import GenerationSettings


@pytest.fixture(scope="module")
def model() -> Model:
    root = Path(__file__).resolve().parents[3]
    settings = GenerationSettings(
        schema_paths=(root / "specification/src/main/resources/released-schema/2016-06/ome.xsd",),
        output_dir=root / "target" / "unused-test-output",
        java=JavaConfiguration(root / "xsd-fu/src/xsd_fu/templates/java"),
    )
    return Model.build(load_schema(settings), settings)


def test_model_object_introspection(model: Model) -> None:
    assert model.get_object_by_name(None) is None
    assert model.resolve_parents("OME") is None
    assert "BinData" not in model.metadata_object_ignore

    for obj in model.objects.values():
        assert obj.lang_type == obj.name
        assert obj.lang_type_ns.endswith(f".{obj.name}")
        assert obj.lang_base_type_ns.startswith("ome.xml.model.")
        assert obj.method_name
        assert obj.argument_name
        assert isinstance(obj.is_annotation, bool)
        assert isinstance(obj.is_annotated, bool)
        assert isinstance(obj.is_named, bool)
        assert isinstance(obj.is_described, bool)
        assert isinstance(obj.is_parent_abstract, bool)
        assert isinstance(obj.parents, dict | type(None))
        assert isinstance(obj.source_dependencies, list)


def test_model_property_introspection(model: Model) -> None:
    enumerations = 0
    for obj in model.objects.values():
        for prop in obj.properties.values():
            assert prop.namespace
            assert isinstance(prop.is_global, bool)
            assert isinstance(prop.is_many_to_many, bool)
            assert isinstance(prop.is_annotation, bool)
            assert isinstance(prop.concrete_classes, list)
            assert isinstance(prop.source_dependencies, set)
            _ = prop.units_default
            _ = prop.default_xsd_value
            if prop.is_enumeration:
                enumerations += 1
                assert prop.default_value in prop.possible_values
                assert isinstance(prop.enum_properties, dict)
                assert isinstance(prop.enum_documentation, dict)
    assert enumerations > 0


def test_invalid_property_operations_are_explicit(model: Model) -> None:
    parent = model.objects["Image"]
    declarationless = ModelProperty(
        model=model,
        parent=parent,
        kind=PropertyKind.ELEMENT,
    )
    back_reference = ModelProperty.back_reference(
        name="Image_BackReference",
        data_type="Image",
        parent=parent,
        model=model,
    )
    attribute = next(prop for prop in parent.properties.values() if prop.is_attribute)

    with pytest.raises(ModelProcessingError, match="no declaration"):
        _ = declarationless.name
    with pytest.raises(ModelProcessingError, match="no complex content"):
        attribute.is_complex()
    assert declarationless.max_occurs == 1
    assert declarationless.min_occurs == 1
    assert back_reference.namespace == parent.namespace
    assert declarationless.possible_values == []
    assert declarationless.default_xsd_value is None
    assert declarationless.enum_properties is None
    assert declarationless.enum_documentation is None
