"""ASGI entry point: FastAPI + Socket.IO on the same origin.

Production: `uvicorn cuadrillapp.main:create_app --factory --workers 1`
"""

import asyncio
import contextlib
import logging
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass

import socketio
from fastapi import FastAPI

from cuadrillapp.http.health import health_router
from cuadrillapp.http.security import SecurityHeadersMiddleware
from cuadrillapp.http.static import SpaStaticFiles
from cuadrillapp.realtime.hub import RealtimeHub
from cuadrillapp.realtime.scheduler import AsyncioScheduler, Scheduler
from cuadrillapp.settings import Settings
from cuadrillapp.store.memory import MemoryRoomStore


@dataclass(frozen=True, slots=True)
class AppBundle:
    asgi: socketio.ASGIApp
    api: FastAPI
    hub: RealtimeHub


def build_app(
    settings: Settings | None = None,
    *,
    scheduler: Scheduler | None = None,
    clock: Callable[[], float] | None = None,
) -> AppBundle:
    settings = settings or Settings()
    hub = RealtimeHub(
        settings=settings,
        store=MemoryRoomStore(),
        scheduler=scheduler or AsyncioScheduler(),
        clock=clock or time.monotonic,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        sweeper = asyncio.create_task(hub.run_sweeper())
        try:
            yield
        finally:
            sweeper.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await sweeper

    api = FastAPI(
        title="Cuadrillapp",
        lifespan=lifespan,
        docs_url=None if settings.is_production else "/api/docs",
        redoc_url=None,
        openapi_url=None if settings.is_production else "/api/openapi.json",
    )
    api.add_middleware(SecurityHeadersMiddleware)
    api.include_router(health_router(settings))
    if settings.web_dist_dir is not None and settings.web_dist_dir.is_dir():
        api.mount("/", SpaStaticFiles(directory=settings.web_dist_dir), name="web")

    asgi = socketio.ASGIApp(hub.sio, other_asgi_app=api, socketio_path="socket.io")
    return AppBundle(asgi=asgi, api=api, hub=hub)


def create_app() -> socketio.ASGIApp:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    return build_app().asgi
