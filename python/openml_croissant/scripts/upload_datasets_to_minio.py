#!python3
"""
Temporary script, to upload all data to MinIO. Not part of the main python package, because it
will be deleted (or edited?) later.

This is a temporary solution: for now we'll just upload the data to MinIO, and React will request
the data to embed it. We're running a cronjob to periodically convert new datasets.
"""

import argparse
import os
from distutils.util import strtobool
from pathlib import Path

from dotenv import load_dotenv
from minio import Minio
from tqdm import tqdm

from openml_croissant._src.logger import setup_logger

DATASET_BUCKET = "datasets"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload croissants to MinIO.")
    parser.add_argument(
        "--id",
        type=int,
        nargs="*",
        help="Openml dataset identifier for which to copy the croissant. If empty, all the "
        "identifiers from the input directory will be copied.",
    )
    parser.add_argument(
        "-i",
        "--input-directory",
        type=str,
        required=True,
        help="A path to the directory where the croissants have been written to.",
    )
    return parser.parse_args()


def minio_client() -> Minio:
    load_dotenv()
    return Minio(
        os.environ.get("MINIO_SERVER", default="openml1.win.tue.nl"),
        access_key=os.environ["MINIO_ACCESS_KEY"],
        secret_key=os.environ["MINIO_SECRET_KEY"],
        secure=bool(strtobool(os.environ.get("MINIO_SECURE", "True"))),
    )


def format_croissant_object_name(dataset_id: int) -> str:
    return f"{dataset_id // 10000:04d}/{dataset_id:04d}/dataset_{dataset_id}_croissant.json"


def main():
    args = _parse_args()
    setup_logger()
    path_croissant_dir = Path(args.input_directory) / "croissant"
    client = minio_client()
    if not path_croissant_dir.exists():
        msg = f"Input directory not found: {path_croissant_dir}"
        raise ValueError(msg)
    if args.id:
        files = [path_croissant_dir / f"{a}.json" for a in args.id]
    else:
        files = list(path_croissant_dir.iterdir())
    for file in tqdm(files):
        identifier = int(file.stem)
        minio_file_path = format_croissant_object_name(identifier)
        client.fput_object(DATASET_BUCKET, minio_file_path, file)


if __name__ == "__main__":
    main()
