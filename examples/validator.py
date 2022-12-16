import argparse
import json
from functools import partial
from pathlib import Path
from typing import List

import jsonschema
from jsonschema.exceptions import ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError


def main():
    """
    Run like this from the command line:

    `python3 -m validator.py -s schema.json CITATION.cff`
    """
    parser = argparse.ArgumentParser(
        description="Validates a YAML file against a JSON Schema"
    )
    # Add positional argument with one or more inputs required
    parser.add_argument("data", type=Path, help="A YAML data file", nargs="+")

    # Add option for passing the JSON schema file as input
    # Defaults to ../schema.json which is included in the repository
    parser.add_argument(
        "-s",
        "--schema",
        type=Path,
        help="A JSON Schema file",
        default=(Path(__file__).parent.parent / "schema.json").as_posix(),
    )

    # Add verbose argument to output full error messages
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--no-verbose", dest="verbose", action="store_false")
    parser.set_defaults(verbose=False)

    # Parse arguments from command-line inputs
    args = parser.parse_args()
    validate_multiple(args.data, args.schema, verbose=args.verbose)


def validate_single(data_path: Path, schema_path: Path, verbose: bool):
    with data_path.open(mode="r") as fi:
        yaml = YAML(typ="safe")
        yaml.constructor.yaml_constructors[
            "tag:yaml.org,2002:timestamp"
        ] = yaml.constructor.yaml_constructors["tag:yaml.org,2002:str"]

        # with open(schema_path, "r") as sf:
        with schema_path.open(mode="r") as sf:
            schema_data = json.loads(sf.read())
            try:
                yml_data = yaml.load(fi)
                jsonschema.validate(
                    instance=yml_data,
                    schema=schema_data,
                    format_checker=jsonschema.FormatChecker(),
                )
            except (ValidationError, ScannerError) as err:
                if isinstance(err, ValidationError):
                    validation_message = f"Failed to validate {data_path}"
                else:
                    validation_message = f"Failed to load yaml of {data_path}"

                # Get lines of the error message (which can be very long from ValidationError)
                error_message_lines = str(err).splitlines()

                if len(error_message_lines) <= 25:
                    # If the message is short, use it as is
                    error_message = str(err)
                    is_short = True
                else:
                    # If it is long and verbose option is not set, make it shorter
                    error_message = "\n".join(error_message_lines[0:25])
                    is_short = False

                # Full message without notice of verbose option
                full_message = "\n".join([validation_message, error_message])
                if not verbose and not is_short:

                    # Add notice that verbose output is possible with flag option
                    verbose_notice = "\n... (Add --verbose flag for full output.)"
                    raise err.__class__(full_message + verbose_notice)
                else:

                    # Raise with the full message
                    raise err.__class__(full_message)


def validate_multiple(data_paths: List[Path], schema_path: Path, verbose: bool):
    """
    Validate multiple cff files using given schema.
    """
    # Pass the static arguments to validate_single to create a partial function
    validate_single_with_schema = partial(
        validate_single, schema_path=schema_path, verbose=verbose
    )

    # Iterate over cff files and validate each
    for data_path in data_paths:
        validate_single_with_schema(data_path=data_path)


def validate(data_path, schema_path):
    with open(data_path, "r") as fi:
        # Convert to Python object
        yaml = YAML(typ="safe")
        yaml.constructor.yaml_constructors[
            "tag:yaml.org,2002:timestamp"
        ] = yaml.constructor.yaml_constructors["tag:yaml.org,2002:str"]
        yml_data = yaml.load(fi)

        with open(schema_path, "r") as sf:
            schema_data = json.loads(sf.read())
            jsonschema.validate(
                instance=yml_data,
                schema=schema_data,
                format_checker=jsonschema.FormatChecker(),
            )


if __name__ == "__main__":
    main()
