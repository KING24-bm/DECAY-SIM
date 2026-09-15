"""Physical and unit conversion constants used by the simulator."""

from __future__ import annotations

import math

SECONDS_PER_MINUTE = 60.0
SECONDS_PER_HOUR = 60.0 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24.0 * SECONDS_PER_HOUR
SECONDS_PER_YEAR = 365.25 * SECONDS_PER_DAY
SECONDS_PER_MILLION_YEARS = 1_000_000.0 * SECONDS_PER_YEAR
LN2 = math.log(2.0)

TIME_UNITS: dict[str, float] = {
    "seconds": 1.0,
    "minutes": SECONDS_PER_MINUTE,
    "hours": SECONDS_PER_HOUR,
    "days": SECONDS_PER_DAY,
    "years": SECONDS_PER_YEAR,
    "millions_of_years": SECONDS_PER_MILLION_YEARS,
}


def to_seconds(value: float, unit: str) -> float:
    """Convert a non-negative duration to seconds."""
    if unit not in TIME_UNITS:
        raise ValueError(f"Unsupported time unit: {unit}")
    if value < 0 or not math.isfinite(value):
        raise ValueError("Duration must be finite and non-negative")
    return value * TIME_UNITS[unit]


def from_seconds(value: float, unit: str) -> float:
    """Convert seconds to a configured display unit."""
    if unit not in TIME_UNITS:
        raise ValueError(f"Unsupported time unit: {unit}")
    return value / TIME_UNITS[unit]