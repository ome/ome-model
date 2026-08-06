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

Use `--locked` with development and CI commands to use the committed lockfile.
Run `uv lock` when intentionally changing dependencies.

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

Package overrides must be valid dotted Java package names. Every destination is
resolved below `--output-dir` before any files are written, and writes use
temporary files followed by atomic replacement. Conflicting or escaping output
paths are rejected before anything is written.

Schema imports are resolved from checked-in sibling XSDs (or the adjacent
`external` directory), never fetched over the network. `--list-dependencies`
includes these transitive schema imports as well as templates.

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
uv run --locked ruff check --no-fix
uv run --locked ruff format --check
uv run --locked ty check
uv run --locked pytest
uv run --locked pytest --cov-report=html
```

Maven invokes the installed command during `generate-sources` to generate both
source families, then validates them against the hand-written
`MetadataConverter` API.

## Maintaining the transform catalog

`specification` packages `ome-transforms.xml`, a catalog of the best available
XSL route between every pair of supported OME schema versions. Regenerate it
after adding or removing a top-level `SOURCE-to-TARGET.xsl` transform:

```sh
uv run --locked xsd-fu generate-transform-catalog \
  specification/src/main/resources/transforms \
  --output specification/src/main/resources/transforms/ome-transforms.xml
```

CI verifies that the committed catalog is current. Run the same check locally:

```sh
uv run --locked xsd-fu generate-transform-catalog \
  specification/src/main/resources/transforms \
  --output specification/src/main/resources/transforms/ome-transforms.xml \
  --check
```
