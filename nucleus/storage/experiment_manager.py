"""Portable JSON experiment files and scientific CSV export."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def save_experiment(path: Path, configuration: dict[str, Any]) -> None:
    path.write_text(json.dumps(configuration, indent=2), encoding="utf-8")


def load_experiment(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Experiment file must contain a JSON object")
    return payload


def export_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("There is no simulation data to export")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)