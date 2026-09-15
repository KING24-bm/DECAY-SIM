"""Small dependency-free statistical helpers for experiment analysis."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class Summary:
    count: int
    mean: float
    median: float
    standard_deviation: float
    variance: float
    minimum: float
    maximum: float


def summarize(values: np.ndarray | list[float]) -> Summary:
    data = np.asarray(values, dtype=float)
    data = data[np.isfinite(data)]
    if data.size == 0:
        raise ValueError("Dataset is empty")
    variance = float(np.var(data, ddof=1)) if data.size > 1 else 0.0
    return Summary(int(data.size), float(np.mean(data)), float(np.median(data)), math.sqrt(variance), variance, float(np.min(data)), float(np.max(data)))


def percentage_error(measured: float, reference: float) -> float:
    if reference == 0:
        raise ValueError("Reference value cannot be zero")
    return abs(measured - reference) / abs(reference) * 100.0