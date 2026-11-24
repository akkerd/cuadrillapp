"""Socket.IO server: validate, apply domain rules, store and broadcast.

Atomicity rule: there is no `await` between a room's `store.get` and `store.put`.
With a single event loop, two commands never interleave on the same room.
"""

import asyncio
import contextlib
import logging
import secrets
from collections.abc import Callable, Coroutine
from typing import Any

import socketio
from pydantic import BaseModel, ValidationError

from cuadrillapp.constants import MAX_PARTICIPANTS
from cuadrillapp.domain.apply import apply_command, create_room, join_room, rejoin_room
from cuadrillapp.domain.codes import generate_code, normalize_code
from cuadrillapp.domain.effects import (
    Applied,
    CancelGrace,
    Disconnect,
    Effect,
    GraceExpired,
    SeatReleased,
    StartGrace,
)
from cuadrillapp.domain.errors import DomainError
from cuadrillapp.domain.projection import project_snapshot
from cuadrillapp.protocol import commands as c
from cuadrillapp.protocol.acks import AckPayload, ack_error, ack_ok
from cuadrillapp.protocol.registry import COMMANDS
from cuadrillapp.protocol.results import KickedEvent, PeekResult, ReplacedEvent
from cuadrillapp.realtime.ratelimit import TokenBucketLimiter, WindowLimiter
from cuadrillapp.realtime.scheduler import Scheduler
from cuadrillapp.settings import Settings
from cuadrillapp.store.base import RoomStore

log = logging.getLogger("cuadrillapp.realtime")

type Clock = Callable[[], float]
type TokenFactory = Callable[[], str]

_ENTRY_EVENTS = {"room:create", "room:peek", "room:join", "room:rejoin"}


