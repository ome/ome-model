from __future__ import annotations

import re
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genshi.template import NewTextTemplate

from xsd_fu import config
from xsd_fu.errors import ModelProcessingError
from xsd_fu.model import Model, ModelObject, ModelProperty
from xsd_fu.schema import load_schema
from xsd_fu.settings import GenerationSettings


@dataclass(frozen=True, slots=True)
class GeneratedFile:
    """One deterministic output produced by a generation plan."""

    relative_path: Path
    content: str
    dependencies: frozenset[Path]


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Files and inputs used by one generation run."""

    files: tuple[GeneratedFile, ...]
    dependencies: frozenset[Path]


@dataclass(slots=True)
class TemplateContext:
    """Small, explicit collection of helpers exposed to Genshi templates."""

    metadata_object_ignore: tuple[str, ...] = field(
        default_factory=lambda: tuple(config.METADATA_OBJECT_IGNORE)
    )
    metadata_count_ignore: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: dict(config.METADATA_COUNT_IGNORE)
    )
    back_reference_class_name_override: dict[str, str] = field(
        default_factory=lambda: dict(config.BACK_REFERENCE_CLASS_NAME_OVERRIDE)
    )
    complex_override: tuple[str, ...] = config.COMPLEX_OVERRIDE
    annotation_override: tuple[str, ...] = config.ANNOTATION_OVERRIDE

    @staticmethod
    def link_overridden(property_name: str, class_name: str) -> bool:
        """Return whether link methods are suppressed for a back-reference."""
        return class_name in config.BACK_REFERENCE_LINK_OVERRIDE.get(property_name, ())

    @staticmethod
    def back_reference_overridden(property_name: str, class_name: str) -> str | bool:
        """Return a configured back-reference name, or false when absent."""
        name = f"{class_name}.{config.REF_REGEX.sub('', property_name)}"
        return config.BACK_REFERENCE_NAME_OVERRIDE.get(name, False)

    @staticmethod
    def max_occurs_under_parent(model: Model, parent: str, name: str) -> int:
        """Return an element's maximum occurrence count below a parent."""
        parent_object = model.get_object_by_name(parent)
        if parent_object is None:
            return 0
        return next(
            (prop.max_occurs for prop in parent_object.properties.values() if prop.name == name),
            0,
        )

    def resolve_hierarchy(
        self,
        results: dict[str, list[dict[str, str]]],
        model: Model,
        names: dict[str, Any] | None,
        func: Callable[..., dict[str, str]],
        child: str | None = None,
        key: str | None = None,
        level: int = 0,
        min_occurs: int = 2,
        concrete_name: str | None = None,
    ) -> bool:
        """Populate metadata index signatures for every parent path."""
        if names is None:
            return False
        is_multi_path = False
        for name in sorted(names):
            obj = model.get_object_by_name(name)
            if obj is None:
                raise ModelProcessingError(f"Unknown hierarchy object: {name}")
            current_key = key
            if level == 1:
                current_key = name
                if obj.is_abstract_substitution and concrete_name is not None:
                    current_key = concrete_name
                results[current_key] = []
            maximum = self.max_occurs_under_parent(model, name, child or "")
            is_multi_path = is_multi_path or len(names) > 1
            if obj.is_concrete_substitution:
                parent_name = obj.parent_name
                nested = {parent_name: model.resolve_parents(parent_name)}
                child_multi_path = self.resolve_hierarchy(
                    results,
                    model,
                    nested,
                    func,
                    name,
                    current_key,
                    level,
                    min_occurs,
                    name,
                )
            else:
                child_multi_path = self.resolve_hierarchy(
                    results,
                    model,
                    names[name],
                    func,
                    name,
                    current_key,
                    level + 1,
                    min_occurs,
                    concrete_name,
                )
            is_multi_path = is_multi_path or child_multi_path
            if child is not None and maximum >= min_occurs:
                if current_key is None:
                    raise ModelProcessingError(f"Hierarchy for {child} has no top-level key")
                child_object = model.get_object_by_name(child)
                if child_object is None:
                    raise ModelProcessingError(f"Unknown hierarchy child: {child}")
                if child_object.is_abstract_substitution:
                    results[current_key].append(func(child, maximum, level, concrete_name))
                else:
                    results[current_key].append(func(child, maximum, level))
        return is_multi_path


def enum_value_name(value: str, is_units_enum: bool) -> str:
    """Convert an XML enumeration value into its historical Java constant."""
    if re.match(r"^\d+", value):
        for digit, word in enumerate(
            (
                "zero",
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
            )
        ):
            value = value.replace(str(digit), word)
    value = value.replace(" ", "").replace("-", "")
    if is_units_enum:
        replacements = (
            (r"^M", "mega"),
            (r"^G", "giga"),
            (r"^T(?!o)", "tera"),
            (r"^P(?!a)", "peta"),
            (r"^E", "exa"),
            (r"^Z", "zetta"),
            (r"^Y", "yotta"),
        )
        for pattern, replacement in replacements:
            value = re.sub(pattern, replacement, value)
        value = value.replace("µ", "micro").replace("°", "degree").replace("Å", "angstrom")
    return value.upper()


