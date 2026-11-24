import pytest
from pydantic import ValidationError

from cuadrillapp.protocol import commands as c
from cuadrillapp.protocol.snapshot import Me


def test_commands_accept_camel_case_payloads() -> None:
    cmd = c.AdminSet.model_validate({"participantId": "p2", "isAdmin": True})
    assert cmd.is_admin


@pytest.mark.parametrize(
    "payload",
    [
        {"participantId": "p2", "isAdmin": "yes"},
        {"participantId": "p2!", "isAdmin": True},
        {"participantId": "p2", "isAdmin": True, "extra": 1},
        {"isAdmin": True},
    ],
)
def test_invalid_payloads_are_rejected(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        c.AdminSet.model_validate(payload)


def test_profile_rejects_overlong_names() -> None:
    with pytest.raises(ValidationError):
        c.RoomCreate.model_validate({"name": "x" * 17, "emoji": "🦄"})


def test_role_defaults_to_candidate() -> None:
    assert c.RoomCreate.model_validate({"name": "Ana", "emoji": "🦄"}).role == "candidate"


def test_outgoing_models_serialize_in_camel_case() -> None:
    assert Me(participant_id="p1", is_admin=True).model_dump() == {
        "participantId": "p1",
        "isAdmin": True,
    }
