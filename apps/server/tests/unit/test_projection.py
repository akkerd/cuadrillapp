"""Anonymity and domain purity."""

import ast
from pathlib import Path

from cuadrillapp.domain.models import Room
from cuadrillapp.domain.projection import project_snapshot
from cuadrillapp.protocol import commands as c
from factories import new_room, run, score


def _room_with_scores() -> tuple[Room, dict[str, str], str]:
    room, ids = new_room("Ana", "Leo", "Sara")
    admin = ids["Ana"]
    room = run(room, admin, c.ManualAdd(name="Grandma", emoji="🧙"))
    grandma = next(p.id for p in room.participants.values() if p.is_manual)
    room = run(room, admin, c.CategoryAdd(emoji="😂", name="Gracioso"))
    room = run(room, admin, c.VotingStart())
    room = score(room, ids["Leo"], ids["Sara"], "c1", 30)
    room = run(
        room,
        admin,
        c.ScoreSet(
            candidate_id=ids["Sara"], category_id="c1", quarters=8, as_participant_id=grandma
        ),
    )
    return room, ids, grandma


def test_other_players_scores_hidden() -> None:
    room, ids, grandma = _room_with_scores()
    for viewer in ids.values():
        snapshot = project_snapshot(room, viewer)
        assert all(s.voter_id == viewer for s in snapshot.my_scores)
        assert all(s.voter_id == grandma for s in snapshot.proxy_scores)
    admin_view = project_snapshot(room, ids["Ana"])
    assert len(admin_view.proxy_scores) == 1
    assert project_snapshot(room, ids["Sara"]).proxy_scores == []


def test_progress_for_admins() -> None:
    room, ids, _ = _room_with_scores()
    admin_view = project_snapshot(room, ids["Ana"])
    leo = next(p for p in admin_view.participants if p.id == ids["Leo"])
    assert leo.progress is not None
    # Ana, Sara and Grandma (manual, candidate) × 1 category
    assert (leo.progress.given, leo.progress.total) == (1, 3)
    player_view = project_snapshot(room, ids["Sara"])
    leo_for_sara = next(p for p in player_view.participants if p.id == ids["Leo"])
    assert leo_for_sara.progress is None


def test_domain_has_no_io_dependencies() -> None:
    forbidden = {"asyncio", "socketio", "engineio", "fastapi", "starlette", "uvicorn"}
    domain = Path(__file__).parents[2] / "src" / "cuadrillapp" / "domain"
    for path in domain.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert name.split(".")[0] not in forbidden, f"{path.name} imports {name}"
