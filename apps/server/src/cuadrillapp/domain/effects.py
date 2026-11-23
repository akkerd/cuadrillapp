"""Resultado de aplicar un comando y efectos que ejecuta la capa realtime."""

from dataclasses import dataclass

from pydantic import BaseModel

from cuadrillapp.domain.models import Room


@dataclass(frozen=True, slots=True)
class Disconnect:
    """Comando interno: el socket del actor se ha cerrado."""


@dataclass(frozen=True, slots=True)
class GraceExpired:
    """Comando interno: el actor lleva desconectado más que el periodo de gracia."""


type InternalCommand = Disconnect | GraceExpired


@dataclass(frozen=True, slots=True)
class StartGrace:
    participant_id: str


@dataclass(frozen=True, slots=True)
class CancelGrace:
    participant_id: str


@dataclass(frozen=True, slots=True)
class SeatReleased:
    """El participante ya no está en la sala (salió o lo expulsaron)."""

    participant_id: str
    kicked: bool


type Effect = StartGrace | CancelGrace | SeatReleased


@dataclass(frozen=True, slots=True)
class Applied:
    room: Room
    data: BaseModel | None = None
    effects: tuple[Effect, ...] = ()
