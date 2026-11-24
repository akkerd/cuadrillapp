"""Keyed timers, swappable for a fake implementation in tests."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol

type Callback = Callable[[], Awaitable[None]]


class Scheduler(Protocol):
    def call_later(self, delay: float, key: str, callback: Callback) -> None: ...
    def cancel(self, key: str) -> None: ...
    def cancel_prefix(self, prefix: str) -> None: ...


class AsyncioScheduler:
    def __init__(self) -> None:
        self._handles: dict[str, asyncio.TimerHandle] = {}
        self._tasks: set[asyncio.Task[None]] = set()

    def call_later(self, delay: float, key: str, callback: Callback) -> None:
        self.cancel(key)
        loop = asyncio.get_running_loop()

        def fire() -> None:
            self._handles.pop(key, None)
            task = loop.create_task(_run(callback))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

        self._handles[key] = loop.call_later(delay, fire)

    def cancel(self, key: str) -> None:
        handle = self._handles.pop(key, None)
        if handle is not None:
            handle.cancel()

    def cancel_prefix(self, prefix: str) -> None:
        for key in [k for k in self._handles if k.startswith(prefix)]:
            self.cancel(key)


async def _run(callback: Callback) -> None:
    await callback()


class FakeClock:
    """Clock controlled by the tests."""

    def __init__(self, start: float = 1_000.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now


class FakeScheduler:
    """Runs timers when the fake clock advances, without waiting."""

    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self._pending: dict[str, tuple[float, Callback]] = {}

    def call_later(self, delay: float, key: str, callback: Callback) -> None:
        self._pending[key] = (self.clock.now + delay, callback)

    def cancel(self, key: str) -> None:
        self._pending.pop(key, None)

    def cancel_prefix(self, prefix: str) -> None:
        for key in [k for k in self._pending if k.startswith(prefix)]:
            self.cancel(key)

    def pending(self) -> list[str]:
        return list(self._pending)

    async def advance(self, seconds: float) -> None:
        self.clock.now += seconds
        due = sorted(
            ((when, key) for key, (when, _) in self._pending.items() if when <= self.clock.now),
        )
        for _, key in due:
            entry = self._pending.pop(key, None)
            if entry is not None:
                await entry[1]()
