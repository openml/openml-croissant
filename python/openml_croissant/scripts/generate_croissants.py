#!python3
"""
Script to generate (all) croissant files. Can be used as integration test.
"""


import argparse
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Iterator

import mlcroissant as mlc
import openml
from minio import Minio, S3Error
from tqdm import tqdm

import openml_croissant
from openml_croissant._src.hashing import ParquetHasher
from openml_croissant._src.logger import setup_logger
from openml_croissant.scripts.upload_datasets_to_minio import (
    DATASET_BUCKET,
    format_croissant_object_name,
    minio_client,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate croissants.")
    data_id_group = parser.add_mutually_exclusive_group(required=True)
    data_id_group.add_argument(
        "--id",
        type=int,
        nargs="*",
        help="Openml dataset identifier for which to generate a Croissant.",
    )
    data_id_group.add_argument(
        "--all",
        action="store_true",
        help="Create a Croissant for every identifier.",
    )
    data_id_group.add_argument(
        "--latest",
        action="store_true",
        help="If set, determine the last dataset which already has a Croissant file "
        "associated with it, and resume from there.",
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
    parser.add_argument(
        "--max_categories_per_enumeration",
        type=int,
        help="if a categorical variable has more categories than this, the categories will not be "
        "described in a Croissant RecordSet.",
        default=openml_croissant.Settings().max_categories_per_enumeration,
    )
    parser.add_argument(
        "--max_features",
        type=int,
        help="if an OpenML Dataset has more features than this, the features will not be "
        "described in the Croissant.",
        default=openml_croissant.Settings().max_features,
    )
    return parser.parse_args()


def _all_dataset_identifiers() -> list[int]:
    df = openml.datasets.list_datasets(output_format="dataframe")
    return list(df["did"])


def _dataset_has_croissant(dataset_id: int, client: Minio) -> bool:
    croissant_object = format_croissant_object_name(dataset_id)
    try:
        client.stat_object(DATASET_BUCKET, croissant_object)
    except S3Error as e:
        if e.code == "NoSuchKey":
            return False
        raise
    return True


def _new_identifiers(minio: Minio) -> Iterator[int]:
    minio.list_objects()

    offset = int(os.environ.get("OPENML_DATASET_OFFSET", 5380))
    df = openml.datasets.list_datasets(
        # The number of known datasets at the moment, to speed this up.
        offset=offset,
        output_format="dataframe",
    )
    for identifier in df["did"].sort_values(ascending=False):
        if _dataset_has_croissant(identifier, minio):
            return
        yield identifier
    if offset > 0:
        msg = "No existing croissant file found. Fix the offset in the script."
        raise RuntimeError(msg)


def main():
    args = _parse_args()
    setup_logger()
    path_output_dir = Path(args.output_directory)
    if args.clean and path_output_dir.exists():
        shutil.rmtree(path_output_dir)
    path_output_dir.mkdir(parents=True, exist_ok=True)

    if server := os.environ.get("OPENML_SERVER"):
        openml.config.server = server

    minio = minio_client()
    if args.id:
        identifiers = args.id
    elif args.all:
        identifiers = _all_dataset_identifiers()
    else:
        identifiers = sorted(_new_identifiers(minio))

    settings = openml_croissant.Settings(
        max_categories_per_enumeration=args.max_categories_per_enumeration,
        max_features=args.max_features,
    )
    path_exception_file = path_output_dir / "exceptions.csv"
    path_croissants = path_output_dir / "croissant"
    path_croissants.mkdir(exist_ok=True)
    if not path_exception_file.exists():
        with path_exception_file.open("w") as f:
            f.write("identifier,error_type,error\n")
    parquet_hasher = ParquetHasher(minio)
    logging.info(f"{len(identifiers)} datasets")
    for identifier in tqdm(identifiers):
        try:
            metadata_openml = openml.datasets.get_dataset(
                identifier,
                download_data=False,
                download_qualities=False,
                download_features_meta_data=True,
            )
            metadata_croissant = openml_croissant.convert(metadata_openml, settings, parquet_hasher)
            logging.info(f"Writing to {path_croissants / f'{identifier}.json'}")
            filepath = path_croissants / f"{identifier}.json"
            with filepath.open("w") as f:
                json.dump(
                    metadata_croissant,
                    f,
                    indent=4,
                    default=openml_croissant.serialize_croissant,
                )
            mlc.Dataset(filepath, debug=False)  # Validate, just to be sure.
        except Exception as e:
            with path_exception_file.open("a") as f:
                msg = str(e).replace("\n", ";")
                f.write(f"{identifier},{type(e).__name__},{msg}\n")
                logging.error(f"{type(e).__name__} exception on {identifier}: {msg}")


if __name__ == "__main__":
    main()
