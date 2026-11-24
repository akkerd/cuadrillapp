"""Game limits and catalogs. Exported to the frontend with `make gen`."""

from typing import Final

MAX_PARTICIPANTS: Final = 30
NAME_MAX_LENGTH: Final = 16
TITLE_MAX_LENGTH: Final = 30
EMOJI_MAX_LENGTH: Final = 16
DEFAULT_TITLE: Final = "Concurso"

CODE_LENGTH: Final = 5
# No ambiguous characters: 0, O, 1, I, L.
CODE_ALPHABET: Final = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

ADMIN_GRACE_SECONDS: Final = 60.0
ROOM_IDLE_TTL_SECONDS: Final = 30 * 60.0

EMOJIS: Final[tuple[str, ...]] = (
    "🦄", "🐸", "🌮", "🥑", "👽", "🤖", "🦖", "🐙", "🍕", "🤡",
    "👻", "🎃", "🦥", "🐧", "🦩", "🐔", "🥸", "🤠", "😎", "🧌",
    "🐷", "🐵", "🦊", "🐼", "🐨", "🐯", "🦁", "🐮", "🐻", "🐶",
    "🐱", "🐹", "🦔", "🦦", "🦭", "🐳", "🦈", "🐢", "🦀", "🐝",
    "🍩", "🍔", "🌭", "🍟", "🥨", "🧀", "🍉", "🍍", "🥥", "🍄",
    "🌵", "🌈", "🔥", "⚡", "🪩", "🎸", "🛸", "🧙", "🥷", "🧛",
)  # fmt: skip
