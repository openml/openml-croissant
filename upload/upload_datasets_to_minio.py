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
from pathlib import Path

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
    parser.add_argument(
        "-a",
        "--access_key",
        type=str,
        required=True,
        help="Credentials for the Minio tenant.",
    )
    parser.add_argument(
        "-s",
        "--secret-key",
        type=str,
        required=True,
        help="Credentials for the Minio tenant.",
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    client = Minio(
        args.client_url,
        access_key=args.access_key,
        secret_key=args.secret_key,
        secure=True,
    )
    path_croissant_dir = Path(args.input_directory) / "croissant"
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
        if not client.bucket_exists(bucket_name):
            # we don't want to create more buckets!
            logging.warning(f"Bucket {bucket_name} does not exist, ignoring for now.")
        else:
            client.fput_object(bucket_name, "croissant.json", file)


if __name__ == "__main__":
    main()
