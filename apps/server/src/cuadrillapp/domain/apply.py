"""Business rules for a room.

Pure functions: they take the state and return a new state (built on a copy) or an
error. Nothing here does I/O, reads the real clock or knows about Socket.IO.
"""

import copy
import secrets

from cuadrillapp.constants import (
    CATEGORY_NAME_MAX_LENGTH,
    EMOJIS,
    MAX_CATEGORIES,
    MAX_PARTICIPANTS,
    NAME_MAX_LENGTH,
    TITLE_MAX_LENGTH,
)
from cuadrillapp.domain.effects import (
    Applied,
    CancelGrace,
    Disconnect,
    GraceExpired,
    SeatReleased,
    StartGrace,
)
from cuadrillapp.domain.errors import DomainError, ErrorCode
from cuadrillapp.domain.models import Category, Participant, Role, Room
from cuadrillapp.domain.names import clean_display, normalize_name
from cuadrillapp.domain.results import compute_results
from cuadrillapp.protocol import commands as c
from cuadrillapp.protocol.results import JoinResult, RejoinResult

type Outcome = Applied | DomainError


def _err(code: ErrorCode) -> DomainError:
    return DomainError(code)


# --- Entering a room -----------------------------------------------------------------


def create_room(*, code: str, cmd: c.RoomCreate, token: str, now: float) -> Outcome:
    room = Room(code=code, created_at=now)
    created = _add_participant(room, cmd.name, cmd.emoji, cmd.role, manual=False, token=token)
    if isinstance(created, DomainError):
        return created
    created.is_admin = True
    _finalize(room, now)
    return Applied(room, JoinResult(code=code, participant_id=created.id, token=token))


def join_room(room: Room, *, cmd: c.RoomJoin, token: str, now: float) -> Outcome:
    room = copy.deepcopy(room)
    created = _add_participant(room, cmd.name, cmd.emoji, cmd.role, manual=False, token=token)
    if isinstance(created, DomainError):
        return created
    _finalize(room, now)
    return Applied(room, JoinResult(code=room.code, participant_id=created.id, token=token))


def rejoin_room(room: Room, *, token: str, now: float) -> Outcome:
    room = copy.deepcopy(room)
    for participant in room.participants.values():
        stored = participant.rejoin_token
        if stored is not None and secrets.compare_digest(stored, token):
            participant.connected = True
            participant.away = False
            _finalize(room, now)
            return Applied(
                room,
                RejoinResult(participant_id=participant.id),
                (CancelGrace(participant.id),),
            )
    return _err("BAD_TOKEN")


# --- Commands inside a room ----------------------------------------------------------


def apply_command(
    room: Room, actor_id: str, cmd: c.Command | Disconnect | GraceExpired, now: float
) -> Outcome:
    room = copy.deepcopy(room)
    actor = room.participants.get(actor_id)
    if actor is None:
        return _err("NOT_IN_ROOM")
    outcome = _route(room, actor, cmd)
    if isinstance(outcome, DomainError):
        return outcome
    _finalize(room, now)
    return outcome


def _route(room: Room, actor: Participant, cmd: c.Command | Disconnect | GraceExpired) -> Outcome:
    match cmd:
        case Disconnect():
            actor.connected = False
            return Applied(room, effects=(StartGrace(actor.id),))
        case GraceExpired():
            if not actor.connected:
                actor.away = True
            return Applied(room)
        case c.RoomLeave():
            _remove(room, actor.id)
            return Applied(room, effects=(SeatReleased(actor.id, kicked=False),))
        case c.TitleSet():
            return _set_title(room, actor, cmd)
        case c.ParticipantUpdate():
            return _update_participant(room, actor, cmd)
        case c.ParticipantKick():
            return _kick(room, actor, cmd)
        case c.AdminSet():
            return _set_admin(room, actor, cmd)
        case c.ManualAdd():
            return _add_manual(room, actor, cmd)
        case c.CategoryAdd() | c.CategoryUpdate() | c.CategoryDelete() | c.CategoryMove():
            return _edit_categories(room, actor, cmd)
        case c.VotingStart() | c.VotingReveal() | c.VotingReopen() | c.RoundNew():
            return _change_phase(room, actor, cmd)
        case c.ScoreSet():
            return _set_score(room, actor, cmd)
        case c.VoterDone():
            return _set_done(room, actor, cmd)
        case _:
            return _err("INVALID")


def _set_title(room: Room, actor: Participant, cmd: c.TitleSet) -> Outcome:
    if not actor.is_admin:
        return _err("FORBIDDEN")
    title = clean_display(cmd.title)
    if not 1 <= len(title) <= TITLE_MAX_LENGTH:
        return _err("INVALID")
    room.title = title
    return Applied(room)


