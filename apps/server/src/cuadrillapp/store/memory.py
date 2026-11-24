"""Rooms kept in process memory (single instance)."""

from collections.abc import Iterator

from cuadrillapp.domain.models import Room


class MemoryRoomStore:
    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}

    def get(self, code: str) -> Room | None:
        return self._rooms.get(code)

    def put(self, room: Room) -> None:
        self._rooms[room.code] = room

    def delete(self, code: str) -> None:
        self._rooms.pop(code, None)

    def exists(self, code: str) -> bool:
        return code in self._rooms

    def codes(self) -> Iterator[str]:
        return iter(list(self._rooms))

    def count(self) -> int:
        return len(self._rooms)
