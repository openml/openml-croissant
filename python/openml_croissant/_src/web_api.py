"""
Defines web API endpoints.
"""
import openml
from fastapi import FastAPI, HTTPException
from openml.exceptions import OpenMLServerException
from starlette import status

from openml_croissant._src import conversion


def fastapi_app(url_prefix: str) -> FastAPI:
    """Create the FastAPI application, complete with routes."""
    app = FastAPI(
        openapi_url=f"{url_prefix}/openapi.json",
        docs_url=f"{url_prefix}/docs",
        swagger_ui_init_oauth={
            "appName": "OpenML Croissant bakery",
        },
    )

    @app.get(url_prefix + "/croissant/{identifier}")
    def convert(identifier: int) -> dict:
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
            return conversion.convert(metadata_openml)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error on conversion: {str(e)}",
            ) from e

    return app