def _render_template(path: Path, **context: object) -> str:
    source = path.read_text(encoding="utf-8")
    template = NewTextTemplate(source, filepath=str(path), encoding="utf-8")
    rendered = template.generate(**context).render(encoding="utf-8")
    return rendered.decode("utf-8")


def _java_path(package: str, filename: str) -> Path:
    return Path(*package.split(".")) / filename


def _custom_class_fragments(
    template_path: Path,
    obj: ModelObject,
    model: Model,
    settings: GenerationSettings,
    template_context: TemplateContext,
) -> tuple[str, dict[str, str], dict[str, str], set[Path]]:
    stem = template_path.stem
    suffix = template_path.suffix
    base_context = {
        "fu": template_context,
        "klass": obj,
        "parents": model.resolve_parents(obj.name),
        "model": model,
        "opts": settings,
        "lang": settings.java,
        "debug": settings.debug,
    }
    dependencies: set[Path] = set()
    class_path = template_path.with_name(f"{stem}_{obj.name}{suffix}")
    custom_content = ""
    if class_path.is_file():
        dependencies.add(class_path.resolve())
        custom_content = _render_template(class_path, **base_context)

    update_content: dict[str, str] = {}
    update_pattern = f"{stem}_{obj.name}_update_*{suffix}"
    for custom_path in sorted(template_path.parent.glob(update_pattern)):
        dependencies.add(custom_path.resolve())
        property_name = custom_path.stem.rsplit("_", 1)[-1]
        update_content[property_name] = _render_template(custom_path, **base_context)

    xml_content: dict[str, str] = {}
    xml_pattern = f"{stem}_{obj.name}_asXMLElement_*{suffix}"
    for custom_path in sorted(template_path.parent.glob(xml_pattern)):
        dependencies.add(custom_path.resolve())
        property_name = custom_path.stem.rsplit("_", 1)[-1]
        xml_content[property_name] = _render_template(custom_path, **base_context)
    return custom_content, update_content, xml_content, dependencies


def _model_files(model: Model, settings: GenerationSettings) -> list[GeneratedFile]:
    java = settings.java
    template_context = TemplateContext(metadata_object_ignore=model.metadata_object_ignore)
    outputs: list[GeneratedFile] = []
    class_template = java.template_path("class")
    class_dependency = class_template.resolve()
    for obj in model.objects.values():
        if obj.name in java.model_type_map:
            continue
        filename = java.generated_filename(obj.name, settings.source_type)
        custom, custom_update, custom_xml, custom_dependencies = _custom_class_fragments(
            class_template, obj, model, settings, template_context
        )
        content = _render_template(
            class_template,
            fu=template_context,
            klass=obj,
            model=model,
            opts=settings,
            lang=java,
            debug=settings.debug,
            custom_content=custom,
            custom_update_property_content=custom_update,
            custom_as_xml_element_property_content=custom_xml,
        )
        outputs.append(
            GeneratedFile(
                _java_path(java.model_package, filename),
                content,
                frozenset({class_dependency, *custom_dependencies}),
            )
        )

    enums: dict[str, ModelProperty] = {}
    for obj in model.objects.values():
        for prop in obj.properties.values():
            if prop.is_enumeration:
                enums.setdefault(prop.lang_type, prop)

    enum_template = java.template_path("enum")
    enum_dependency = enum_template.resolve()
    handler_template = java.template_path("enum_handler")
    handler_dependency = handler_template.resolve()
    for enum_name in sorted(enums):
        prop = enums[enum_name]
        enum_filename = java.generated_filename(enum_name, settings.source_type)
        enum_content = _render_template(
            enum_template,
            fu=template_context,
            klass=prop,
            opts=settings,
            lang=java,
            debug=settings.debug,
            enum_value_name=enum_value_name,
        )
        outputs.append(
            GeneratedFile(
                _java_path(java.enum_package, enum_filename),
                enum_content,
                frozenset({enum_dependency}),
            )
        )
        handler_filename = java.generated_filename(f"{enum_name}EnumHandler", settings.source_type)
        handler_content = _render_template(
            handler_template,
            fu=template_context,
            klass=prop,
            model=model,
            opts=settings,
            lang=java,
            debug=settings.debug,
            enum_value_name=enum_value_name,
            config=config.ENUM_HANDLERS,
        )
        outputs.append(
            GeneratedFile(
                _java_path(java.enum_handler_package, handler_filename),
                handler_content,
                frozenset({handler_dependency}),
            )
        )
    return outputs