def _update_participant(room: Room, actor: Participant, cmd: c.ParticipantUpdate) -> Outcome:
    target = room.participants.get(cmd.participant_id or actor.id)
    if target is None:
        return _err("NOT_FOUND")
    is_self = target.id == actor.id
    if not is_self and not actor.is_admin:
        return _err("FORBIDDEN")
    edits_profile = cmd.name is not None or cmd.emoji is not None
    if edits_profile and not is_self and not target.is_manual:
        return _err("FORBIDDEN")
    if cmd.role is not None and cmd.role != target.role and room.phase != "lobby":
        return _err("WRONG_PHASE")
    name = target.name
    if cmd.name is not None:
        validated = _validate_name(room, cmd.name, exclude_id=target.id)
        if isinstance(validated, DomainError):
            return validated
        name = validated
    if cmd.emoji is not None and cmd.emoji not in EMOJIS:
        return _err("INVALID")
    target.name = name
    target.emoji = cmd.emoji or target.emoji
    target.role = cmd.role or target.role
    return Applied(room)


def _kick(room: Room, actor: Participant, cmd: c.ParticipantKick) -> Outcome:
    if not actor.is_admin:
        return _err("FORBIDDEN")
    if cmd.participant_id == actor.id:
        return _err("FORBIDDEN")
    if cmd.participant_id not in room.participants:
        return _err("NOT_FOUND")
    _remove(room, cmd.participant_id)
    return Applied(room, effects=(SeatReleased(cmd.participant_id, kicked=True),))


def _set_admin(room: Room, actor: Participant, cmd: c.AdminSet) -> Outcome:
    if not actor.is_admin:
        return _err("FORBIDDEN")
    target = room.participants.get(cmd.participant_id)
    if target is None:
        return _err("NOT_FOUND")
    if cmd.is_admin:
        if target.is_manual:
            return _err("NOT_MANUAL")
        target.is_admin = True
        return Applied(room)
    admins = [p for p in room.participants.values() if p.is_admin]
    if target.id == actor.id and len(admins) == 1:
        return _err("LAST_ADMIN")
    target.is_admin = False
    return Applied(room)


def _add_manual(room: Room, actor: Participant, cmd: c.ManualAdd) -> Outcome:
    if not actor.is_admin:
        return _err("FORBIDDEN")
    created = _add_participant(room, cmd.name, cmd.emoji, cmd.role, manual=True, token=None)
    if isinstance(created, DomainError):
        return created
    return Applied(room)


def _edit_categories(
    room: Room,
    actor: Participant,
    cmd: c.CategoryAdd | c.CategoryUpdate | c.CategoryDelete | c.CategoryMove,
) -> Outcome:
    if not actor.is_admin:
        return _err("FORBIDDEN")
    if room.phase != "lobby":
        return _err("WRONG_PHASE")
    match cmd:
        case c.CategoryAdd():
            if len(room.categories) >= MAX_CATEGORIES:
                return _err("TOO_MANY_CATEGORIES")
            name = clean_display(cmd.name)
            if not 1 <= len(name) <= CATEGORY_NAME_MAX_LENGTH:
                return _err("INVALID")
            room.categories.append(Category(f"c{room.next_category_seq}", cmd.emoji, name))
            room.next_category_seq += 1
        case c.CategoryUpdate():
            category = room.category(cmd.category_id)
            if category is None:
                return _err("NOT_FOUND")
            name = clean_display(cmd.name)
            if not 1 <= len(name) <= CATEGORY_NAME_MAX_LENGTH:
                return _err("INVALID")
            category.emoji = cmd.emoji
            category.name = name
        case c.CategoryDelete():
            category = room.category(cmd.category_id)
            if category is None:
                return _err("NOT_FOUND")
            room.categories.remove(category)
        case c.CategoryMove():
            category = room.category(cmd.category_id)
            if category is None:
                return _err("NOT_FOUND")
            index = room.categories.index(category)
            target = index + cmd.direction
            if 0 <= target < len(room.categories):
                cats = room.categories
                cats[index], cats[target] = cats[target], cats[index]
    return Applied(room)


