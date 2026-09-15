"""Vectorized Monte Carlo radioactive decay simulations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .decay_engine import DecayInputError, decay_constant_from_half_life, decay_probability


@dataclass(frozen=True)
class MonteCarloResult:
    time_seconds: np.ndarray
    remaining_nuclei: np.ndarray
    decayed_nuclei: np.ndarray


def simulate_monte_carlo(
    initial_nuclei: int,
    half_life_seconds: float,
    duration_seconds: float,
    timestep_seconds: float,
    seed: int | None = None,
) -> MonteCarloResult:
    """Simulate individual decay events using binomial sampling per timestep."""
    if isinstance(initial_nuclei, bool) or int(initial_nuclei) != initial_nuclei or initial_nuclei < 0:
        raise DecayInputError("Initial nuclei must be a non-negative integer")
    if duration_seconds < 0 or timestep_seconds <= 0:
        raise DecayInputError("Duration must be non-negative and timestep must be positive")
    initial_nuclei = int(initial_nuclei)
    duration_seconds = float(duration_seconds)
    timestep_seconds = float(timestep_seconds)
    lam = decay_constant_from_half_life(half_life_seconds)
    times = np.arange(0.0, duration_seconds + timestep_seconds * 0.5, timestep_seconds)
    if times.size == 0 or times[-1] < duration_seconds:
        times = np.append(times, duration_seconds)
    rng = np.random.default_rng(seed)
    remaining = np.empty(times.size, dtype=np.int64)
    remaining[0] = initial_nuclei
    for index in range(1, times.size):
        delta = times[index] - times[index - 1]
        probability = decay_probability(lam, delta)
        remaining[index] = remaining[index - 1] - rng.binomial(remaining[index - 1], probability)
    return MonteCarloResult(times, remaining, initial_nuclei - remaining)