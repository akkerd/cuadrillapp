"""Projection and domain purity."""

import ast
from pathlib import Path

from cuadrillapp.domain.projection import project_snapshot
from cuadrillapp.protocol import commands as c
from factories import new_room, run


def test_snapshot_lists_participants_for_each_viewer() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.ManualAdd(name="Grandma", emoji="🧙"))
    snapshot = project_snapshot(room, ids["Leo"])
    assert [p.name for p in snapshot.participants] == ["Ana", "Leo", "Grandma"]
    assert snapshot.me.participant_id == ids["Leo"]
    assert not snapshot.me.is_admin
    assert snapshot.participants[0].is_admin
    assert snapshot.participants[2].is_manual


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
