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
    "WRONG_PHASE",
    "NOT_FOUND",
    "NOT_CANDIDATE",
    "NOT_MANUAL",
    "SELF_VOTE",
    "LAST_ADMIN",
    "TOO_MANY_CATEGORIES",
    "START_REQUIREMENTS",
]


@dataclass(frozen=True, slots=True)
class DomainError:
    code: ErrorCode
