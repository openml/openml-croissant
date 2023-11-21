"""
Defines web API endpoints.
"""
import openml
from fastapi import FastAPI

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
        metadata_openml = openml.datasets.get_dataset(identifier)
        return conversion.convert(metadata_openml)

    return app
