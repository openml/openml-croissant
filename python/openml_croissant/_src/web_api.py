"""
Defines web API endpoints.
"""

import openml
from fastapi import Depends, FastAPI, HTTPException
from minio import Minio
from openml.exceptions import OpenMLServerException
from starlette import status

import openml_croissant
from openml_croissant._src.hashing import ParquetHasher


def fastapi_app(minio_client: Minio) -> FastAPI:
    """Create the FastAPI application, complete with routes."""

    app = FastAPI(
        openapi_url="/openapi.json",
        docs_url="/docs",
        swagger_ui_init_oauth={
            "appName": "OpenML Croissant bakery",
        },
    )
    parquet_hasher = ParquetHasher(minio_client)

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
