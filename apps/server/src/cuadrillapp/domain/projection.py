"""Room view for one specific participant."""

from cuadrillapp.domain.models import Participant, Room
from cuadrillapp.protocol.snapshot import Me, ParticipantView, RoomSnapshot


def project_snapshot(room: Room, viewer_id: str) -> RoomSnapshot:
    viewer = room.participants[viewer_id]
    return RoomSnapshot(
        code=room.code,
        version=room.version,
        title=room.title,
        phase=room.phase,
        me=Me(participant_id=viewer.id, is_admin=viewer.is_admin),
        participants=[_participant(p) for p in room.ordered_participants()],
    )


def _participant(p: Participant) -> ParticipantView:
    return ParticipantView(
        id=p.id,
        name=p.name,
        emoji=p.emoji,
        role=p.role,
        is_admin=p.is_admin,
        is_manual=p.is_manual,
        connected=p.connected,
    )
