"""specs/room-admin."""

from cuadrillapp.domain.apply import rejoin_room
from cuadrillapp.domain.effects import Applied, Disconnect, GraceExpired
from cuadrillapp.protocol import commands as c
from factories import NOW, fails, new_room, run


def test_accion_sin_permiso() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.CategoryAdd(emoji="😂", name="Gracioso"))
    assert fails(room, ids["Leo"], c.VotingStart()) == "FORBIDDEN"
    assert room.phase == "lobby"


def test_conceder_admin() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.AdminSet(participant_id=ids["Leo"], is_admin=True))
    assert room.participants[ids["Leo"]].is_admin


def test_participante_manual_cannot_be_admin() -> None:
    room, ids = new_room("Ana")
    room = run(room, ids["Ana"], c.ManualAdd(name="Abuela", emoji="🧙"))
    abuela = next(p.id for p in room.participants.values() if p.is_manual)
    assert fails(room, ids["Ana"], c.AdminSet(participant_id=abuela, is_admin=True)) == "NOT_MANUAL"


def test_ultimo_admin() -> None:
    room, ids = new_room("Ana", "Leo")
    cmd = c.AdminSet(participant_id=ids["Ana"], is_admin=False)
    assert fails(room, ids["Ana"], cmd) == "LAST_ADMIN"


def test_admin_can_step_down_when_others_remain() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.AdminSet(participant_id=ids["Leo"], is_admin=True))
    room = run(room, ids["Ana"], c.AdminSet(participant_id=ids["Ana"], is_admin=False))
    assert not room.participants[ids["Ana"]].is_admin


def test_el_admin_sale() -> None:
    room, ids = new_room("Ana", "Leo", "Sara")
    room = run(room, ids["Ana"], c.RoomLeave())
    assert room.participants[ids["Leo"]].is_admin
    assert not room.participants[ids["Sara"]].is_admin


def test_el_admin_pierde_la_conexion_un_momento() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], Disconnect())
    assert not room.participants[ids["Leo"]].is_admin


def test_el_admin_tarda_en_volver() -> None:
    room, ids = new_room("Ana", "Leo", "Sara")
    room = run(room, ids["Ana"], Disconnect())
    room = run(room, ids["Ana"], GraceExpired(), now=NOW + 61)
    assert room.participants[ids["Leo"]].is_admin
    assert not room.participants[ids["Sara"]].is_admin
    assert room.participants[ids["Ana"]].is_admin  # conserva su permiso al volver


def test_grace_does_not_expire_if_admin_came_back() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], Disconnect())
    room.participants[ids["Ana"]].connected = True  # volvió (rejoin)
    room = run(room, ids["Ana"], GraceExpired())
    assert not room.participants[ids["Leo"]].is_admin


def test_nadie_con_movil_conectado() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Leo"], Disconnect())
    room = run(room, ids["Leo"], GraceExpired())
    room = run(room, ids["Ana"], c.RoomLeave())
    assert not any(p.is_admin for p in room.participants.values())
    # Leo vuelve: la sucesión se aplica en cuanto alguien se conecta
    outcome = rejoin_room(room, token="token-0", now=NOW + 120)
    assert isinstance(outcome, Applied)
    assert outcome.room.participants[ids["Leo"]].is_admin
