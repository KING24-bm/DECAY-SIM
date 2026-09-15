import math

import numpy as np
import pytest

from nucleus.core.decay_chain import simulate_two_step_chain
from nucleus.core.decay_engine import (
    DecayInputError,
    activity,
    decay_constant_from_half_life,
    decay_probability,
    half_life_from_decay_constant,
    remaining_nuclei,
    simulate_analytical,
)
from nucleus.core.monte_carlo import simulate_monte_carlo
from nucleus.core.statistics import percentage_error, summarize
from nucleus.decay_modes import transform
from nucleus.isotopes import IsotopeDatabase
from nucleus.isotopes.isotope_database import validate_database


def test_half_life_and_decay_constant_are_inverses() -> None:
    assert half_life_from_decay_constant(decay_constant_from_half_life(5730.0)) == pytest.approx(5730.0)


def test_one_half_life_leaves_half() -> None:
    lam = decay_constant_from_half_life(10.0)
    assert remaining_nuclei(1000.0, lam, 10.0) == pytest.approx(500.0)
    assert activity(1000.0, lam) == pytest.approx(lam * 1000.0)


def test_decay_probability_is_exact() -> None:
    lam = decay_constant_from_half_life(10.0)
    assert decay_probability(lam, 10.0) == pytest.approx(0.5)


def test_invalid_parameters_are_rejected() -> None:
    with pytest.raises(DecayInputError):
        decay_constant_from_half_life(0)
    with pytest.raises(DecayInputError):
        remaining_nuclei(-1, 0.1, 1)


def test_monte_carlo_is_reproducible_and_integer_valued() -> None:
    first = simulate_monte_carlo(10_000, 100.0, 200.0, 10.0, seed=42)
    second = simulate_monte_carlo(10_000, 100.0, 200.0, 10.0, seed=42)
    assert np.array_equal(first.remaining_nuclei, second.remaining_nuclei)
    assert np.all(first.remaining_nuclei[1:] <= first.remaining_nuclei[:-1])


def test_monte_carlo_converges_in_large_sample() -> None:
    result = simulate_monte_carlo(1_000_000, 100.0, 100.0, 100.0, seed=7)
    assert result.remaining_nuclei[-1] / 1_000_000 == pytest.approx(0.5, abs=0.002)


def test_decay_modes_conserve_expected_quantities() -> None:
    alpha = transform(92, 238, "alpha")
    beta = transform(6, 14, "beta-minus")
    gamma = transform(43, 99, "gamma")
    assert (alpha.daughter_atomic_number, alpha.daughter_mass_number) == (90, 234)
    assert (beta.daughter_atomic_number, beta.daughter_mass_number) == (7, 14)
    assert (gamma.daughter_atomic_number, gamma.daughter_mass_number) == (43, 99)


def test_chain_initial_conditions_and_statistics() -> None:
    times, parent, daughter = simulate_two_step_chain(1000, 0.1, 0.01, 100, 10)
    assert times[0] == 0
    assert parent[0] == pytest.approx(1000)
    assert daughter[0] == pytest.approx(0)
    summary = summarize([1, 2, 3, 4])
    assert summary.mean == pytest.approx(2.5)
    assert percentage_error(95, 100) == pytest.approx(5)


def test_isotope_database_has_valid_entries() -> None:
    database = IsotopeDatabase()
    validate_database(database)
    assert len(database.all()) >= 9
    assert database.get("carbon-14").half_life_seconds > 0