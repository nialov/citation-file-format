import argparse
import json
from pathlib import Path
from typing import List
import sys

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
    parser.add_argument("data", type=Path, help="A YAML data file", nargs="+")
    parser.add_argument(
        "-s",
        "--schema",
        type=Path,
        help="A JSON Schema file",
        default=(Path(__file__).parent.parent / "schema.json").as_posix(),
    )
    args = parser.parse_args()
    validate_multiple(args.data, args.schema)


def validate_multiple(data_paths:List[Path], schema_path:Path):
    for data_path in data_paths:

        with data_path.open(mode="r") as fi:
        # with open(data_path, "r") as fi:
            # Convert to Python object
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
                except ( ValidationError, ScannerError ) as err:
                    if isinstance(err, ValidationError):
                        print(f"ERROR: Failed to validate {data_path}\n", file=sys.stderr)
                    else:
                        print(f"ERROR: Failed to load yaml of {data_path}\n", file=sys.stderr)
                    raise

def validate(data_path, schema_path):
    with open(data_path, 'r') as fi:
        # Convert to Python object
        yaml = YAML(typ='safe')
        yaml.constructor.yaml_constructors[u'tag:yaml.org,2002:timestamp'] = yaml.constructor.yaml_constructors[u'tag:yaml.org,2002:str']
        yml_data = yaml.load(fi)

        with open(schema_path, 'r') as sf:
            schema_data = json.loads(sf.read())
            jsonschema.validate(instance=yml_data, schema=schema_data, format_checker=jsonschema.FormatChecker())



if __name__ == "__main__":
    main()
