#!python3

import argparse
import json
import shutil
from pathlib import Path

import openml
from tqdm import tqdm

import openml_croissant


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate croissants.")
    parser.add_argument(
        "--id",
        type=int,
        nargs="*",
        help="Openml dataset identifier for which to generate a Croissant. If "
        "omitted, a croissant is generated for every identifier.",
    )
    parser.add_argument(
        "-o",
        "--output-directory",
        type=str,
        required=True,
        help="A path to the directory where the results should be written to.",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action=argparse.BooleanOptionalAction,
        help="Remove all existing results beforehand. If omitted, the results will be "
        "overwritten.",
    )
    return parser.parse_args()


def _all_dataset_identifiers() -> list[int]:
    df = openml.datasets.list_datasets(output_format="dataframe")
    return list(df["did"])


def main():
    args = _parse_args()
    path_output_dir = Path(args.output_directory)
    if args.clean and path_output_dir.exists():
        shutil.rmtree(path_output_dir)
    path_output_dir.mkdir(parents=True, exist_ok=True)
    identifiers = args.id if args.id else _all_dataset_identifiers()
    path_exception_file = path_output_dir / "exceptions.csv"
    path_croissants = path_output_dir / "croissant"
    path_croissants.mkdir(exist_ok=True)
    if not path_exception_file.exists():
        with path_exception_file.open("w") as f:
            f.write("identifier,error_type,error\n")
    for identifier in tqdm(identifiers):
        try:
            metadata_openml = openml.datasets.get_dataset(
                identifier,
                download_data=False,
                download_qualities=False,
                download_features_meta_data=True,
            )
            metadata_croissant = openml_croissant.convert(metadata_openml)
            with (path_croissants / f"{identifier}.json").open("w") as f:
                json.dump(
                    metadata_croissant,
                    f,
                    indent=4,
                    default=openml_croissant.serialize_croissant,
                )
        except Exception as e:
            with path_exception_file.open("a") as f:
                msg = str(e).replace("\n", ";")
                f.write(f"{identifier},{type(e).__name__},{msg}\n")


if __name__ == "__main__":
    main()
