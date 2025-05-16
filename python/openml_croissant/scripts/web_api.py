#!python3
"""
Script to run the OpenML Croissant Web API
"""

import argparse

import uvicorn

import openml_croissant
from openml_croissant.scripts.upload_datasets_to_minio import minio_client


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


def main():
    args = _parse_args()
    minio = minio_client()
    app = openml_croissant.fastapi_app(minio)
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload, root_path=args.url_prefix)


if __name__ == "__main__":
    main()
