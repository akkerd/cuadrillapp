"""Códigos de sala."""

import secrets
from collections.abc import Callable

from cuadrillapp.constants import CODE_ALPHABET, CODE_LENGTH


def normalize_code(raw: str) -> str:
    """Ignora espacios y mayúsculas/minúsculas."""
    return "".join(raw.split()).upper()


def is_valid_code(code: str) -> bool:
    return len(code) == CODE_LENGTH and all(ch in CODE_ALPHABET for ch in code)


def generate_code(
    exists: Callable[[str], bool],
    choice: Callable[[str], str] = secrets.choice,
    attempts: int = 100,
) -> str:
    for _ in range(attempts):
        code = "".join(choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        if not exists(code):
            return code
    raise RuntimeError("No free room code found")
