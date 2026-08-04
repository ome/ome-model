# xsd-fu

`xsd-fu` validates OME XML Schema documents, normalizes them into a typed model,
and deterministically generates the Java model classes and metadata APIs used by
`ome-xml`.

## Installation

The repository maintains one uv lockfile for Python tooling and Maven code
generation. From the repository root:

```sh
uv sync --locked
uv run --locked xsd-fu --help
```

The wheel includes all Java templates, so the command does not depend on the
checkout layout after installation.

## Generating Java sources

Generate both model and metadata sources:

```sh
uv run --locked xsd-fu generate \
  specification/src/main/resources/released-schema/2016-06/ome.xsd \
  --output-dir target/generated-sources/xsd-fu \
  --target all
```

`--target` accepts `all`, `model`, or `metadata`. The command also supports:

- `--dry-run` to render and validate without writing files;
- `--list-generated` to print generated destinations;
- `--list-dependencies` to print schemas and templates used;
- `--template-dir` to use an alternate template set;
- package override options for each generated Java package.

Writes use temporary files followed by atomic replacement. Conflicting output
paths are rejected before anything is written.

## Validating MetadataConverter

Compare the generated metadata interfaces with a converter implementation:

```sh
uv run --locked xsd-fu validate-converter \
  --store path/to/MetadataStore.java \
  --retrieve path/to/MetadataRetrieve.java \
  --converter path/to/MetadataConverter.java
```

## Compatibility contract

The integration suite verifies SHA-256 hashes for every generated file from the
2012-06, 2013-06, 2015-01, and 2016-06 schemas. The contract is based on commit
`1957bd781d54ea4fde815912f27ee94b950beb2c`.

## Development

Run all quality gates from the repository root:

```sh
uv run --locked ruff check
uv run --locked ruff format --check xsd-fu/src/xsd_fu xsd-fu/tests
uv run --locked ty check
uv run --locked pytest
uv run --locked pytest --cov-report=html
```

Maven invokes the installed command once during `generate-sources` to generate
both source families.
