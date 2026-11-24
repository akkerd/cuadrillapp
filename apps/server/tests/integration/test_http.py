from pathlib import Path

import httpx
import pytest

from cuadrillapp.main import build_app
from cuadrillapp.settings import Settings


@pytest.fixture
def dist(tmp_path: Path) -> Path:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<!doctype html><title>Cuadrillapp</title>")
    (tmp_path / "assets" / "app-123.js").write_text("console.log(1)")
    (tmp_path / "sw.js").write_text("self.addEventListener('install', () => {})")
    return tmp_path


def _client(settings: Settings) -> httpx.AsyncClient:
    app = build_app(settings).asgi
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_healthz_reports_version() -> None:
    async with _client(Settings(env="test", render_git_commit="abc123")) as client:
        response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "abc123"}


async def test_spa_fallback_serves_index_for_room_links(dist: Path) -> None:
    async with _client(Settings(env="test", web_dist_dir=dist)) as client:
        root = await client.get("/")
        room = await client.get("/r/ABC23")
    assert root.status_code == room.status_code == 200
    assert "Cuadrillapp" in room.text
    assert room.headers["cache-control"] == "no-cache"


async def test_assets_are_cached_forever_and_sw_is_not(dist: Path) -> None:
    async with _client(Settings(env="test", web_dist_dir=dist)) as client:
        asset = await client.get("/assets/app-123.js")
        sw = await client.get("/sw.js")
    assert "immutable" in asset.headers["cache-control"]
    assert sw.headers["cache-control"] == "no-cache"


async def test_missing_files_and_api_paths_are_404(dist: Path) -> None:
    async with _client(Settings(env="test", web_dist_dir=dist)) as client:
        missing_asset = await client.get("/assets/nope.js")
        api = await client.get("/api/nope")
    assert missing_asset.status_code == 404
    assert api.status_code == 404


async def test_security_headers(dist: Path) -> None:
    async with _client(Settings(env="test", web_dist_dir=dist)) as client:
        response = await client.get("/")
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["x-content-type-options"] == "nosniff"


async def test_docs_are_disabled_in_production() -> None:
    async with _client(Settings(env="production")) as client:
        response = await client.get("/api/docs")
    assert response.status_code == 404
