"""Shortcuts for building rooms in domain tests."""

from cuadrillapp.domain.apply import apply_command, create_room, join_room
from cuadrillapp.domain.effects import Applied, Disconnect, GraceExpired
from cuadrillapp.domain.errors import DomainError, ErrorCode
from cuadrillapp.domain.models import Role, Room
from cuadrillapp.protocol import commands as c
from cuadrillapp.protocol.results import JoinResult

NOW = 1_000.0
EMOJI = "🦄"


def new_room(admin: str = "Ana", *others: str | tuple[str, Role]) -> tuple[Room, dict[str, str]]:
    """Create a room with `admin` and join `others`. Return the room and name → id."""
    outcome = create_room(
        code="ABCDE", cmd=c.RoomCreate(name=admin, emoji=EMOJI), token="token-admin", now=NOW
    )
    assert isinstance(outcome, Applied), outcome
    room = outcome.room
    ids = {admin: "p1"}
    for index, other in enumerate(others):
        name, role = other if isinstance(other, tuple) else (other, "candidate")
        room, pid = join(room, name, role=role, token=f"token-{index}")
        ids[name] = pid
    return room, ids


def join(
    room: Room, name: str, *, role: Role = "candidate", token: str = "token-x"
) -> tuple[Room, str]:
    outcome = join_room(
        room,
        cmd=c.RoomJoin(code=room.code, name=name, emoji=EMOJI, role=role),
        token=token,
        now=NOW,
    )
    assert isinstance(outcome, Applied), outcome
    assert isinstance(outcome.data, JoinResult)
    pid = outcome.data.participant_id
    return outcome.room, pid


def run(
    room: Room, actor: str, cmd: c.Command | Disconnect | GraceExpired, now: float = NOW
) -> Room:
    outcome = apply_command(room, actor, cmd, now)
    assert isinstance(outcome, Applied), outcome
    return outcome.room


def applied(
    room: Room, actor: str, cmd: c.Command | Disconnect | GraceExpired, now: float = NOW
) -> Applied:
    outcome = apply_command(room, actor, cmd, now)
    assert isinstance(outcome, Applied), outcome
    return outcome


def fails(
    room: Room, actor: str, cmd: c.Command | Disconnect | GraceExpired, now: float = NOW
) -> ErrorCode:
    outcome = apply_command(room, actor, cmd, now)
    assert isinstance(outcome, DomainError), outcome
    return outcome.code
