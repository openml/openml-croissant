#!python3
"""
Temporary script, to upload all data to MinIO. Not part of the main python package, because it
will be deleted (or edited?) later.

This is a temporary solution: for now we'll just upload the data to MinIO,
and React will request the data to embed it. Newer datasets won't have a croissant.
Later we'll figure out a permanent solution.
"""

import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from minio import Minio
from tqdm import tqdm


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
    parser.add_argument(
        "--client-url",
        type=str,
        help="Client url",
        default="openml1.win.tue.nl",
    )
    return parser.parse_args()


def format_parquet_object_name() -> str:
    return "croissant.json"


def minio_client(url):
    return Minio(
        url,
        access_key=os.environ["MINIO_ACCESS_KEY"],
        secret_key=os.environ["MINIO_SECRET_KEY"],
        secure=True,
    )


def main():
    args = _parse_args()
    load_dotenv()
    path_croissant_dir = Path(args.input_directory) / "croissant"
    client = minio_client(args.client_url)
    if not path_croissant_dir.exists():
        msg = f"Input directory not found: {path_croissant_dir}"
        raise ValueError(msg)
    if args.id:
        files = [path_croissant_dir / f"{a}.json" for a in args.id]
    else:
        files = list(path_croissant_dir.iterdir())
    for file in tqdm(files):
        identifier = file.stem
        bucket_name = f"dataset{identifier}"
        minio_file_path = format_parquet_object_name()
        if not client.bucket_exists(bucket_name):
            # we don't want to create more buckets!
            logging.warning(f"Bucket {bucket_name} does not exist, ignoring for now.")
        else:
            client.fput_object(bucket_name, minio_file_path, file)


if __name__ == "__main__":
    main()
