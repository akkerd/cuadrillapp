"""Health endpoint: Render uses it to decide whether a new version may receive traffic."""

from fastapi import APIRouter

from cuadrillapp.settings import Settings


def health_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "version": settings.render_git_commit}

    return router
