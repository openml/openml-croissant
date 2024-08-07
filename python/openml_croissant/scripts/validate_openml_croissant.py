#!python3
"""
Script to validate a croissant file that's been uploaded to the OpenML website. Makes it easy to
validate a file based on the newest mlcroissant version.

Created this script after a message from Pierre Marcenac, stating that some of the croissants did
not pass validation.
"""


import argparse
import json
import logging
import tempfile
from pathlib import Path

import mlcroissant as mlc
from dotenv import load_dotenv

from openml_croissant.scripts.upload_datasets_to_minio import (
    format_croissant_object_name,
    minio_client,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate croissants.")
    parser.add_argument(
        "--id",
        type=int,
        nargs="*",
        help="Openml dataset identifier to check.",
        required=True,
    )
    parser.add_argument(
        "--site",
        type=str,
        help="Openml website.",
        default="https://www.openml.org/",
    )
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = _parse_args()
    load_dotenv()
    client = minio_client()
    for identifier in args.id:
        bucket_name = f"dataset{identifier}"
        minio_file_name = format_croissant_object_name(identifier)
        response = None
        try:
            response = client.get_object(bucket_name, minio_file_name)
            croissant = response.json()
            with tempfile.TemporaryDirectory() as tmp_dir:
                filename = Path(tmp_dir) / "croissant.json"
                with filename.open("w") as f:
                    json.dump(croissant, f, indent=4)
                logging.info(f"Checking {identifier}")
                mlc.Dataset(filename, debug=False)
                logging.info(f"Checking {identifier} done")
        except Exception:
            logging.exception("Exception while reading or validating croissant")
        finally:
            if response is not None:
                response.close()
                response.release_conn()


if __name__ == "__main__":
    main()
