"""Datos de respuesta (ack) de los comandos que devuelven algo."""

from cuadrillapp.domain.models import Phase
from cuadrillapp.protocol.base import Outgoing


class JoinResult(Outgoing):
    code: str
    participant_id: str
    token: str


class RejoinResult(Outgoing):
    participant_id: str


class PeekResult(Outgoing):
    code: str
    title: str
    phase: Phase
    full: bool


class KickedEvent(Outgoing):
    code: str


class ReplacedEvent(Outgoing):
    code: str
