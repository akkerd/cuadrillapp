"""Room state. Plain dataclasses, no I/O."""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Literal

from cuadrillapp.constants import DEFAULT_TITLE

Role = Literal["candidate", "voter"]
Phase = Literal["lobby", "voting", "results"]
StartRequirement = Literal["categories", "candidates", "participants"]
ScoreKey = tuple[str, str, str]  # (voter_id, candidate_id, category_id)


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
    done: bool = False
    rejoin_token: str | None = None

    @property
    def has_device(self) -> bool:
        return not self.is_manual

    @property
    def present(self) -> bool:
        """Counts as present: connected, or still within the grace period."""
        return self.has_device and (self.connected or not self.away)


@dataclass(slots=True)
class Category:
    id: str
    emoji: str
    name: str


@dataclass(frozen=True, slots=True)
class RankEntry:
    candidate_id: str
    name: str
    emoji: str
    score: Fraction | None
    count: int
    position: int | None


@dataclass(frozen=True, slots=True)
class CategoryResult:
    category_id: str
    emoji: str
    name: str
    entries: tuple[RankEntry, ...]


@dataclass(frozen=True, slots=True)
class Results:
    overall: tuple[RankEntry, ...]
    by_category: tuple[CategoryResult, ...]


@dataclass(slots=True)
class Room:
    code: str
    created_at: float
    title: str = DEFAULT_TITLE
    phase: Phase = "lobby"
    participants: dict[str, Participant] = field(default_factory=dict)
    categories: list[Category] = field(default_factory=list)
    scores: dict[ScoreKey, int] = field(default_factory=dict)
    results: Results | None = None
    next_participant_seq: int = 1
    next_category_seq: int = 1
    version: int = 0
    empty_since: float | None = None

    def ordered_participants(self) -> list[Participant]:
        return sorted(self.participants.values(), key=lambda p: p.joined_seq)

    def candidates(self) -> list[Participant]:
        return [p for p in self.ordered_participants() if p.role == "candidate"]

    def category(self, category_id: str) -> Category | None:
        return next((c for c in self.categories if c.id == category_id), None)

    def start_missing(self) -> list[StartRequirement]:
        missing: list[StartRequirement] = []
        if not self.categories:
            missing.append("categories")
        if not self.candidates():
            missing.append("candidates")
        if len(self.participants) < 2:
            missing.append("participants")
        return missing
