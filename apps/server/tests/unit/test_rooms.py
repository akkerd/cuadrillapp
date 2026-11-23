"""specs/rooms (parte de dominio)."""

from cuadrillapp.constants import MAX_PARTICIPANTS
from cuadrillapp.domain.apply import join_room, rejoin_room
from cuadrillapp.domain.effects import Applied, Disconnect
from cuadrillapp.domain.errors import DomainError
from cuadrillapp.protocol import commands as c
from cuadrillapp.protocol.results import RejoinResult
from factories import NOW, fails, join, new_room, run


def test_creacion_correcta_creator_is_admin_in_lobby() -> None:
    room, ids = new_room("Ana")
    creator = room.participants[ids["Ana"]]
    assert room.phase == "lobby"
    assert creator.is_admin
    assert creator.connected


def test_admin_cambia_el_titulo() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.TitleSet(title="  Halloween   🎃 "))
    assert room.title == "Halloween 🎃"
    assert fails(room, ids["Leo"], c.TitleSet(title="Mío")) == "FORBIDDEN"


def test_sala_llena() -> None:
    room, _ = new_room("Ana")
    for i in range(MAX_PARTICIPANTS - 1):
        room, _ = join(room, f"Jugador {i}")
    outcome = join_room(
        room, cmd=c.RoomJoin(code=room.code, name="Tarde", emoji="🦄"), token="t" * 8, now=NOW
    )
    assert isinstance(outcome, DomainError)
    assert outcome.code == "ROOM_FULL"


def test_recarga_de_la_pagina_recovers_the_same_seat() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Leo"], Disconnect())
    assert not room.participants[ids["Leo"]].connected
    outcome = rejoin_room(room, token="token-0", now=NOW)
    assert isinstance(outcome, Applied)
    leo = outcome.room.participants[ids["Leo"]]
    assert leo.connected
    assert isinstance(outcome.data, RejoinResult)
    assert outcome.data.participant_id == ids["Leo"]


def test_rejoin_with_unknown_token_fails() -> None:
    room, _ = new_room("Ana")
    outcome = rejoin_room(room, token="nope-nope", now=NOW)
    assert isinstance(outcome, DomainError)
    assert outcome.code == "BAD_TOKEN"


def test_room_tracks_when_it_became_empty() -> None:
    room, ids = new_room("Ana")
    assert room.empty_since is None
    room = run(room, ids["Ana"], Disconnect(), now=NOW + 5)
    assert room.empty_since == NOW + 5


def test_every_change_bumps_the_version() -> None:
    room, ids = new_room("Ana")
    before = room.version
    room = run(room, ids["Ana"], c.TitleSet(title="Otra"))
    assert room.version == before + 1


def test_failed_commands_do_not_change_the_room() -> None:
    room, ids = new_room("Ana", "Leo")
    snapshot = (room.title, room.version)
    assert fails(room, ids["Leo"], c.TitleSet(title="X")) == "FORBIDDEN"
    assert (room.title, room.version) == snapshot
