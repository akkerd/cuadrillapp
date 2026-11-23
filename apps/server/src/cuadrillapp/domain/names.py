"""Limpieza y normalización de nombres."""

import unicodedata


def clean_display(text: str) -> str:
    """Quita espacios al principio y al final y colapsa los internos."""
    return " ".join(text.split())


def normalize_name(name: str) -> str:
    """Clave de comparación: sin mayúsculas, tildes ni espacios sobrantes."""
    decomposed = unicodedata.normalize("NFKD", clean_display(name))
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_marks.casefold()
