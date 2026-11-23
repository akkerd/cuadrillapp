"""Endpoint de salud: Render lo usa para decidir si la versión nueva puede recibir tráfico."""

from fastapi import APIRouter

from cuadrillapp.settings import Settings


def health_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "version": settings.render_git_commit}

    return router
