"""Response format for every command: {ok: true, data} | {ok: false, error}."""

from pydantic import BaseModel

from cuadrillapp.domain.errors import ErrorCode

type AckPayload = dict[str, object]


def ack_ok(data: BaseModel | None = None) -> AckPayload:
    return {"ok": True, "data": None if data is None else data.model_dump(mode="json")}


def ack_error(code: ErrorCode) -> AckPayload:
    return {"ok": False, "error": code}
