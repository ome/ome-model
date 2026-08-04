from __future__ import annotations

from pathlib import Path

from xsd_fu.validation import validate_converter


def test_converter_validation_reports_both_directions(tmp_path: Path) -> None:
    store = tmp_path / "MetadataStore.java"
    retrieve = tmp_path / "MetadataRetrieve.java"
    converter = tmp_path / "MetadataConverter.java"
    store.write_text("void setName(String value); void setRoot(Object root);", encoding="utf-8")
    retrieve.write_text("String getName(); Object getRoot();", encoding="utf-8")
    converter.write_text("void setName(); void getUnexpected();", encoding="utf-8")

    assert validate_converter(store, retrieve, converter) == [
        "getName is present in MetadataRetrieve but missing from MetadataConverter",
        "getUnexpected is present in MetadataConverter but missing from MetadataRetrieve",
    ]


def test_converter_validation_accepts_complete_converter(tmp_path: Path) -> None:
    store = tmp_path / "store.java"
    retrieve = tmp_path / "retrieve.java"
    converter = tmp_path / "converter.java"
    store.write_text("void setValue();", encoding="utf-8")
    retrieve.write_text("Object getValue();", encoding="utf-8")
    converter.write_text("converter.setValue(); converter.getValue();", encoding="utf-8")

    assert validate_converter(store, retrieve, converter) == []
