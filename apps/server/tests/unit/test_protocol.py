import pytest
from pydantic import ValidationError

from cuadrillapp.protocol import commands as c
from cuadrillapp.protocol.snapshot import Progress


def test_commands_accept_camel_case_payloads() -> None:
    cmd = c.ScoreSet.model_validate({"candidateId": "p2", "categoryId": "c1", "quarters": 29})
    assert cmd.quarters == 29


@pytest.mark.parametrize(
    "payload",
    [
        {"candidateId": "p2", "categoryId": "c1", "quarters": 41},  # 10,25
        {"candidateId": "p2", "categoryId": "c1", "quarters": 29.2},  # 7,30
        {"candidateId": "p2", "categoryId": "c1", "quarters": "29"},
        {"candidateId": "p2", "categoryId": "c1", "quarters": 29, "extra": 1},
        {"candidateId": "p2!", "categoryId": "c1", "quarters": 29},
    ],
)
def test_invalid_score_payloads_are_rejected(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        c.ScoreSet.model_validate(payload)


def test_profile_rejects_overlong_names() -> None:
    with pytest.raises(ValidationError):
        c.RoomCreate.model_validate({"name": "x" * 17, "emoji": "🦄"})


def test_role_defaults_to_candidate() -> None:
    assert c.RoomCreate.model_validate({"name": "Ana", "emoji": "🦄"}).role == "candidate"


def test_outgoing_models_serialize_in_camel_case() -> None:
    assert Progress(given=1, total=2).model_dump() == {"given": 1, "total": 2}
    dumped = c.ScoreSet(candidate_id="p2", category_id="c1", quarters=4).model_dump()
    assert "candidateId" in dumped
