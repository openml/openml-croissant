#!python3
"""
Script to run the OpenML Croissant Web API
"""

import argparse
import os
import typing

import boto3
import openml
import uvicorn
from botocore import UNSIGNED
from botocore.config import Config

if typing.TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client

import openml_croissant


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the web API. Please refer to the README.")
    parser.add_argument("--url-prefix", default="", help="Prefix for the api url.")
    parser.add_argument(
        "--reload",
        action=argparse.BooleanOptionalAction,
        help="Use `--reload` for FastAPI.",
    )
    parser.add_argument("--host", default="localhost", help="Bind the socket to this host.")
    parser.add_argument("--port", type=int, default=8000, help="Bind the socket to this port.")
    parser.add_argument(
        "--s3-server",
        type=str,
        default="https://www.openml.org/s3/",
        help="The OpenML S3 server url, used to find the Parquet hashes.",
    )
    return parser.parse_args()


def _create_s3_client(s3_server: str) -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url=s3_server,
        config=Config(s3={"addressing_style": "path"}, signature_version=UNSIGNED),
    )


def _strtobool(input_: str) -> bool:
    return {"yes": True, "y": True, "true": True, "no": False, "n": False, "false": False}[
        input_.lower()
    ]


def main():
    args = _parse_args()
    if server := os.environ.get("OPENML_SERVER"):
        openml.config.server = server
    s3_client = _create_s3_client(args.s3_server)
    app = openml_croissant.fastapi_app(s3_client)
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload, root_path=args.url_prefix)


if __name__ == "__main__":
    main()
