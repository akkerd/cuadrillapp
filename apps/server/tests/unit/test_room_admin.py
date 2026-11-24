"""specs/room-admin."""

from cuadrillapp.domain.apply import rejoin_room
from cuadrillapp.domain.effects import Applied, Disconnect, GraceExpired
from cuadrillapp.protocol import commands as c
from factories import NOW, fails, new_room, run


def test_action_without_permission() -> None:
    room, ids = new_room("Ana", "Leo")
    assert fails(room, ids["Leo"], c.ManualAdd(name="Uncle", emoji="🧙")) == "FORBIDDEN"
    assert len(room.participants) == 2


def test_grant_admin() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.AdminSet(participant_id=ids["Leo"], is_admin=True))
    assert room.participants[ids["Leo"]].is_admin


def test_manual_participant_cannot_be_admin() -> None:
    room, ids = new_room("Ana")
    room = run(room, ids["Ana"], c.ManualAdd(name="Grandma", emoji="🧙"))
    grandma = next(p.id for p in room.participants.values() if p.is_manual)
    assert (
        fails(room, ids["Ana"], c.AdminSet(participant_id=grandma, is_admin=True)) == "NOT_MANUAL"
    )


def test_last_admin() -> None:
    room, ids = new_room("Ana", "Leo")
    cmd = c.AdminSet(participant_id=ids["Ana"], is_admin=False)
    assert fails(room, ids["Ana"], cmd) == "LAST_ADMIN"


def test_admin_can_step_down_when_others_remain() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.AdminSet(participant_id=ids["Leo"], is_admin=True))
    room = run(room, ids["Ana"], c.AdminSet(participant_id=ids["Ana"], is_admin=False))
    assert not room.participants[ids["Ana"]].is_admin


def test_the_admin_leaves() -> None:
    room, ids = new_room("Ana", "Leo", "Sara")
    room = run(room, ids["Ana"], c.RoomLeave())
    assert room.participants[ids["Leo"]].is_admin
    assert not room.participants[ids["Sara"]].is_admin


def test_admin_briefly_loses_connection() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], Disconnect())
    assert not room.participants[ids["Leo"]].is_admin


def test_admin_takes_too_long_to_return() -> None:
    room, ids = new_room("Ana", "Leo", "Sara")
    room = run(room, ids["Ana"], Disconnect())
    room = run(room, ids["Ana"], GraceExpired(), now=NOW + 61)
    assert room.participants[ids["Leo"]].is_admin
    assert not room.participants[ids["Sara"]].is_admin
    assert room.participants[ids["Ana"]].is_admin  # keeps the permission after coming back


def test_grace_does_not_expire_if_admin_came_back() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], Disconnect())
    room.participants[ids["Ana"]].connected = True  # came back (rejoin)
    room = run(room, ids["Ana"], GraceExpired())
    assert not room.participants[ids["Leo"]].is_admin


def test_nobody_with_a_phone_connected() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Leo"], Disconnect())
    room = run(room, ids["Leo"], GraceExpired())
    room = run(room, ids["Ana"], c.RoomLeave())
    assert not any(p.is_admin for p in room.participants.values())
    # Leo comes back: succession applies as soon as someone connects
    outcome = rejoin_room(room, token="token-0", now=NOW + 120)
    assert isinstance(outcome, Applied)
    assert outcome.room.participants[ids["Leo"]].is_admin
