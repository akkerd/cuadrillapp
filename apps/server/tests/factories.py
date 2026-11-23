"""Atajos para construir salas en tests de dominio."""

from cuadrillapp.domain.apply import apply_command, create_room, join_room
from cuadrillapp.domain.effects import Applied, Disconnect, GraceExpired
from cuadrillapp.domain.errors import DomainError, ErrorCode
from cuadrillapp.domain.models import Role, Room
from cuadrillapp.protocol import commands as c
from cuadrillapp.protocol.results import JoinResult

NOW = 1_000.0
EMOJI = "🦄"


def new_room(admin: str = "Ana", *others: str | tuple[str, Role]) -> tuple[Room, dict[str, str]]:
    """Crea una sala con `admin` y une a `others`. Devuelve la sala y nombre → id."""
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


def voting_room(*others: str | tuple[str, Role]) -> tuple[Room, dict[str, str]]:
    """Sala ya en votación con dos categorías (c1 Gracioso, c2 Estilo)."""
    room, ids = new_room("Ana", *(others or ("Leo", "Sara")))
    admin = ids["Ana"]
    room = run(room, admin, c.CategoryAdd(emoji="😂", name="Gracioso"))
    room = run(room, admin, c.CategoryAdd(emoji="👗", name="Estilo"))
    room = run(room, admin, c.VotingStart())
    return room, ids


def score(room: Room, voter: str, candidate: str, category: str, quarters: int | None) -> Room:
    return run(
        room,
        voter,
        c.ScoreSet(candidate_id=candidate, category_id=category, quarters=quarters),
    )
