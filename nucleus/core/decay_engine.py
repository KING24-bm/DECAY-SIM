"""Validated analytical and stochastic radioactive decay calculations."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .constants import LN2


class DecayInputError(ValueError):
    """Raised when a decay parameter is physically or numerically invalid."""


def _positive_finite(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise DecayInputError(f"{label} must be finite and greater than zero")
    return value


def _nonnegative_finite(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise DecayInputError(f"{label} must be finite and non-negative")
    return value


def decay_constant_from_half_life(half_life_seconds: float) -> float:
    """Return lambda in s^-1 from a half-life in seconds."""
    return LN2 / _positive_finite(half_life_seconds, "Half-life")


def half_life_from_decay_constant(decay_constant: float) -> float:
    """Return half-life in seconds from lambda in s^-1."""
    return LN2 / _positive_finite(decay_constant, "Decay constant")


def remaining_nuclei(initial_nuclei: float, decay_constant: float, time_seconds: float) -> float:
    """Evaluate N(t) = N0 exp(-lambda t) without overflow for valid inputs."""
    initial = _nonnegative_finite(initial_nuclei, "Initial nuclei")
    decay_constant = _positive_finite(decay_constant, "Decay constant")
    time_seconds = _nonnegative_finite(time_seconds, "Time")
    return initial * math.exp(-decay_constant * time_seconds)


def activity(nuclei: float, decay_constant: float) -> float:
    """Evaluate activity A = lambda N in becquerels."""
    return _nonnegative_finite(nuclei, "Nuclei") * _positive_finite(decay_constant, "Decay constant")


def decay_probability(decay_constant: float, timestep_seconds: float) -> float:
    """Return the exact probability of decay during one timestep."""
    decay_constant = _positive_finite(decay_constant, "Decay constant")
    timestep_seconds = _nonnegative_finite(timestep_seconds, "Timestep")
    return float(-math.expm1(-decay_constant * timestep_seconds))


@dataclass(frozen=True)
class AnalyticalResult:
    """Vectorized analytical decay series."""

    time_seconds: np.ndarray
    expected_nuclei: np.ndarray
    expected_activity: np.ndarray


def simulate_analytical(
    initial_nuclei: float,
    half_life_seconds: float,
    duration_seconds: float,
    timestep_seconds: float,
) -> AnalyticalResult:
    """Generate an analytical decay curve on an inclusive regular time grid."""
    initial_nuclei = _nonnegative_finite(initial_nuclei, "Initial nuclei")
    half_life_seconds = _positive_finite(half_life_seconds, "Half-life")
    duration_seconds = _nonnegative_finite(duration_seconds, "Duration")
    timestep_seconds = _positive_finite(timestep_seconds, "Timestep")
    if duration_seconds == 0:
        times = np.array([0.0])
    else:
        count = int(math.floor(duration_seconds / timestep_seconds))
        times = np.arange(count + 1, dtype=float) * timestep_seconds
        if times[-1] < duration_seconds:
            times = np.append(times, duration_seconds)
    lam = decay_constant_from_half_life(half_life_seconds)
    expected = initial_nuclei * np.exp(-lam * times)
    return AnalyticalResult(times, expected, lam * expected)