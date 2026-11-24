"""specs/participants."""

from cuadrillapp.domain.apply import join_room
from cuadrillapp.domain.effects import SeatReleased
from cuadrillapp.domain.errors import DomainError
from cuadrillapp.protocol import commands as c
from factories import NOW, applied, fails, new_room, run, score, voting_room


def test_duplicate_name() -> None:
    room, _ = new_room("Dani")
    outcome = join_room(
        room, cmd=c.RoomJoin(code=room.code, name=" dáni ", emoji="🐸"), token="t" * 8, now=NOW
    )
    assert isinstance(outcome, DomainError)
    assert outcome.code == "NAME_TAKEN"


def test_same_emoji_is_allowed() -> None:
    room, ids = new_room("Ana", "Leo")
    assert room.participants[ids["Ana"]].emoji == room.participants[ids["Leo"]].emoji


def test_emoji_must_come_from_the_curated_list() -> None:
    outcome = join_room(
        new_room("Ana")[0],
        cmd=c.RoomJoin(code="ABCDE", name="Leo", emoji="X"),
        token="t" * 8,
        now=NOW,
    )
    assert isinstance(outcome, DomainError)


def test_role_change_in_lobby() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Leo"], c.ParticipantUpdate(role="voter"))
    assert room.participants[ids["Leo"]].role == "voter"
    assert [p.name for p in room.candidates()] == ["Ana"]


def test_role_locked_during_voting() -> None:
    room, ids = voting_room()
    assert fails(room, ids["Leo"], c.ParticipantUpdate(role="voter")) == "WRONG_PHASE"


def test_admin_changes_someone_elses_role_but_not_their_name() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.ParticipantUpdate(participant_id=ids["Leo"], role="voter"))
    assert room.participants[ids["Leo"]].role == "voter"
    cmd = c.ParticipantUpdate(participant_id=ids["Leo"], name="Leonardo")
    assert fails(room, ids["Ana"], cmd) == "FORBIDDEN"
    cmd = c.ParticipantUpdate(participant_id=ids["Ana"], role="voter")
    assert fails(room, ids["Leo"], cmd) == "FORBIDDEN"


def test_late_candidate() -> None:
    room, _ = voting_room()
    outcome = join_room(
        room, cmd=c.RoomJoin(code=room.code, name="Latecomer", emoji="🐸"), token="t" * 8, now=NOW
    )
    assert not isinstance(outcome, DomainError)
    assert "Latecomer" in [p.name for p in outcome.room.candidates()]


def test_add_friend_without_phone() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.ManualAdd(name="Grandma", emoji="🧙", role="candidate"))
    grandma = next(p for p in room.participants.values() if p.name == "Grandma")
    assert grandma.is_manual
    assert not grandma.connected
    assert grandma in room.candidates()
    assert fails(room, ids["Leo"], c.ManualAdd(name="Uncle", emoji="🧙")) == "FORBIDDEN"


def test_leave_during_voting_discards_scores() -> None:
    room, ids = voting_room()
    room = score(room, ids["Ana"], ids["Leo"], "c1", 20)
    room = score(room, ids["Leo"], ids["Sara"], "c1", 30)
    outcome = applied(room, ids["Leo"], c.RoomLeave())
    assert ids["Leo"] not in outcome.room.participants
    assert outcome.room.scores == {}
    assert SeatReleased(ids["Leo"], kicked=False) in outcome.effects


def test_kick() -> None:
    room, ids = new_room("Ana", "Leo")
    outcome = applied(room, ids["Ana"], c.ParticipantKick(participant_id=ids["Leo"]))
    assert ids["Leo"] not in outcome.room.participants
    assert SeatReleased(ids["Leo"], kicked=True) in outcome.effects


def test_admin_can_kick_another_admin_but_not_themselves() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.AdminSet(participant_id=ids["Leo"], is_admin=True))
    room = run(room, ids["Leo"], c.ParticipantKick(participant_id=ids["Ana"]))
    assert ids["Ana"] not in room.participants
    assert fails(room, ids["Leo"], c.ParticipantKick(participant_id=ids["Leo"])) == "FORBIDDEN"


def test_non_admin_cannot_kick() -> None:
    room, ids = new_room("Ana", "Leo")
    assert fails(room, ids["Leo"], c.ParticipantKick(participant_id=ids["Ana"])) == "FORBIDDEN"
