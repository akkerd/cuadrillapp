"""Outcome of applying a command, and the effects the realtime layer runs."""

from dataclasses import dataclass

from pydantic import BaseModel

from cuadrillapp.domain.models import Room


@dataclass(frozen=True, slots=True)
class Disconnect:
    """Internal command: the actor's socket has closed."""


@dataclass(frozen=True, slots=True)
class GraceExpired:
    """Internal command: the actor has been disconnected longer than the grace period."""


type InternalCommand = Disconnect | GraceExpired


@dataclass(frozen=True, slots=True)
class StartGrace:
    participant_id: str


@dataclass(frozen=True, slots=True)
class CancelGrace:
    participant_id: str


@dataclass(frozen=True, slots=True)
class SeatReleased:
    """The participant is no longer in the room (they left or were kicked)."""

    participant_id: str
    kicked: bool


type Effect = StartGrace | CancelGrace | SeatReleased


@dataclass(frozen=True, slots=True)
class Applied:
    room: Room
    data: BaseModel | None = None
    effects: tuple[Effect, ...] = ()
