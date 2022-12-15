import argparse
import json
from pathlib import Path
from typing import List

import jsonschema
from ruamel.yaml import YAML


def main():
    """Run like this from the command line:
    `python3 -m validator.py -d data.yml -s schema.json`
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
    validate(args.data, args.schema)


def validate(data_paths:List[Path], schema_path:Path):
    for data_path in data_paths:

        with data_path.open(mode="r") as fi:
        # with open(data_path, "r") as fi:
            # Convert to Python object
            yaml = YAML(typ="safe")
            yaml.constructor.yaml_constructors[
                "tag:yaml.org,2002:timestamp"
            ] = yaml.constructor.yaml_constructors["tag:yaml.org,2002:str"]
            yml_data = yaml.load(fi)

            # with open(schema_path, "r") as sf:
            with schema_path.open(mode="r") as sf:
                schema_data = json.loads(sf.read())
                jsonschema.validate(
                    instance=yml_data,
                    schema=schema_data,
                    format_checker=jsonschema.FormatChecker(),
                )


if __name__ == "__main__":
    main()
