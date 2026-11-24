"""Room state as each participant sees it."""

from cuadrillapp.domain.models import Phase, Role
from cuadrillapp.protocol.base import Outgoing


class ParticipantView(Outgoing):
    id: str
    name: str
    emoji: str
    role: Role
    is_admin: bool
    is_manual: bool
    connected: bool


class Me(Outgoing):
    participant_id: str
    is_admin: bool


class RoomSnapshot(Outgoing):
    code: str
    version: int
    title: str
    phase: Phase
    me: Me
    participants: list[ParticipantView]
