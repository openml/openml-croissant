#!python3
"""
Script to run the OpenML Croissant Web API
"""

import argparse
import os

import openml
import uvicorn
from dotenv import load_dotenv
from minio import Minio

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
    return parser.parse_args()


def _minio_client() -> Minio:
    load_dotenv()
    return Minio(
        os.environ.get("MINIO_SERVER", default="openml1.win.tue.nl"),
        access_key=os.environ["MINIO_ACCESS_KEY"],
        secret_key=os.environ["MINIO_SECRET_KEY"],
        secure=bool(_strtobool(os.environ.get("MINIO_SECURE", "True"))),
        cert_check=bool(_strtobool(os.environ.get("MINIO_CERT_CHECK", "True"))),
    )


def _strtobool(input_: str) -> bool:
    return {"yes": True, "y": True, "true": True, "no": False, "n": False, "false": False}[
        input_.lower()
    ]


def main():
    args = _parse_args()
    minio = _minio_client()
    if server := os.environ.get("OPENML_SERVER"):
        openml.config.server = server
    app = openml_croissant.fastapi_app(minio)
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload, root_path=args.url_prefix)


if __name__ == "__main__":
    main()
