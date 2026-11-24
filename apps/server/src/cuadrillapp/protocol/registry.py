"""Event map: source of truth for the server and for the frontend types."""

from pydantic import BaseModel

from cuadrillapp.protocol import commands as c
from cuadrillapp.protocol.results import (
    JoinResult,
    KickedEvent,
    PeekResult,
    RejoinResult,
    ReplacedEvent,
)
from cuadrillapp.protocol.snapshot import RoomSnapshot

# event → (payload model, model of the ack's `data`, or None)
COMMANDS: dict[str, tuple[type[c.Command], type[BaseModel] | None]] = {
    "room:create": (c.RoomCreate, JoinResult),
    "room:peek": (c.RoomPeek, PeekResult),
    "room:join": (c.RoomJoin, JoinResult),
    "room:rejoin": (c.RoomRejoin, RejoinResult),
    "room:leave": (c.RoomLeave, None),
    "room:title": (c.TitleSet, None),
    "participant:update": (c.ParticipantUpdate, None),
    "participant:kick": (c.ParticipantKick, None),
    "admin:set": (c.AdminSet, None),
    "manual:add": (c.ManualAdd, None),
    "category:add": (c.CategoryAdd, None),
    "category:update": (c.CategoryUpdate, None),
    "category:delete": (c.CategoryDelete, None),
    "category:move": (c.CategoryMove, None),
    "voting:start": (c.VotingStart, None),
    "score:set": (c.ScoreSet, None),
    "voter:done": (c.VoterDone, None),
}

# server → client event → model
SERVER_EVENTS: dict[str, type[BaseModel]] = {
    "room:state": RoomSnapshot,
    "room:kicked": KickedEvent,
    "room:replaced": ReplacedEvent,
}
