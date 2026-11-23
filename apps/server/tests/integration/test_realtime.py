"""Comportamiento en tiempo real con clientes Socket.IO reales."""

import asyncio
from typing import Any

from conftest import Live, Player, profile


def names(state: dict[str, Any]) -> list[str]:
    return [p["name"] for p in state["participants"]]


async def room_with(live: Live, *others: str) -> tuple[str, Player, list[Player]]:
    admin = await live.player()
    created = await admin.ok("room:create", profile("Ana"))
    players = []
    for name in others:
        player = await live.player()
        await player.ok("room:join", {**profile(name), "code": created["code"]})
        players.append(player)
    return created["code"], admin, players


async def test_llega_un_participante_nuevo(live: Live) -> None:
    code, admin, _ = await room_with(live)
    leo = await live.player()
    await leo.ok("room:join", {**profile("Leo"), "code": code.lower()})
    state = await admin.wait_for(lambda s: "Leo" in names(s))
    assert names(state) == ["Ana", "Leo"]


async def test_codigo_inexistente(live: Live) -> None:
    player = await live.player()
    result = await player.call("room:join", {**profile("Leo"), "code": "ZZZZZ"})
    assert result == {"ok": False, "error": "ROOM_NOT_FOUND"}


async def test_peek_reports_title_and_phase(live: Live) -> None:
    code, _, _ = await room_with(live)
    visitor = await live.player()
    data = await visitor.ok("room:peek", {"code": f" {code.lower()} "})
    assert data == {"code": code, "title": "Concurso", "phase": "lobby", "full": False}


async def test_datos_invalidos_no_cambian_la_sala(live: Live) -> None:
    code, admin, _ = await room_with(live, "Leo")
    before = (await admin.wait_for(lambda s: "Leo" in names(s)))["version"]
    result = await admin.call("room:title", {"title": 123})
    assert result == {"ok": False, "error": "INVALID"}
    assert live.hub.store.get(code).version == before  # type: ignore[union-attr]


async def test_notas_ajenas_nunca_salen_del_servidor(live: Live) -> None:
    _, admin, (leo, sara) = await room_with(live, "Leo", "Sara")
    await admin.ok("category:add", {"emoji": "😂", "name": "Gracioso"})
    await admin.ok("voting:start")
    sara_id = sara.state["me"]["participantId"]  # type: ignore[index]
    await leo.ok("score:set", {"candidateId": sara_id, "categoryId": "c1", "quarters": 29})
    admin_state = await admin.wait_for(lambda s: s["phase"] == "voting")
    leo_state = await leo.wait_for(lambda s: len(s["myScores"]) == 1)
    assert admin_state["myScores"] == []
    assert leo_state["myScores"][0]["quarters"] == 29
    sara_state = await sara.wait_for(lambda s: s["phase"] == "voting")
    assert sara_state["myScores"] == []
    assert sara_state["proxyScores"] == []


async def test_reconexion_recupera_la_plaza(live: Live) -> None:
    code, admin, (leo,) = await room_with(live, "Leo")
    token_state = await leo.wait_for(lambda s: s["code"] == code)
    leo_id = token_state["me"]["participantId"]
    seat = live.hub.store.get(code).participants[leo_id]  # type: ignore[union-attr]
    token = seat.rejoin_token
    await leo.close()
    await admin.wait_for(
        lambda s: any(p["id"] == leo_id and not p["connected"] for p in s["participants"])
    )
    again = await live.player()
    data = await again.ok("room:rejoin", {"code": code, "token": token})
    assert data == {"participantId": leo_id}
    await admin.wait_for(
        lambda s: any(p["id"] == leo_id and p["connected"] for p in s["participants"])
    )


async def test_sucesion_de_admin_tras_la_gracia(live: Live) -> None:
    _, admin, (leo, _) = await room_with(live, "Leo", "Sara")
    await admin.close()
    await leo.wait_for(lambda s: not s["participants"][0]["connected"])
    assert not (await leo.wait_for(lambda s: True))["me"]["isAdmin"]
    await live.scheduler.advance(61)
    state = await leo.wait_for(lambda s: s["me"]["isAdmin"])
    assert state["me"]["isAdmin"]


async def test_expulsion_avisa_al_expulsado(live: Live) -> None:
    _, admin, (leo,) = await room_with(live, "Leo")
    leo_id = (await leo.wait_for(lambda s: True))["me"]["participantId"]
    await admin.ok("participant:kick", {"participantId": leo_id})
    async with asyncio.timeout(3):
        while not any(event == "room:kicked" for event, _ in leo.events):
            await asyncio.sleep(0.02)
    state = await admin.wait_for(lambda s: "Leo" not in names(s))
    assert names(state) == ["Ana"]
    result = await leo.call("room:title", {"title": "hola"})
    assert result == {"ok": False, "error": "NOT_IN_ROOM"}


async def test_concurrent_scores_are_all_kept(live: Live) -> None:
    code, admin, (leo, sara) = await room_with(live, "Leo", "Sara")
    for i in range(4):
        await admin.ok("category:add", {"emoji": "⭐", "name": f"Cat {i}"})
    await admin.ok("voting:start")
    ids = {p["name"]: p["id"] for p in (await admin.wait_for(lambda s: True))["participants"]}
    calls = [
        player.ok("score:set", {"candidateId": target, "categoryId": f"c{cat}", "quarters": 40})
        for player, target in ((leo, ids["Sara"]), (sara, ids["Leo"]), (admin, ids["Leo"]))
        for cat in range(1, 5)
    ]
    await asyncio.gather(*calls)
    assert len(live.hub.store.get(code).scores) == 12  # type: ignore[union-attr]


async def test_rafaga_de_acciones_is_rate_limited(live: Live) -> None:
    live.hub.limiter.capacity = 5
    live.hub.limiter.refill = 0
    _, admin, _ = await room_with(live)
    results = [await admin.call("room:title", {"title": f"T{i}"}) for i in range(10)]
    assert {"ok": False, "error": "RATE_LIMITED"} in results


async def test_sala_abandonada_is_swept(live: Live) -> None:
    code, admin, _ = await room_with(live)
    await admin.close()
    async with asyncio.timeout(3):
        while live.hub.store.get(code).empty_since is None:  # type: ignore[union-attr]
            await asyncio.sleep(0.02)
    live.clock.now += 29 * 60
    assert live.hub.sweep() == []
    live.clock.now += 2 * 60
    assert live.hub.sweep() == [code]
    visitor = await live.player()
    result = await visitor.call("room:rejoin", {"code": code, "token": "whatever-token"})
    assert result == {"ok": False, "error": "ROOM_NOT_FOUND"}
