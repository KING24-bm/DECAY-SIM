"""Educational nuclear transformation rules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Transformation:
    mode: str
    parent_atomic_number: int
    parent_mass_number: int
    daughter_atomic_number: int
    daughter_mass_number: int
    emitted_particle: str
    explanation: str


def transform(atomic_number: int, mass_number: int, mode: str) -> Transformation:
    if atomic_number <= 0 or mass_number < atomic_number:
        raise ValueError("Invalid parent nuclide numbers")
    normalized = mode.strip().lower()
    if normalized == "alpha":
        return Transformation(mode, atomic_number, mass_number, atomic_number - 2, mass_number - 4, "alpha particle", "Alpha emission reduces atomic number by 2 and mass number by 4.")
    if normalized in {"beta-minus", "beta minus", "beta−"}:
        return Transformation(mode, atomic_number, mass_number, atomic_number + 1, mass_number, "electron and antineutrino", "Beta-minus emission converts a neutron to a proton; mass number is unchanged.")
    if normalized in {"beta-plus", "beta plus", "beta+"}:
        return Transformation(mode, atomic_number, mass_number, atomic_number - 1, mass_number, "positron and neutrino", "Beta-plus emission converts a proton to a neutron; mass number is unchanged.")
    if normalized == "gamma":
        return Transformation(mode, atomic_number, mass_number, atomic_number, mass_number, "gamma photon", "Gamma emission changes nuclear energy state, not atomic or mass number.")
    raise ValueError(f"Unsupported decay mode: {mode}")