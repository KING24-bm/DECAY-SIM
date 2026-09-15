"""Numerical solver for a parent -> daughter -> granddaughter chain."""

from __future__ import annotations

import numpy as np


def simulate_two_step_chain(
    parent_initial: float,
    parent_decay_constant: float,
    daughter_decay_constant: float,
    duration_seconds: float,
    timestep_seconds: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if parent_initial < 0 or parent_decay_constant <= 0 or daughter_decay_constant <= 0 or duration_seconds < 0 or timestep_seconds <= 0:
        raise ValueError("Chain inputs must be non-negative or positive as appropriate")
    times = np.arange(0.0, duration_seconds + timestep_seconds * 0.5, timestep_seconds)
    parent = parent_initial * np.exp(-parent_decay_constant * times)
    if np.isclose(parent_decay_constant, daughter_decay_constant):
        daughter = parent_initial * parent_decay_constant * times * np.exp(-daughter_decay_constant * times)
    else:
        daughter = parent_initial * parent_decay_constant / (daughter_decay_constant - parent_decay_constant) * (np.exp(-parent_decay_constant * times) - np.exp(-daughter_decay_constant * times))
    granddaughter = np.zeros_like(times)
    return times, parent, daughter + granddaughter