"""Estado de la sala tal como lo ve cada participante."""

from cuadrillapp.domain.models import Phase, Role, StartRequirement
from cuadrillapp.protocol.base import Outgoing


class Progress(Outgoing):
    given: int
    total: int


class ParticipantView(Outgoing):
    id: str
    name: str
    emoji: str
    role: Role
    is_admin: bool
    is_manual: bool
    connected: bool
    done: bool
    progress: Progress | None


class CategoryView(Outgoing):
    id: str
    emoji: str
    name: str


class ScoreView(Outgoing):
    voter_id: str
    candidate_id: str
    category_id: str
    quarters: int


class RankEntryView(Outgoing):
    candidate_id: str
    name: str
    emoji: str
    score: float | None
    count: int
    position: int | None


class CategoryResultView(Outgoing):
    category_id: str
    emoji: str
    name: str
    entries: list[RankEntryView]


class ResultsView(Outgoing):
    overall: list[RankEntryView]
    by_category: list[CategoryResultView]


class StartCheck(Outgoing):
    ready: bool
    missing: list[StartRequirement]


class Me(Outgoing):
    participant_id: str
    is_admin: bool
    progress: Progress


class RoomSnapshot(Outgoing):
    code: str
    version: int
    title: str
    phase: Phase
    me: Me
    participants: list[ParticipantView]
    categories: list[CategoryView]
    my_scores: list[ScoreView]
    proxy_scores: list[ScoreView]
    results: ResultsView | None
    start_check: StartCheck
