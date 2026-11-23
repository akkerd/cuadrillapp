"""Sirve la build de la PWA con fallback a index.html para las rutas de la SPA."""

from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

NO_CACHE = {"index.html", "sw.js", "registerSW.js", "manifest.webmanifest"}
API_PREFIXES = ("api/", "healthz", "socket.io/")


class SpaStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            response = await super().get_response(path, scope)
            served = path
        except HTTPException as exc:
            if exc.status_code != 404 or path.startswith(API_PREFIXES) or _looks_like_file(path):
                raise
            response = await super().get_response("index.html", scope)
            served = "index.html"
        _cache_headers(served, response)
        return response


def _looks_like_file(path: str) -> bool:
    """`/assets/x.js` que no existe debe dar 404; `/r/ABC23` o `/` caen en la SPA."""
    return path not in ("", ".") and "." in path.rsplit("/", 1)[-1]


def _cache_headers(path: str, response: Response) -> None:
    name = path.rsplit("/", 1)[-1] or "index.html"
    if path in ("", ".") or name in NO_CACHE or name.startswith("workbox-"):
        response.headers["Cache-Control"] = "no-cache"
    elif path.startswith("assets/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
