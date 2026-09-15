# NUCLEUS — Radioactive Decay Simulator

NUCLEUS is a desktop educational laboratory for exploring radioactive decay with analytical equations and reproducible Monte Carlo experiments. It uses Python, CustomTkinter, NumPy, and Matplotlib, with a deliberately separate physics layer so calculations can be tested without starting the GUI.

## Features

- Analytical decay law, activity, half-life, decay constant, and exact timestep probability.
- Vectorized/binomial Monte Carlo simulation with optional random seed.
- Catalog of nine educational isotopes, including Carbon-14, Uranium-238, Cesium-137, Iodine-131, and Technetium-99m.
- Alpha, beta-minus, beta-plus, and gamma transformation rules.
- Two-step parent/daughter chain solver.
- Scientific charting, JSON experiment save/load, and CSV data export.
- Focused automated tests for numerical correctness and physical invariants.

## Installation and use

Python 3.12 or newer is recommended. On Windows, use the launcher explicitly if multiple Python versions are installed:

```powershell
py -3.14 -m pip install -r requirements.txt
py -3.14 main.py
```

Run tests with:

```powershell
py -3.14 -m pytest -q
```

## Physics

The analytical model is $N(t)=N_0e^{-\lambda t}$, with $\lambda=\ln(2)/T_{1/2}$. Activity is $A(t)=\lambda N(t)$. Individual nuclei are sampled using $P(\mathrm{decay})=1-e^{-\lambda\Delta t}$; each timestep uses a binomial draw, which is efficient and preserves the stochastic interpretation.

All calculations use seconds internally. Isotope values are approximate educational values and are labeled in the catalog. They are not a substitute for a current evaluated nuclear-data library.

## Architecture

`nucleus/core` contains numerical services, `nucleus/isotopes` contains the catalog, `nucleus/decay_modes.py` contains transformations, `nucleus/storage` handles portable files, and `nucleus/gui` contains only presentation and event wiring. The current dashboard is the first complete runnable UI surface; additional navigation entries provide a clear expansion point for dedicated laboratory panels.

## Data and limitations

Experiments are portable JSON files. Simulation samples can be exported as CSV with time, expected and experimental populations, activity, and percentages. This is an educational simulator, not a radiation-safety, medical, shielding, dosimetry, or reactor-design tool.

## Screenshots

Screenshots can be added here after capturing the dashboard on the target desktop environment.