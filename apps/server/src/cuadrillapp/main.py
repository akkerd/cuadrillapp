"""ASGI entry point.

Production: `uvicorn cuadrillapp.main:create_app --factory --workers 1`
"""

import logging
from dataclasses import dataclass

from fastapi import FastAPI

from cuadrillapp.http.health import health_router
from cuadrillapp.http.security import SecurityHeadersMiddleware
from cuadrillapp.http.static import SpaStaticFiles
from cuadrillapp.settings import Settings


@dataclass(frozen=True, slots=True)
class AppBundle:
    asgi: FastAPI
    api: FastAPI


def build_app(settings: Settings | None = None) -> AppBundle:
    settings = settings or Settings()
    api = FastAPI(
        title="Cuadrillapp",
        docs_url=None if settings.is_production else "/api/docs",
        redoc_url=None,
        openapi_url=None if settings.is_production else "/api/openapi.json",
    )
    api.add_middleware(SecurityHeadersMiddleware)
    api.include_router(health_router(settings))
    if settings.web_dist_dir is not None and settings.web_dist_dir.is_dir():
        api.mount("/", SpaStaticFiles(directory=settings.web_dist_dir), name="web")
    return AppBundle(asgi=api, api=api)


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    return build_app().asgi
