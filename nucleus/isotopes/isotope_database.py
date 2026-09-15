"""Load scientifically sourced educational isotope data from JSON."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from nucleus.core.constants import TIME_UNITS, to_seconds


@dataclass(frozen=True)
class Isotope:
    key: str
    name: str
    symbol: str
    mass_number: int
    atomic_number: int
    half_life: float
    half_life_unit: str
    decay_mode: str
    daughter: str
    decay_energy_mev: float | None
    notes: str

    @property
    def half_life_seconds(self) -> float:
        return to_seconds(self.half_life, self.half_life_unit)

    @property
    def nuclide_label(self) -> str:
        return f"{self.symbol}-{self.mass_number}"


class IsotopeDatabase:
    def __init__(self, path: Path | None = None) -> None:
        path = path or Path(__file__).resolve().parents[1] / "data" / "isotopes.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._isotopes = {item["key"]: Isotope(**item) for item in raw}

    def all(self) -> list[Isotope]:
        return list(self._isotopes.values())

    def get(self, key: str) -> Isotope:
        try:
            return self._isotopes[key]
        except KeyError as exc:
            raise KeyError(f"Unknown isotope: {key}") from exc


def validate_database(database: IsotopeDatabase) -> None:
    """Validate data invariants at startup or in a data-quality test."""
    for isotope in database.all():
        if isotope.half_life_unit not in TIME_UNITS or isotope.half_life <= 0:
            raise ValueError(f"Invalid half-life for {isotope.key}")
        if isotope.atomic_number <= 0 or isotope.mass_number < isotope.atomic_number:
            raise ValueError(f"Invalid nuclide numbers for {isotope.key}")