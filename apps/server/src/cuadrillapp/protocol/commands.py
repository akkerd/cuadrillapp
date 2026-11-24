"""Client → server commands. One model per Socket.IO event."""

from typing import Annotated

from pydantic import StringConstraints

from cuadrillapp.constants import (
    EMOJI_MAX_LENGTH,
    NAME_MAX_LENGTH,
    TITLE_MAX_LENGTH,
)
from cuadrillapp.domain.models import Role
from cuadrillapp.protocol.base import Incoming

Id = Annotated[str, StringConstraints(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")]
Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=NAME_MAX_LENGTH)
]
Emoji = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=EMOJI_MAX_LENGTH)
]
Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=TITLE_MAX_LENGTH)
]
RawCode = Annotated[str, StringConstraints(min_length=1, max_length=20)]
Token = Annotated[str, StringConstraints(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")]


class Command(Incoming):
    """Base class for every command."""


class ProfileFields(Command):
    name: Name
    emoji: Emoji
    role: Role = "candidate"


class RoomCreate(ProfileFields):
    pass


class RoomPeek(Command):
    code: RawCode


class RoomJoin(ProfileFields):
    code: RawCode


class RoomRejoin(Command):
    code: RawCode
    token: Token


class RoomLeave(Command):
    pass


class TitleSet(Command):
    title: Title


class ParticipantUpdate(Command):
    """Change my profile or, as an admin, someone's role or a manual participant's profile."""

    participant_id: Id | None = None
    name: Name | None = None
    emoji: Emoji | None = None
    role: Role | None = None


class ParticipantKick(Command):
    participant_id: Id


class AdminSet(Command):
    participant_id: Id
    is_admin: bool


class ManualAdd(ProfileFields):
    pass
