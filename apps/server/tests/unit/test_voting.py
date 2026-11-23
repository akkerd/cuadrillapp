"""specs/voting."""

from cuadrillapp.constants import CATEGORY_SUGGESTIONS, MAX_CATEGORIES
from cuadrillapp.domain.projection import progress_of
from cuadrillapp.protocol import commands as c
from factories import fails, new_room, run, score, voting_room


def test_anadir_categoria_sugerida() -> None:
    emoji, name = CATEGORY_SUGGESTIONS[0]
    room, ids = new_room("Ana")
    room = run(room, ids["Ana"], c.CategoryAdd(emoji=emoji, name=name))
    assert [(cat.emoji, cat.name) for cat in room.categories] == [("😂", "Gracioso")]


def test_categories_can_be_edited_reordered_and_deleted() -> None:
    room, ids = new_room("Ana")
    admin = ids["Ana"]
    room = run(room, admin, c.CategoryAdd(emoji="😂", name="Gracioso"))
    room = run(room, admin, c.CategoryAdd(emoji="👗", name="Estilo"))
    room = run(room, admin, c.CategoryMove(category_id="c2", direction=-1))
    assert [cat.id for cat in room.categories] == ["c2", "c1"]
    room = run(room, admin, c.CategoryUpdate(category_id="c1", emoji="🤣", name="Risas"))
    assert room.category("c1") is not None
    room = run(room, admin, c.CategoryDelete(category_id="c2"))
    assert [cat.name for cat in room.categories] == ["Risas"]


def test_category_limit() -> None:
    room, ids = new_room("Ana")
    for i in range(MAX_CATEGORIES):
        room = run(room, ids["Ana"], c.CategoryAdd(emoji="⭐", name=f"Cat {i}"))
    assert (
        fails(room, ids["Ana"], c.CategoryAdd(emoji="⭐", name="Una más")) == "TOO_MANY_CATEGORIES"
    )


def test_categorias_bloqueadas() -> None:
    room, ids = voting_room()
    assert fails(room, ids["Ana"], c.CategoryAdd(emoji="⭐", name="Otra")) == "WRONG_PHASE"
    assert fails(room, ids["Ana"], c.CategoryDelete(category_id="c1")) == "WRONG_PHASE"


def test_empezar_sin_categorias() -> None:
    room, ids = new_room("Ana", "Leo")
    assert room.start_missing() == ["categories"]
    assert fails(room, ids["Ana"], c.VotingStart()) == "START_REQUIREMENTS"


def test_start_requires_two_participants_and_a_candidate() -> None:
    room, ids = new_room("Ana")
    room = run(room, ids["Ana"], c.ParticipantUpdate(role="voter"))
    room = run(room, ids["Ana"], c.CategoryAdd(emoji="😂", name="Gracioso"))
    assert room.start_missing() == ["candidates", "participants"]


def test_empezar_la_votacion() -> None:
    room, _ = voting_room()
    assert room.phase == "voting"


def test_nota_valida() -> None:
    room, ids = voting_room()
    room = score(room, ids["Leo"], ids["Sara"], "c1", 29)
    assert room.scores[(ids["Leo"], ids["Sara"], "c1")] == 29


def test_sin_autovoto() -> None:
    room, ids = voting_room()
    cmd = c.ScoreSet(candidate_id=ids["Leo"], category_id="c1", quarters=40)
    assert fails(room, ids["Leo"], cmd) == "SELF_VOTE"


def test_cannot_score_voters_or_unknown_categories() -> None:
    room, ids = voting_room("Leo", ("Vera", "voter"))
    cmd = c.ScoreSet(candidate_id=ids["Vera"], category_id="c1", quarters=10)
    assert fails(room, ids["Leo"], cmd) == "NOT_CANDIDATE"
    cmd = c.ScoreSet(candidate_id=ids["Ana"], category_id="c9", quarters=10)
    assert fails(room, ids["Leo"], cmd) == "NOT_FOUND"


def test_cambiar_de_opinion_and_clear() -> None:
    room, ids = voting_room()
    room = score(room, ids["Leo"], ids["Sara"], "c1", 24)
    room = score(room, ids["Leo"], ids["Sara"], "c1", 34)
    assert room.scores[(ids["Leo"], ids["Sara"], "c1")] == 34
    room = score(room, ids["Leo"], ids["Sara"], "c1", None)
    assert (ids["Leo"], ids["Sara"], "c1") not in room.scores


def test_votacion_cerrada() -> None:
    room, ids = voting_room()
    room = run(room, ids["Ana"], c.VotingReveal())
    cmd = c.ScoreSet(candidate_id=ids["Sara"], category_id="c1", quarters=10)
    assert fails(room, ids["Leo"], cmd) == "WRONG_PHASE"


def test_admin_vota_por_la_abuela() -> None:
    room, ids = new_room("Ana", "Leo")
    room = run(room, ids["Ana"], c.ManualAdd(name="Abuela", emoji="🧙"))
    abuela = next(p.id for p in room.participants.values() if p.is_manual)
    room = run(room, ids["Ana"], c.CategoryAdd(emoji="😂", name="Gracioso"))
    room = run(room, ids["Ana"], c.VotingStart())
    as_abuela = c.ScoreSet(
        candidate_id=ids["Leo"], category_id="c1", quarters=40, as_participant_id=abuela
    )
    room = run(room, ids["Ana"], as_abuela)
    assert room.scores[(abuela, ids["Leo"], "c1")] == 40
    self_vote = c.ScoreSet(
        candidate_id=abuela, category_id="c1", quarters=40, as_participant_id=abuela
    )
    assert fails(room, ids["Ana"], self_vote) == "SELF_VOTE"


def test_proxy_voting_rules() -> None:
    room, ids = voting_room()
    as_leo = c.ScoreSet(
        candidate_id=ids["Sara"], category_id="c1", quarters=4, as_participant_id=ids["Leo"]
    )
    assert fails(room, ids["Ana"], as_leo) == "NOT_MANUAL"
    as_ana = c.ScoreSet(
        candidate_id=ids["Sara"], category_id="c1", quarters=4, as_participant_id=ids["Ana"]
    )
    assert fails(room, ids["Leo"], as_ana) == "FORBIDDEN"


def test_marcar_listo_and_progress() -> None:
    room, ids = voting_room()
    room = score(room, ids["Leo"], ids["Sara"], "c1", 20)
    progress = progress_of(room, ids["Leo"])
    assert (progress.given, progress.total) == (1, 4)  # 2 concursantes × 2 categorías
    room = run(room, ids["Leo"], c.VoterDone(done=True))
    assert room.participants[ids["Leo"]].done


def test_start_resets_done_flags() -> None:
    room, ids = voting_room()
    room = run(room, ids["Leo"], c.VoterDone(done=True))
    room = run(room, ids["Ana"], c.VotingReveal())
    room = run(room, ids["Ana"], c.RoundNew())
    room = run(room, ids["Ana"], c.VotingStart())
    assert not room.participants[ids["Leo"]].done
