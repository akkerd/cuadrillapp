"""Scores as integer quarter points (0..40 = 0.00..10.00)."""

from decimal import Decimal, InvalidOperation

from cuadrillapp.constants import MAX_QUARTERS, QUARTERS_PER_POINT


def is_valid_quarters(quarters: int) -> bool:
    return 0 <= quarters <= MAX_QUARTERS


def quarters_to_points(quarters: int) -> Decimal:
    return Decimal(quarters) / QUARTERS_PER_POINT


def points_to_quarters(points: str | Decimal) -> int | None:
    """Convert a score in points to quarters; None if it is off the scale."""
    try:
        value = Decimal(points) * QUARTERS_PER_POINT
    except InvalidOperation:
        return None
    if value != value.to_integral_value():
        return None
    quarters = int(value)
    return quarters if is_valid_quarters(quarters) else None
