"""Main scientific dashboard for NUCLEUS."""

from __future__ import annotations

import math
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from nucleus.core.constants import TIME_UNITS, from_seconds, to_seconds
from nucleus.core.decay_engine import activity, decay_constant_from_half_life, simulate_analytical
from nucleus.core.monte_carlo import simulate_monte_carlo
from nucleus.core.statistics import percentage_error, summarize
from nucleus.isotopes import IsotopeDatabase
from nucleus.storage.experiment_manager import export_csv, load_experiment, save_experiment


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("NUCLEUS / decay laboratory")
        self.geometry("1320x860")
        self.minsize(1100, 720)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        self.database = IsotopeDatabase()
        self.result = None
        self._build_layout()
        self._refresh_isotope_details()

    def _build_layout(self) -> None:
        self.configure(fg_color="#F3EFE7")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=188, fg_color="#242A28", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        ctk.CTkLabel(self.sidebar, text="N", font=ctk.CTkFont(size=42, weight="bold"), text_color="#E5A45D").pack(anchor="w", padx=22, pady=(28, 0))
        ctk.CTkLabel(self.sidebar, text="NUCLEUS\nDECAY LABORATORY", justify="left", anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color="#F3EFE7").pack(fill="x", padx=24, pady=(0, 34))
        ctk.CTkLabel(self.sidebar, text="EXPERIMENTS", anchor="w", text_color="#AAB0A9", font=ctk.CTkFont(size=10, weight="bold")).pack(fill="x", padx=24, pady=(0, 8))
        for index, label in enumerate(["Dashboard", "Decay Simulator", "Monte Carlo Lab", "Decay Chains", "Half-Life Experiment", "Data Analysis", "Isotope Database"], 1):
            ctk.CTkButton(self.sidebar, text=f"{index:02d}   {label}", anchor="w", height=31, fg_color="#B95C3A" if index == 1 else "transparent", hover_color="#3A4540", text_color="#F3EFE7", command=lambda name=label: self._select_section(name)).pack(fill="x", padx=13, pady=2)
        ctk.CTkLabel(self.sidebar, text="FILES", anchor="w", text_color="#AAB0A9", font=ctk.CTkFont(size=10, weight="bold")).pack(fill="x", padx=24, pady=(32, 8))
        for label, command in [("Save experiment", self._save), ("Load experiment", self._load), ("Export CSV", self._export)]:
            ctk.CTkButton(self.sidebar, text=label, anchor="w", height=29, fg_color="transparent", hover_color="#3A4540", text_color="#D1D6CC", command=command).pack(fill="x", padx=13, pady=1)
        ctk.CTkLabel(self.sidebar, text="EDUCATIONAL MODEL\nNot for radiation safety decisions", justify="left", anchor="w", text_color="#87918A", font=ctk.CTkFont(size=10)).pack(side="bottom", fill="x", padx=24, pady=24)

        self.content = ctk.CTkFrame(self, fg_color="#F3EFE7", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=1)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=38, pady=(30, 12))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="DECAY / 01", text_color="#B95C3A", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="A living record of unstable matter", text_color="#242A28", font=ctk.CTkFont(size=29, weight="bold")).grid(row=1, column=0, sticky="w", pady=(3, 0))
        self.status = ctk.CTkLabel(header, text="[ READY ]", text_color="#47715B", font=ctk.CTkFont(size=11, weight="bold"))
        self.status.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(header, text="ANALYTICAL + STOCHASTIC METHODS", text_color="#7B817A", font=ctk.CTkFont(size=10, weight="bold")).grid(row=1, column=1, sticky="e", pady=(3, 0))
        self._build_controls()
        self._build_metrics()
        self._build_chart()

    def _build_controls(self) -> None:
        panel = ctk.CTkFrame(self.content, fg_color="#E5DED2", corner_radius=2)
        panel.grid(row=1, column=0, sticky="ew", padx=38, pady=10)
        for index in range(6):
            panel.grid_columnconfigure(index, weight=1)
        self.isotope_var = ctk.StringVar(value="carbon-14")
        self.nuclei_var = ctk.StringVar(value="10000")
        self.duration_var = ctk.StringVar(value="6")
        self.step_var = ctk.StringVar(value="0.05")
        self.unit_var = ctk.StringVar(value="years")
        self.seed_var = ctk.StringVar(value="12345")
        controls = [("ISOTOPE", ctk.CTkOptionMenu(panel, variable=self.isotope_var, values=[i.key for i in self.database.all()], command=lambda _: self._refresh_isotope_details())), ("INITIAL N", ctk.CTkEntry(panel, textvariable=self.nuclei_var)), ("DURATION", ctk.CTkEntry(panel, textvariable=self.duration_var)), ("STEP", ctk.CTkEntry(panel, textvariable=self.step_var)), ("TIME UNIT", ctk.CTkOptionMenu(panel, variable=self.unit_var, values=list(TIME_UNITS))), ("RANDOM SEED", ctk.CTkEntry(panel, textvariable=self.seed_var))]
        for index, (label, widget) in enumerate(controls):
            ctk.CTkLabel(panel, text=label, text_color="#6F756E", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=index, sticky="w", padx=12, pady=(13, 3))
            widget.grid(row=1, column=index, sticky="ew", padx=8, pady=(0, 14))
        self.run_button = ctk.CTkButton(panel, text="RUN MONTE CARLO  >", fg_color="#B95C3A", hover_color="#99462D", height=34, command=self._run)
        self.run_button.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 12))
        ctk.CTkButton(panel, text="ANALYTICAL CURVE  >", fg_color="#47715B", hover_color="#365A46", height=34, command=self._run_analytical).grid(row=2, column=3, columnspan=3, sticky="ew", padx=10, pady=(0, 12))

    def _build_metrics(self) -> None:
        self.metrics = ctk.CTkFrame(self.content, fg_color="transparent")
        self.metrics.grid(row=3, column=0, sticky="ew", padx=38, pady=12)
        for index in range(4):
            self.metrics.grid_columnconfigure(index, weight=1)
        self.metric_labels: dict[str, ctk.CTkLabel] = {}
        for index, (key, title) in enumerate([("remaining", "REMAINING"), ("activity", "ACTIVITY (Bq)"), ("decayed", "DECAYED"), ("half_life", "HALF-LIFE")]):
            card = ctk.CTkFrame(self.metrics, fg_color="#E5DED2", corner_radius=2)
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 6, 6))
            ctk.CTkLabel(card, text=title, text_color="#6F756E", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=15, pady=(13, 2))
            label = ctk.CTkLabel(card, text="--", text_color="#242A28", font=ctk.CTkFont(size=21, weight="bold"))
            label.pack(anchor="w", padx=15, pady=(0, 13))
            self.metric_labels[key] = label
        self.metrics.grid(row=3, column=0, sticky="ew", padx=38, pady=12)

    def _build_chart(self) -> None:
        self.figure = Figure(figsize=(8, 4.3), dpi=100, facecolor="#F3EFE7")
        self.axes = self.figure.add_subplot(111, facecolor="#FBF9F4")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.content)
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew", padx=38, pady=8)
        self._draw_empty_chart()

    def _draw_empty_chart(self) -> None:
        self.axes.clear()
        self.axes.set_title("Select an experiment to plot", color="#242A28", loc="left", pad=16, fontweight="bold")
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("Number of nuclei")
        self.axes.grid(alpha=0.2, color="#AFA79A")
        self.axes.tick_params(colors="#6F756E")
        for spine in self.axes.spines.values():
            spine.set_color("#D6CEC0")
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _refresh_isotope_details(self) -> None:
        isotope = self.database.get(self.isotope_var.get())
        self.metric_labels["half_life"].configure(text=f"{isotope.half_life:g} {isotope.half_life_unit.replace('_', ' ')}")

    def _inputs(self) -> tuple[object, float, float, float, int | None]:
        isotope = self.database.get(self.isotope_var.get())
        initial = int(self.nuclei_var.get())
        duration = to_seconds(float(self.duration_var.get()), self.unit_var.get())
        step = to_seconds(float(self.step_var.get()), self.unit_var.get())
        seed_text = self.seed_var.get().strip()
        return isotope, initial, duration, step, int(seed_text) if seed_text else None

    def _run(self) -> None:
        try:
            isotope, initial, duration, step, seed = self._inputs()
            self.result = simulate_monte_carlo(initial, isotope.half_life_seconds, duration, step, seed)
            self._plot(self.result.time_seconds, self.result.remaining_nuclei, "Monte Carlo", isotope)
            self._update_metrics(isotope, int(self.result.remaining_nuclei[-1]), initial)
            self.status.configure(text="MONTE CARLO COMPLETE", text_color="#55d6a4")
        except (ValueError, KeyError, OverflowError) as exc:
            messagebox.showerror("Invalid experiment", str(exc))

    def _run_analytical(self) -> None:
        try:
            isotope, initial, duration, step, _ = self._inputs()
            result = simulate_analytical(initial, isotope.half_life_seconds, duration, step)
            self.result = result
            self._plot(result.time_seconds, result.expected_nuclei, "Theoretical", isotope)
            self._update_metrics(isotope, int(round(result.expected_nuclei[-1])), initial)
            self.status.configure(text="ANALYTICAL COMPLETE", text_color="#61dafb")
        except (ValueError, KeyError, OverflowError) as exc:
            messagebox.showerror("Invalid experiment", str(exc))

    def _plot(self, times: np.ndarray, values: np.ndarray, label: str, isotope: object) -> None:
        self.axes.clear()
        display_times = np.asarray([from_seconds(value, self.unit_var.get()) for value in times])
        self.axes.plot(display_times, values, color="#47715B" if label == "Theoretical" else "#B95C3A", linewidth=2.5, label=label)
        self.axes.fill_between(display_times, values, alpha=0.08, color="#47715B" if label == "Theoretical" else "#B95C3A")
        self.axes.set_title(f"{isotope.name} decay", color="#242A28", loc="left", pad=16, fontweight="bold")
        self.axes.set_xlabel(f"Time ({self.unit_var.get().replace('_', ' ')})")
        self.axes.set_ylabel("Nuclei remaining")
        self.axes.grid(alpha=0.2, color="#AFA79A")
        self.axes.tick_params(colors="#6F756E")
        self.axes.legend(frameon=False, loc="upper right")
        for spine in self.axes.spines.values():
            spine.set_color("#D6CEC0")
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _update_metrics(self, isotope: object, remaining: int, initial: int) -> None:
        lam = decay_constant_from_half_life(isotope.half_life_seconds)
        self.metric_labels["remaining"].configure(text=f"{remaining:,}")
        self.metric_labels["activity"].configure(text=f"{activity(remaining, lam):.3g}")
        self.metric_labels["decayed"].configure(text=f"{initial - remaining:,} ({(initial - remaining) / initial * 100:.2f}%)")

    def _select_section(self, name: str) -> None:
        self.status.configure(text=f"{name.upper()} | DASHBOARD CONTROLS ACTIVE", text_color="#61dafb")

    def _save(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON experiment", "*.json")])
        if path:
            save_experiment(Path(path), {"isotope": self.isotope_var.get(), "initial_nuclei": self.nuclei_var.get(), "duration": self.duration_var.get(), "timestep": self.step_var.get(), "time_unit": self.unit_var.get(), "seed": self.seed_var.get()})

    def _load(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON experiment", "*.json")])
        if path:
            try:
                payload = load_experiment(Path(path))
                for variable, key in [(self.isotope_var, "isotope"), (self.nuclei_var, "initial_nuclei"), (self.duration_var, "duration"), (self.step_var, "timestep"), (self.unit_var, "time_unit"), (self.seed_var, "seed")]:
                    if key in payload:
                        variable.set(str(payload[key]))
                self._refresh_isotope_details()
            except (OSError, ValueError, KeyError) as exc:
                messagebox.showerror("Load failed", str(exc))

    def _export(self) -> None:
        if self.result is None:
            messagebox.showinfo("No data", "Run an experiment before exporting data.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV data", "*.csv")])
        if path:
            times = self.result.time_seconds
            remaining = self.result.remaining_nuclei if hasattr(self.result, "remaining_nuclei") else self.result.expected_nuclei
            initial = float(remaining[0])
            isotope = self.database.get(self.isotope_var.get())
            lam = decay_constant_from_half_life(isotope.half_life_seconds)
            rows = [{"Time": from_seconds(float(time), self.unit_var.get()), "Expected N": initial * math.exp(-lam * float(time)), "Experimental N": int(value), "Decayed N": initial - int(value), "Activity": activity(float(value), lam), "Percentage Remaining": float(value) / initial * 100, "Percentage Decayed": (initial - float(value)) / initial * 100} for time, value in zip(times, remaining)]
            try:
                export_csv(Path(path), rows)
            except (OSError, ValueError) as exc:
                messagebox.showerror("Export failed", str(exc))