def _change_phase(
    room: Room,
    actor: Participant,
    cmd: c.VotingStart | c.VotingReveal | c.VotingReopen | c.RoundNew,
) -> Outcome:
    if not actor.is_admin:
        return _err("FORBIDDEN")
    match cmd:
        case c.VotingStart():
            if room.phase != "lobby":
                return _err("WRONG_PHASE")
            if room.start_missing():
                return _err("START_REQUIREMENTS")
            _reset_done(room)
            room.phase = "voting"
        case c.VotingReveal():
            if room.phase != "voting":
                return _err("WRONG_PHASE")
            room.results = compute_results(room)
            room.phase = "results"
        case c.VotingReopen():
            if room.phase != "results":
                return _err("WRONG_PHASE")
            room.results = None
            room.phase = "voting"
        case c.RoundNew():
            if room.phase != "results":
                return _err("WRONG_PHASE")
            room.scores.clear()
            room.results = None
            _reset_done(room)
            room.phase = "lobby"
    return Applied(room)


def _set_score(room: Room, actor: Participant, cmd: c.ScoreSet) -> Outcome:
    if room.phase != "voting":
        return _err("WRONG_PHASE")
    voter = _resolve_voter(room, actor, cmd.as_participant_id)
    if isinstance(voter, DomainError):
        return voter
    candidate = room.participants.get(cmd.candidate_id)
    if candidate is None or room.category(cmd.category_id) is None:
        return _err("NOT_FOUND")
    if candidate.role != "candidate":
        return _err("NOT_CANDIDATE")
    if candidate.id == voter.id:
        return _err("SELF_VOTE")
    key = (voter.id, candidate.id, cmd.category_id)
    if cmd.quarters is None:
        room.scores.pop(key, None)
    else:
        room.scores[key] = cmd.quarters
    return Applied(room)


def _set_done(room: Room, actor: Participant, cmd: c.VoterDone) -> Outcome:
    if room.phase != "voting":
        return _err("WRONG_PHASE")
    voter = _resolve_voter(room, actor, cmd.as_participant_id)
    if isinstance(voter, DomainError):
        return voter
    voter.done = cmd.done
    return Applied(room)


# --- Helpers -------------------------------------------------------------------------


def _resolve_voter(
    room: Room, actor: Participant, as_participant_id: str | None
) -> Participant | DomainError:
    """Who votes: the actor, or a manual participant an admin votes for."""
    if as_participant_id is None or as_participant_id == actor.id:
        return actor
    if not actor.is_admin:
        return _err("FORBIDDEN")
    represented = room.participants.get(as_participant_id)
    if represented is None:
        return _err("NOT_FOUND")
    if not represented.is_manual:
        return _err("NOT_MANUAL")
    return represented


def _validate_name(room: Room, raw: str, *, exclude_id: str | None = None) -> str | DomainError:
    name = clean_display(raw)
    if not 1 <= len(name) <= NAME_MAX_LENGTH:
        return _err("INVALID")
    key = normalize_name(name)
    for participant in room.participants.values():
        if participant.id != exclude_id and normalize_name(participant.name) == key:
            return _err("NAME_TAKEN")
    return name


def _add_participant(
    room: Room, raw_name: str, emoji: str, role: Role, *, manual: bool, token: str | None
) -> Participant | DomainError:
    if len(room.participants) >= MAX_PARTICIPANTS:
        return _err("ROOM_FULL")
    name = _validate_name(room, raw_name)
    if isinstance(name, DomainError):
        return name
    if emoji not in EMOJIS:
        return _err("INVALID")
    seq = room.next_participant_seq
    room.next_participant_seq += 1
    participant = Participant(
        id=f"p{seq}",
        name=name,
        emoji=emoji,
        role=role,
        joined_seq=seq,
        is_manual=manual,
        connected=not manual,
        rejoin_token=token,
    )
    room.participants[participant.id] = participant
    return participant


def _remove(room: Room, participant_id: str) -> None:
    """Remove a participant and drop the scores they gave and received.

    Results already revealed are frozen in `room.results` and do not change.
    """
    del room.participants[participant_id]
    room.scores = {
        key: value for key, value in room.scores.items() if participant_id not in (key[0], key[1])
    }


def _reset_done(room: Room) -> None:
    for participant in room.participants.values():
        participant.done = False


def _ensure_admin(room: Room) -> None:
    """If no admin is present, promote the connected participant who joined first."""
    if any(p.is_admin and p.present for p in room.participants.values()):
        return
    connected = [p for p in room.ordered_participants() if p.has_device and p.connected]
    if connected:
        connected[0].is_admin = True


def _finalize(room: Room, now: float) -> None:
    _ensure_admin(room)
    if any(p.connected for p in room.participants.values() if p.has_device):
        room.empty_since = None
    elif room.empty_since is None:
        room.empty_since = now
    room.version += 1
