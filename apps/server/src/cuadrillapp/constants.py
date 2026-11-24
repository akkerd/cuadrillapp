"""Game limits and catalogs. Exported to the frontend with `make gen`."""

from typing import Final

MAX_PARTICIPANTS: Final = 30
MAX_CATEGORIES: Final = 8
NAME_MAX_LENGTH: Final = 16
TITLE_MAX_LENGTH: Final = 30
CATEGORY_NAME_MAX_LENGTH: Final = 20
EMOJI_MAX_LENGTH: Final = 16
DEFAULT_TITLE: Final = "Concurso"

CODE_LENGTH: Final = 5
# No ambiguous characters: 0, O, 1, I, L.
CODE_ALPHABET: Final = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

QUARTERS_PER_POINT: Final = 4
MAX_QUARTERS: Final = 40  # 10 points

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

CATEGORY_SUGGESTIONS: Final[tuple[tuple[str, str], ...]] = (
    ("😂", "Gracioso"),
    ("🎨", "Original"),
    ("💪", "Esfuerzo"),
    ("👗", "Estilo"),
    ("🔥", "Épico"),
    ("😍", "Bonito"),
    ("🤯", "Sorpresa"),
    ("😋", "Sabor"),
)
