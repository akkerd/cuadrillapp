"""Servidor real (Uvicorn en el mismo event loop) y clientes Socket.IO que simulan móviles."""

import asyncio
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any

import pytest
import socketio
import uvicorn

from cuadrillapp.main import build_app
from cuadrillapp.realtime.hub import RealtimeHub
from cuadrillapp.realtime.scheduler import FakeClock, FakeScheduler
from cuadrillapp.settings import Settings


@dataclass
class Live:
    url: str
    hub: RealtimeHub
    clock: FakeClock
    scheduler: FakeScheduler
    players: list[Player] = field(default_factory=list)

    async def player(self) -> Player:
        player = Player(self.url)
        await player.connect()
        self.players.append(player)
        return player


class Player:
    """Un móvil: guarda el último snapshot y los eventos recibidos."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.client = socketio.AsyncClient(reconnection=False)
        self.state: dict[str, Any] | None = None
        self.events: list[tuple[str, dict[str, Any]]] = []
        self._changed = asyncio.Event()

        async def on_state(data: dict[str, Any]) -> None:
            if self.state is None or data["version"] >= self.state["version"]:
                self.state = data
            self._changed.set()

        async def on_any(event: str, data: dict[str, Any]) -> None:
            self.events.append((event, data))
            self._changed.set()

        self.client.on("room:state", on_state)
        self.client.on("*", on_any)

    async def connect(self) -> None:
        await self.client.connect(self.url, transports=["websocket"], wait_timeout=5)

    async def call(self, event: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        result: dict[str, Any] = await self.client.call(event, data or {}, timeout=5)
        return result

    async def ok(self, event: str, data: dict[str, Any] | None = None) -> Any:
        result = await self.call(event, data)
        assert result["ok"], result
        return result["data"]

    async def wait_for(
        self, predicate: Callable[[dict[str, Any]], bool], timeout: float = 3
    ) -> dict[str, Any]:
        async with asyncio.timeout(timeout):
            while self.state is None or not predicate(self.state):
                self._changed.clear()
                await self._changed.wait()
        return self.state

    async def close(self) -> None:
        if self.client.connected:
            await self.client.disconnect()


@pytest.fixture
async def live() -> AsyncIterator[Live]:
    clock = FakeClock()
    scheduler = FakeScheduler(clock)
    settings = Settings(env="test", rate_capacity=200, rate_refill_per_second=200)
    bundle = build_app(settings, scheduler=scheduler, clock=clock)
    config = uvicorn.Config(bundle.asgi, host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    async with asyncio.timeout(5):
        while not server.started:
            await asyncio.sleep(0.01)
    port = server.servers[0].sockets[0].getsockname()[1]
    env = Live(url=f"http://127.0.0.1:{port}", hub=bundle.hub, clock=clock, scheduler=scheduler)
    try:
        yield env
    finally:
        for player in env.players:
            await player.close()
        server.should_exit = True
        await task


def profile(name: str, role: str = "candidate", emoji: str = "🦄") -> dict[str, str]:
    return {"name": name, "emoji": emoji, "role": role}