class RealtimeHub:
    def __init__(
        self,
        settings: Settings,
        store: RoomStore,
        scheduler: Scheduler,
        clock: Clock,
        token_factory: TokenFactory | None = None,
    ) -> None:
        self.settings = settings
        self.store = store
        self.scheduler = scheduler
        self.clock = clock
        self.token_factory = token_factory or _new_token
        self.limiter = TokenBucketLimiter(settings.rate_capacity, settings.rate_refill_per_second)
        self.create_limiter = WindowLimiter(settings.room_creates_per_minute, 60)
        # room → participant → sid of the socket holding the seat
        self.seats: dict[str, dict[str, str]] = {}
        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=settings.cors_origins,
            logger=False,
            engineio_logger=False,
        )
        self._register()

    # --- Event registration -----------------------------------------------------------

    def _register(self) -> None:
        self.sio.on("connect", self._on_connect)
        self.sio.on("disconnect", self._on_disconnect)
        self.sio.on("room:create", self._room_create)
        self.sio.on("room:peek", self._room_peek)
        self.sio.on("room:join", self._room_join)
        self.sio.on("room:rejoin", self._room_rejoin)
        for event, (model, _) in COMMANDS.items():
            if event not in _ENTRY_EVENTS:
                self.sio.on(event, self._handler_for(model))

    def _handler_for(
        self, model: type[c.Command]
    ) -> Callable[[str, object], Coroutine[Any, Any, AckPayload]]:
        async def handler(sid: str, data: object = None) -> AckPayload:
            return await self._dispatch(model, sid, data)

        return handler

    async def _on_connect(self, sid: str, environ: dict[str, Any], auth: object = None) -> None:
        await self.sio.save_session(sid, {"ip": environ.get("REMOTE_ADDR", "unknown")})

    async def _on_disconnect(self, sid: str, *_: object) -> None:
        self.limiter.forget(sid)
        await self._release_socket(sid, mark_disconnected=True)

    # --- Entering rooms ----------------------------------------------------------------

    async def _room_create(self, sid: str, data: object = None) -> AckPayload:
        cmd = self._parse(sid, c.RoomCreate, data)
        if isinstance(cmd, dict):
            return cmd
        now = self.clock()
        session = await self.sio.get_session(sid)
        if not self.create_limiter.allow(str(session.get("ip")), now):
            return ack_error("RATE_LIMITED")
        if self.store.count() >= self.settings.max_rooms:
            return ack_error("TOO_MANY_ROOMS")
        code = generate_code(self.store.exists)
        outcome = create_room(code=code, cmd=cmd, token=self.token_factory(), now=now)
        if isinstance(outcome, DomainError):
            return ack_error(outcome.code)
        self.store.put(outcome.room)
        return await self._enter(sid, outcome)

    async def _room_peek(self, sid: str, data: object = None) -> AckPayload:
        cmd = self._parse(sid, c.RoomPeek, data)
        if isinstance(cmd, dict):
            return cmd
        room = self.store.get(normalize_code(cmd.code))
        if room is None:
            return ack_error("ROOM_NOT_FOUND")
        full = len(room.participants) >= MAX_PARTICIPANTS
        return ack_ok(PeekResult(code=room.code, title=room.title, phase=room.phase, full=full))

    async def _room_join(self, sid: str, data: object = None) -> AckPayload:
        cmd = self._parse(sid, c.RoomJoin, data)
        if isinstance(cmd, dict):
            return cmd
        room = self.store.get(normalize_code(cmd.code))
        if room is None:
            return ack_error("ROOM_NOT_FOUND")
        outcome = join_room(room, cmd=cmd, token=self.token_factory(), now=self.clock())
        if isinstance(outcome, DomainError):
            return ack_error(outcome.code)
        self.store.put(outcome.room)
        return await self._enter(sid, outcome)

    async def _room_rejoin(self, sid: str, data: object = None) -> AckPayload:
        cmd = self._parse(sid, c.RoomRejoin, data)
        if isinstance(cmd, dict):
            return cmd
        room = self.store.get(normalize_code(cmd.code))
        if room is None:
            return ack_error("ROOM_NOT_FOUND")
        outcome = rejoin_room(room, token=cmd.token, now=self.clock())
        if isinstance(outcome, DomainError):
            return ack_error(outcome.code)
        self.store.put(outcome.room)
        return await self._enter(sid, outcome)

    async def _enter(self, sid: str, outcome: Applied) -> AckPayload:
        """Bind the socket to the newly created or recovered seat and broadcast the state."""
        code = outcome.room.code
        participant_id = getattr(outcome.data, "participant_id", None)
        if not isinstance(participant_id, str):
            raise TypeError("entry outcome without participant_id")
        await self._release_socket(sid, mark_disconnected=True, keep=(code, participant_id))
        previous = self.seats.setdefault(code, {}).get(participant_id)
        self.seats[code][participant_id] = sid
        async with self.sio.session(sid) as session:
            session["room"] = code
            session["pid"] = participant_id
        if previous is not None and previous != sid:
            await self._detach(previous)
            await self.sio.emit("room:replaced", _dump(ReplacedEvent(code=code)), to=previous)
        await self._run_effects(code, outcome.effects)
        await self.broadcast(code)
        return ack_ok(outcome.data)

    # --- Commands inside a room -------------------------------------------------------

    async def _dispatch(self, model: type[c.Command], sid: str, data: object) -> AckPayload:
        cmd = self._parse(sid, model, data)
        if isinstance(cmd, dict):
            return cmd
        session = await self.sio.get_session(sid)
        code, participant_id = session.get("room"), session.get("pid")
        if not isinstance(code, str) or not isinstance(participant_id, str):
            return ack_error("NOT_IN_ROOM")
        return await self.apply(code, participant_id, cmd)

    async def apply(
        self, code: str, participant_id: str, cmd: c.Command | Disconnect | GraceExpired
    ) -> AckPayload:
        room = self.store.get(code)
        if room is None:
            return ack_error("ROOM_NOT_FOUND")
        outcome = apply_command(room, participant_id, cmd, self.clock())
        if isinstance(outcome, DomainError):
            return ack_error(outcome.code)
        self.store.put(outcome.room)  # ← no await between get and put
        await self._run_effects(code, outcome.effects)
        await self.broadcast(code)
        return ack_ok(outcome.data)

    def _parse[M: BaseModel](self, sid: str, model: type[M], data: object) -> M | AckPayload:
        if not self.limiter.allow(sid, self.clock()):
            return ack_error("RATE_LIMITED")
        try:
            return model.model_validate({} if data is None else data)
        except ValidationError:
            return ack_error("INVALID")

    # --- Effects and broadcast --------------------------------------------------------

    async def _run_effects(self, code: str, effects: tuple[Effect, ...]) -> None:
        for effect in effects:
            match effect:
                case StartGrace(participant_id=pid):
                    self.scheduler.call_later(
                        self.settings.admin_grace_seconds,
                        _grace_key(code, pid),
                        self._grace_callback(code, pid),
                    )
                case CancelGrace(participant_id=pid):
                    self.scheduler.cancel(_grace_key(code, pid))
                case SeatReleased(participant_id=pid, kicked=kicked):
                    self.scheduler.cancel(_grace_key(code, pid))
                    sid = self.seats.get(code, {}).pop(pid, None)
                    if sid is not None:
                        await self._detach(sid)
                        if kicked:
                            await self.sio.emit(
                                "room:kicked", _dump(KickedEvent(code=code)), to=sid
                            )

    def _grace_callback(
        self, code: str, participant_id: str
    ) -> Callable[[], Coroutine[Any, Any, None]]:
        async def expire() -> None:
            await self.apply(code, participant_id, GraceExpired())

        return expire

    async def broadcast(self, code: str) -> None:
        room = self.store.get(code)
        if room is None:
            return
        snapshots = {
            sid: _dump(project_snapshot(room, pid))
            for pid, sid in self.seats.get(code, {}).items()
            if pid in room.participants
        }
        # Clients drop snapshots whose `version` is lower than the last one they saw, so
        # the order of concurrent emits does not matter.
        for sid, snapshot in snapshots.items():
            await self.sio.emit("room:state", snapshot, to=sid)

    async def _release_socket(
        self, sid: str, *, mark_disconnected: bool, keep: tuple[str, str] | None = None
    ) -> None:
        """Free the seat this socket held (on disconnect or when switching rooms)."""
        with contextlib.suppress(KeyError):
            session = await self.sio.get_session(sid)
            code, pid = session.get("room"), session.get("pid")
            if not isinstance(code, str) or not isinstance(pid, str) or (code, pid) == keep:
                return
            if self.seats.get(code, {}).get(pid) != sid:
                return
            del self.seats[code][pid]
            await self._detach(sid)
            if mark_disconnected:
                await self.apply(code, pid, Disconnect())

    async def _detach(self, sid: str) -> None:
        with contextlib.suppress(KeyError):
            async with self.sio.session(sid) as session:
                session.pop("room", None)
                session.pop("pid", None)

    # --- Cleanup ----------------------------------------------------------------------

    def sweep(self) -> list[str]:
        """Delete rooms with nobody connected for longer than the TTL. Return their codes."""
        now = self.clock()
        removed: list[str] = []
        for code in self.store.codes():
            room = self.store.get(code)
            if room is None or room.empty_since is None:
                continue
            if now - room.empty_since >= self.settings.room_idle_ttl_seconds:
                self.store.delete(code)
                self.seats.pop(code, None)
                self.scheduler.cancel_prefix(f"grace:{code}:")
                removed.append(code)
        if removed:
            log.info("swept %d idle rooms", len(removed))
        return removed

    async def run_sweeper(self) -> None:
        while True:
            await asyncio.sleep(self.settings.sweep_interval_seconds)
            self.sweep()


def _new_token() -> str:
    return secrets.token_urlsafe(16)


def _grace_key(code: str, participant_id: str) -> str:
    return f"grace:{code}:{participant_id}"


def _dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json")
