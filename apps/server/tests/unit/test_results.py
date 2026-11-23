"""specs/results."""

from fractions import Fraction

from cuadrillapp.domain.results import compute_results
from cuadrillapp.protocol import commands as c
from factories import run, score, voting_room


def test_media_simple() -> None:
    room, ids = voting_room("Leo", "Sara", "Vera")
    room = score(room, ids["Ana"], ids["Leo"], "c1", 24)  # 6,00
    room = score(room, ids["Sara"], ids["Leo"], "c1", 30)  # 7,50
    room = score(room, ids["Vera"], ids["Leo"], "c1", 36)  # 9,00
    category = compute_results(room).by_category[0]
    leo = next(e for e in category.entries if e.candidate_id == ids["Leo"])
    assert leo.score == Fraction(15, 2)
    assert leo.count == 3


def test_nota_final_con_dos_categorias() -> None:
    room, ids = voting_room()
    room = score(room, ids["Ana"], ids["Leo"], "c1", 30)  # 7,50
    room = score(room, ids["Ana"], ids["Leo"], "c2", 34)  # 8,50
    leo = next(e for e in compute_results(room).overall if e.candidate_id == ids["Leo"])
    assert leo.score == Fraction(8)


def test_final_ignores_categories_without_votes() -> None:
    room, ids = voting_room()
    room = score(room, ids["Ana"], ids["Leo"], "c1", 30)
    leo = next(e for e in compute_results(room).overall if e.candidate_id == ids["Leo"])
    assert leo.score == Fraction(15, 2)


def test_concursante_sin_votos() -> None:
    room, ids = voting_room()
    room = score(room, ids["Ana"], ids["Leo"], "c1", 4)
    overall = compute_results(room).overall
    assert overall[-1].candidate_id == ids["Sara"]
    assert overall[-1].score is None
    assert overall[-1].position is None


def test_empate_en_primera_posicion() -> None:
    room, ids = voting_room("Leo", "Sara", "Vera")
    room = score(room, ids["Ana"], ids["Leo"], "c1", 36)
    room = score(room, ids["Ana"], ids["Sara"], "c1", 36)
    room = score(room, ids["Ana"], ids["Vera"], "c1", 20)
    positions = {e.candidate_id: e.position for e in compute_results(room).overall}
    assert positions[ids["Leo"]] == 1
    assert positions[ids["Sara"]] == 1
    assert positions[ids["Vera"]] == 3


def test_ties_compare_exact_values() -> None:
    # 1/3 + 2/3 de puntos frente a 0,50: comparación exacta, sin redondeos intermedios
    room, ids = voting_room("Leo", "Sara", "Vera")
    room = score(room, ids["Ana"], ids["Leo"], "c1", 1)
    room = score(room, ids["Sara"], ids["Leo"], "c1", 1)
    room = score(room, ids["Vera"], ids["Leo"], "c1", 2)  # media 1/3 de punto
    room = score(room, ids["Ana"], ids["Sara"], "c1", 1)  # 0,25
    overall = compute_results(room).overall
    assert [e.candidate_id for e in overall[:2]] == [ids["Leo"], ids["Sara"]]
    assert overall[0].position == 1
    assert overall[1].position == 2


def test_revelar_freezes_results() -> None:
    room, ids = voting_room()
    room = score(room, ids["Ana"], ids["Leo"], "c1", 20)
    room = run(room, ids["Ana"], c.VotingReveal())
    assert room.phase == "results"
    assert room.results is not None


def test_reabrir() -> None:
    room, ids = voting_room()
    room = score(room, ids["Ana"], ids["Leo"], "c1", 20)
    room = run(room, ids["Ana"], c.VotingReveal())
    room = run(room, ids["Ana"], c.VotingReopen())
    assert room.phase == "voting"
    assert room.results is None
    assert room.scores == {(ids["Ana"], ids["Leo"], "c1"): 20}


def test_nueva_ronda() -> None:
    room, ids = voting_room()
    room = score(room, ids["Ana"], ids["Leo"], "c1", 20)
    room = run(room, ids["Ana"], c.VotingReveal())
    room = run(room, ids["Ana"], c.RoundNew())
    assert room.phase == "lobby"
    assert room.scores == {}
    assert len(room.categories) == 2
    assert len(room.participants) == 3
