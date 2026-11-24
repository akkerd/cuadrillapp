"""Domain errors. Codes are sent to the client as they are."""

from dataclasses import dataclass
from typing import Literal

ErrorCode = Literal[
    "INVALID",
    "RATE_LIMITED",
    "ROOM_NOT_FOUND",
    "ROOM_FULL",
    "TOO_MANY_ROOMS",
    "NOT_IN_ROOM",
    "BAD_TOKEN",
    "NAME_TAKEN",
    "FORBIDDEN",
    "NOT_FOUND",
    "NOT_MANUAL",
    "LAST_ADMIN",
]


@dataclass(frozen=True, slots=True)
class DomainError:
    code: ErrorCode
