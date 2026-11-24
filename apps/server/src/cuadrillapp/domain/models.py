"""Room state. Plain dataclasses, no I/O."""

from dataclasses import dataclass, field
from typing import Literal

from cuadrillapp.constants import DEFAULT_TITLE

Role = Literal["candidate", "voter"]
Phase = Literal["lobby"]


@dataclass(slots=True)
class Participant:
    id: str
    name: str
    emoji: str
    role: Role
    joined_seq: int
    is_admin: bool = False
    is_manual: bool = False
    connected: bool = False
    away: bool = False  # disconnected for longer than the grace period
    rejoin_token: str | None = None

    @property
    def has_device(self) -> bool:
        return not self.is_manual

    @property
    def present(self) -> bool:
        """Counts as present: connected, or still within the grace period."""
        return self.has_device and (self.connected or not self.away)


@dataclass(slots=True)
class Room:
    code: str
    created_at: float
    title: str = DEFAULT_TITLE
    phase: Phase = "lobby"
    participants: dict[str, Participant] = field(default_factory=dict)
    next_participant_seq: int = 1
    version: int = 0
    empty_since: float | None = None

    def ordered_participants(self) -> list[Participant]:
        return sorted(self.participants.values(), key=lambda p: p.joined_seq)

    def candidates(self) -> list[Participant]:
        return [p for p in self.ordered_participants() if p.role == "candidate"]
