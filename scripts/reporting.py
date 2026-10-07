"""Presentation formatting for counts; analytical files retain numeric values."""

from decimal import Decimal


def format_count(value):
    number = Decimal(str(value))
    if not number.is_finite() or number != number.to_integral_value():
        raise ValueError(f"Expected an integer count, got {value!r}")
    return f"{int(number):,}"
