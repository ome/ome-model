from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from xsd_fu.errors import ModelProcessingError
from xsd_fu.filesystem import atomic_write_text
from xsd_fu.java import JavaConfiguration
from xsd_fu.render import generate
from xsd_fu.settings import GenerationSettings
from xsd_fu.transforms import generate_transform_catalog
from xsd_fu.validation import validate_converter

logger = logging.getLogger(__name__)


def _existing_file(value: str) -> Path:
    path = Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"file does not exist: {path}")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"path is not a file: {path}")
    return path


def _existing_directory(value: str) -> Path:
    path = Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"directory does not exist: {path}")
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"path is not a directory: {path}")
    return path


def _add_verbosity(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true")
    group.add_argument("-v", "--verbose", action="count", default=0)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xsd-fu",
        description="Generate OME model sources and transform metadata.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser(
        "generate", help="generate Java model and metadata sources"
    )
    generate_parser.add_argument("schemas", nargs="+", type=_existing_file, metavar="SCHEMA")
    generate_parser.add_argument("-o", "--output-dir", type=Path, required=True, metavar="DIR")
    generate_parser.add_argument("--target", choices=("all", "model", "metadata"), default="all")
    generate_parser.add_argument("--dry-run", action="store_true")
    generate_parser.add_argument("--list-generated", action="store_true")
    generate_parser.add_argument("--list-dependencies", action="store_true")
    generate_parser.add_argument("--template-dir", type=Path)
    generate_parser.add_argument("--model-package")
    generate_parser.add_argument("--enum-package")
    generate_parser.add_argument("--enum-handler-package")
    generate_parser.add_argument("--metadata-package")
    generate_parser.add_argument("--metadata-implementation-package")
    _add_verbosity(generate_parser)

    validate_parser = subparsers.add_parser(
        "validate-converter",
        help="compare generated metadata APIs with a MetadataConverter",
    )
    validate_parser.add_argument("--store", type=_existing_file, required=True)
    validate_parser.add_argument("--retrieve", type=_existing_file, required=True)
    validate_parser.add_argument("--converter", type=_existing_file, required=True)
    _add_verbosity(validate_parser)

    catalog_parser = subparsers.add_parser(
        "generate-transform-catalog",
        help="generate ome-transforms.xml from version-to-version XSL files",
    )
    catalog_parser.add_argument("transform_dir", type=_existing_directory, metavar="DIR")
    catalog_parser.add_argument("-o", "--output", type=Path, metavar="FILE")
    catalog_parser.add_argument(
        "--check",
        action="store_true",
        help="verify that --output already contains the generated catalog",
    )
    _add_verbosity(catalog_parser)
    return parser


def _configure_logging(quiet: bool, verbose: int) -> None:
    if quiet:
        level = logging.ERROR
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _run_generate(args: argparse.Namespace) -> int:
    template_dir = args.template_dir
    if template_dir is None:
        template_dir = Path(__file__).parent / "templates" / "java"
    elif not template_dir.is_dir():
        raise ModelProcessingError(
            f"Template directory does not exist or is not a directory: {template_dir}"
        )

    java = JavaConfiguration(template_dir=template_dir)
    overrides = {
        "model_package": args.model_package,
        "enum_package": args.enum_package,
        "enum_handler_package": args.enum_handler_package,
        "metadata_package": args.metadata_package,
        "metadata_implementation_package": args.metadata_implementation_package,
    }
    for name, value in overrides.items():
        if value is not None:
            setattr(java, name, value)

    settings = GenerationSettings(
        schema_paths=tuple(args.schemas),
        output_dir=args.output_dir,
        java=java,
        dry_run=args.dry_run,
        debug=args.verbose >= 2,
        list_generated=args.list_generated,
        list_dependencies=args.list_dependencies,
    )
    generate(settings, args.target)
    return 0


def _run_generate_transform_catalog(args: argparse.Namespace) -> int:
    content = generate_transform_catalog(args.transform_dir)
    if args.check:
        if args.output is None:
            raise ModelProcessingError("--check requires --output")
        if not args.output.exists():
            raise ModelProcessingError(f"Transform catalog does not exist: {args.output}")
        if not args.output.is_file():
            raise ModelProcessingError(f"Transform catalog path is not a file: {args.output}")
        if args.output.read_text(encoding="utf-8") != content:
            raise ModelProcessingError(f"Transform catalog is out of date: {args.output}")
        return 0
    if args.output is None:
        print(content, end="")
    else:
        atomic_write_text(args.output, content)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the xsd-fu command-line interface."""
    parser = _parser()
    args = parser.parse_args(argv)
    _configure_logging(args.quiet, args.verbose)
    try:
        if args.command == "generate":
            return _run_generate(args)
        if args.command == "generate-transform-catalog":
            return _run_generate_transform_catalog(args)
        errors = validate_converter(args.store, args.retrieve, args.converter)
        for error in errors:
            print(error, file=sys.stderr)
        return 1 if errors else 0
    except (ModelProcessingError, OSError, ValueError) as exc:
        if args.verbose >= 2:
            logger.exception("xsd-fu failed")
        else:
            print(f"xsd-fu: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
