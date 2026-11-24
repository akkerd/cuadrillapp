"""Room view for one specific participant.

Anonymity rule: nobody receives the scores given by other participants with a phone.
Admins also receive each voter's progress and the scores cast on behalf of
manual participants.
"""

from cuadrillapp.domain.models import Participant, RankEntry, Room
from cuadrillapp.protocol.snapshot import (
    CategoryResultView,
    CategoryView,
    Me,
    ParticipantView,
    Progress,
    RankEntryView,
    ResultsView,
    RoomSnapshot,
    ScoreView,
    StartCheck,
)


def progress_of(room: Room, voter_id: str) -> Progress:
    candidates = {p.id for p in room.candidates() if p.id != voter_id}
    categories = {c.id for c in room.categories}
    given = sum(
        1
        for voter, candidate, category in room.scores
        if voter == voter_id and candidate in candidates and category in categories
    )
    return Progress(given=given, total=len(candidates) * len(categories))


def project_snapshot(room: Room, viewer_id: str) -> RoomSnapshot:
    viewer = room.participants[viewer_id]
    manual_ids = {p.id for p in room.participants.values() if p.is_manual}
    return RoomSnapshot(
        code=room.code,
        version=room.version,
        title=room.title,
        phase=room.phase,
        me=Me(
            participant_id=viewer.id,
            is_admin=viewer.is_admin,
            progress=progress_of(room, viewer.id),
        ),
        participants=[_participant(room, p, viewer) for p in room.ordered_participants()],
        categories=[CategoryView(id=c.id, emoji=c.emoji, name=c.name) for c in room.categories],
        my_scores=_scores(room, {viewer.id}),
        proxy_scores=_scores(room, manual_ids) if viewer.is_admin else [],
        results=_results(room),
        start_check=StartCheck(ready=not room.start_missing(), missing=room.start_missing()),
    )


def _participant(room: Room, p: Participant, viewer: Participant) -> ParticipantView:
    sees_progress = viewer.is_admin or viewer.id == p.id
    return ParticipantView(
        id=p.id,
        name=p.name,
        emoji=p.emoji,
        role=p.role,
        is_admin=p.is_admin,
        is_manual=p.is_manual,
        connected=p.connected,
        done=p.done,
        progress=progress_of(room, p.id) if sees_progress else None,
    )


def _scores(room: Room, voters: set[str]) -> list[ScoreView]:
    return [
        ScoreView(voter_id=voter, candidate_id=candidate, category_id=category, quarters=value)
        for (voter, candidate, category), value in room.scores.items()
        if voter in voters
    ]


def _results(room: Room) -> ResultsView | None:
    if room.results is None:
        return None
    return ResultsView(
        overall=[_entry(e) for e in room.results.overall],
        by_category=[
            CategoryResultView(
                category_id=r.category_id,
                emoji=r.emoji,
                name=r.name,
                entries=[_entry(e) for e in r.entries],
            )
            for r in room.results.by_category
        ],
    )


def _entry(entry: RankEntry) -> RankEntryView:
    return RankEntryView(
        candidate_id=entry.candidate_id,
        name=entry.name,
        emoji=entry.emoji,
        score=None if entry.score is None else round(float(entry.score), 4),
        count=entry.count,
        position=entry.position,
    )
