"""Name cleanup and normalization."""

import unicodedata


def clean_display(text: str) -> str:
    """Trim leading and trailing spaces and collapse inner whitespace."""
    return " ".join(text.split())


def normalize_name(name: str) -> str:
    """Comparison key: ignores case, accents and extra spaces."""
    decomposed = unicodedata.normalize("NFKD", clean_display(name))
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_marks.casefold()
