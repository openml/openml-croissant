"""
Defines web API endpoints.
"""

import typing

import openml
from fastapi import Depends, FastAPI, HTTPException
from openml.exceptions import OpenMLServerException
from starlette import status

import openml_croissant
from openml_croissant._src.hashing import ParquetHasher

if typing.TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client


def fastapi_app(s3_client: S3Client) -> FastAPI:
    """Create the FastAPI application, complete with routes."""

    app = FastAPI(
        openapi_url="/openapi.json",
        docs_url="/docs",
        swagger_ui_init_oauth={
            "appName": "OpenML Croissant bakery",
        },
    )
    parquet_hasher = ParquetHasher(s3_client)

    @app.get("/{identifier}")
    def convert(identifier: int, settings: openml_croissant.Settings = Depends()) -> dict:
        try:
            metadata_openml = openml.datasets.get_dataset(
                identifier,
                download_data=False,
                download_qualities=False,
                download_features_meta_data=True,
            )
        except OpenMLServerException as e:
            if e.message and "Unknown dataset" in e.message:
                msg = f"Dataset with identifier {identifier} not found in OpenML."
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg) from e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Unexpected response from OpenML: "{e.message}"',
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Unexpected response from OpenML: "{str(e)}"',
            ) from e
        try:
            return openml_croissant.convert(metadata_openml, settings, parquet_hasher)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error on conversion: {str(e)}",
            ) from e

    return app