def _metadata_context(
    model: Model, settings: GenerationSettings, template_context: TemplateContext
) -> tuple[
    dict[str, dict[str, object] | None],
    dict[str, dict[str, list[dict[str, str]]]],
    dict[str, bool],
]:
    parents: dict[str, dict[str, object] | None] = {}
    indexes: dict[str, dict[str, list[dict[str, str]]]] = {}
    is_multi_path: dict[str, bool] = {}
    for obj in model.objects.values():
        parents[obj.name] = model.resolve_parents(obj.name)
        indexes[obj.name] = {}
        is_multi_path[obj.name] = template_context.resolve_hierarchy(
            indexes[obj.name],
            model,
            {obj.name: parents[obj.name]},
            settings.java.index_signature,
        )
    return parents, indexes, is_multi_path


def _metadata_file(
    template_name: str,
    relative_path: Path,
    model: Model,
    settings: GenerationSettings,
    template_context: TemplateContext,
    parents: dict[str, dict[str, object] | None],
    indexes: dict[str, dict[str, list[dict[str, str]]]],
    is_multi_path: dict[str, bool],
) -> GeneratedFile:
    template_path = settings.java.template_path(template_name)
    common = {
        "fu": template_context,
        "model": model,
        "parents": parents,
        "is_multi_path": is_multi_path,
        "indexes": indexes,
        "opts": settings,
        "lang": settings.java,
        "debug": settings.debug,
    }
    custom_content: dict[str, dict[str, str]] = {}
    dependencies = {template_path.resolve()}
    for custom_path in sorted(template_path.parent.glob(f"{template_path.stem}_*")):
        parts = custom_path.stem.split("_")
        if len(parts) != 3:
            continue
        _, object_name, property_name = parts
        dependencies.add(custom_path.resolve())
        custom_content.setdefault(object_name, {})[property_name] = _render_template(
            custom_path, **common
        )
    content = _render_template(template_path, custom_content=custom_content, **common)
    return GeneratedFile(relative_path, content, frozenset(dependencies))


def _metadata_files(model: Model, settings: GenerationSettings) -> list[GeneratedFile]:
    java = settings.java
    template_context = TemplateContext(metadata_object_ignore=model.metadata_object_ignore)
    parents, indexes, is_multi_path = _metadata_context(model, settings, template_context)
    package = Path(*java.metadata_package.split("."))
    specifications = (
        ("metadata_store", package / "MetadataStore.java"),
        ("metadata_retrieve", package / "MetadataRetrieve.java"),
        ("metadata_aggregate", package / "AggregateMetadata.java"),
        ("filter_metadata", package / "FilterMetadata.java"),
        ("dummy_metadata", package / "DummyMetadata.java"),
        (
            "omexml_metadata",
            _java_path(
                java.metadata_implementation_package,
                java.generated_filename("OMEXMLMetadataImpl", settings.source_type),
            ),
        ),
    )
    return [
        _metadata_file(
            template,
            path,
            model,
            settings,
            template_context,
            parents,
            indexes,
            is_multi_path,
        )
        for template, path in specifications
    ]


def build_plan(settings: GenerationSettings, target: str = "all") -> GenerationResult:
    """Validate schemas and render the selected outputs entirely in memory."""
    if target not in {"all", "model", "metadata"}:
        raise ValueError(f"Unsupported generation target: {target}")
    graph = load_schema(settings)
    model = Model.build(graph, settings)
    files: list[GeneratedFile] = []
    if target in {"all", "model"}:
        files.extend(_model_files(model, settings))
    if target in {"all", "metadata"}:
        files.extend(_metadata_files(model, settings))

    by_path: dict[Path, GeneratedFile] = {}
    for generated in files:
        previous = by_path.get(generated.relative_path)
        if previous is not None and previous.content != generated.content:
            raise ModelProcessingError(f"Conflicting generated output: {generated.relative_path}")
        by_path[generated.relative_path] = generated
    ordered = tuple(by_path[path] for path in sorted(by_path))
    dependencies = frozenset(
        {
            *graph.dependencies,
            *(item for output in ordered for item in output.dependencies),
        }
    )
    return GenerationResult(ordered, dependencies)


def _atomic_write(path: Path, content: str) -> None:
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


def generate(settings: GenerationSettings, target: str = "all") -> GenerationResult:
    """Generate Java sources and return the deterministic generation result."""
    result = build_plan(settings, target)
    if settings.list_generated:
        for generated in result.files:
            print(settings.output_dir / generated.relative_path)
    if settings.list_dependencies:
        for dependency in sorted(result.dependencies):
            print(dependency)
    if not settings.dry_run:
        for generated in result.files:
            _atomic_write(settings.output_dir / generated.relative_path, generated.content)
    return result
