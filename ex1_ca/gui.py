"""
Interactive view of the CA: I use matplotlib inside tkinter so I can show the torus
with the colors from the exercise brief (A red, B blue, inhibited black, empty pale).
"""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.image import AxesImage

from ex1_ca.cellular_automaton import EMPTY, INHIBITED, STRAIN_A, STRAIN_B, random_init, step
from ex1_ca.simulation import count_cells


def grid_to_rgb(grid: list[list[int]]) -> np.ndarray:
    """Map cell states to an RGB image (row 0 at the top)."""
    g = np.asarray(grid, dtype=np.uint8)
    h, w = g.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[g == EMPTY] = (245, 245, 240)
    rgb[g == STRAIN_A] = (215, 35, 45)
    rgb[g == STRAIN_B] = (45, 95, 200)
    rgb[g == INHIBITED] = (15, 15, 15)
    return rgb


def _parse_float(entry: tk.Entry, default: float) -> float:
    try:
        return float(entry.get().strip())
    except ValueError:
        return default


class CAApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Exercise 1 — cellular automaton (Kill the Winner)")
        root.minsize(880, 720)

        self.running = False
        self.after_id: str | None = None
        self.grid: list[list[int]] = []
        self.rng = random.Random()
        self.generation = 0
        self.im: AxesImage | None = None

        main = ttk.Frame(root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        ctrl = ttk.LabelFrame(main, text="Parameters", padding=6)
        ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        self.var_rows = tk.IntVar(value=200)
        self.var_cols = tk.IntVar(value=200)
        self.var_k = tk.IntVar(value=4)
        self.var_delay = tk.IntVar(value=80)
        self.var_batch = tk.IntVar(value=1)

        def add_row(r: int, label: str, widget) -> None:
            ttk.Label(ctrl, text=label).grid(row=r, column=0, sticky=tk.W, pady=2)
            widget.grid(row=r, column=1, sticky=tk.EW, pady=2)

        add_row(0, "Rows", ttk.Spinbox(ctrl, from_=20, to=400, textvariable=self.var_rows, width=10))
        add_row(1, "Cols", ttk.Spinbox(ctrl, from_=20, to=400, textvariable=self.var_cols, width=10))
        self.ent_pa = ttk.Entry(ctrl, width=10)
        self.ent_pa.insert(0, "0.35")
        add_row(2, "P_A", self.ent_pa)
        self.ent_pb = ttk.Entry(ctrl, width=10)
        self.ent_pb.insert(0, "0.12")
        add_row(3, "P_B", self.ent_pb)
        add_row(4, "K (9 = phage off)", ttk.Spinbox(ctrl, from_=0, to=9, textvariable=self.var_k, width=10))
        self.ent_init_a = ttk.Entry(ctrl, width=10)
        self.ent_init_a.insert(0, "0.02")
        add_row(5, "Init frac A", self.ent_init_a)
        self.ent_init_b = ttk.Entry(ctrl, width=10)
        self.ent_init_b.insert(0, "0.02")
        add_row(6, "Init frac B", self.ent_init_b)
        self.ent_seed = ttk.Entry(ctrl, width=10)
        self.ent_seed.insert(0, "42")
        add_row(7, "Seed (blank = random)", self.ent_seed)
        add_row(8, "Delay ms", ttk.Spinbox(ctrl, from_=0, to=2000, increment=20, textvariable=self.var_delay, width=10))
        add_row(9, "Steps per tick", ttk.Spinbox(ctrl, from_=1, to=50, textvariable=self.var_batch, width=10))

        ctrl.columnconfigure(1, weight=1)

        btnf = ttk.Frame(ctrl, padding=(0, 8, 0, 0))
        btnf.grid(row=10, column=0, columnspan=2, sticky=tk.EW)
        ttk.Button(btnf, text="Reset grid", command=self.on_reset).pack(fill=tk.X, pady=2)
        ttk.Button(btnf, text="Step once", command=self.on_step).pack(fill=tk.X, pady=2)
        self.run_btn = ttk.Button(btnf, text="Run", command=self.toggle_run)
        self.run_btn.pack(fill=tk.X, pady=2)

        legend = ttk.LabelFrame(ctrl, text="Legend", padding=6)
        legend.grid(row=11, column=0, columnspan=2, sticky=tk.EW, pady=(12, 0))
        for text, color in (
            ("Empty", "#f5f5f0"),
            ("Strain A", "#d7232d"),
            ("Strain B", "#2d5fc8"),
            ("Inhibited", "#0f0f0f"),
        ):
            row = ttk.Frame(legend)
            row.pack(anchor=tk.W, pady=1)
            c = tk.Canvas(row, width=14, height=14, highlightthickness=0)
            c.pack(side=tk.LEFT, padx=(0, 6))
            c.create_rectangle(0, 0, 14, 14, fill=color, outline=color)
            ttk.Label(row, text=text).pack(side=tk.LEFT)

        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.status = ttk.Label(right, text="")
        self.status.pack(anchor=tk.W, pady=(0, 4))

        self.fig = Figure(figsize=(6.5, 6.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.fig.tight_layout(pad=0.2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.on_reset()

    def _parse_seed(self) -> int | None:
        s = self.ent_seed.get().strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return 0

    def _params(self) -> tuple[float, float, float, float]:
        pa = _parse_float(self.ent_pa, 0.35)
        pb = _parse_float(self.ent_pb, 0.12)
        fa = _parse_float(self.ent_init_a, 0.02)
        fb = _parse_float(self.ent_init_b, 0.02)
        return pa, pb, fa, fb

    def on_reset(self) -> None:
        self.stop_run()
        rows = int(self.var_rows.get())
        cols = int(self.var_cols.get())
        seed = self._parse_seed()
        self.rng = random.Random(seed)
        pa, pb, fa, fb = self._params()
        self.grid = random_init(rows, cols, fa, fb, self.rng)
        self.generation = 0
        self._redraw()

    def on_step(self) -> None:
        pa, pb, _fa, _fb = self._params()
        self.grid = step(self.grid, pa, pb, int(self.var_k.get()), self.rng)
        self.generation += 1
        self._redraw()

    def toggle_run(self) -> None:
        if self.running:
            self.stop_run()
        else:
            self.running = True
            self.run_btn.configure(text="Pause")
            self._schedule_tick()

    def stop_run(self) -> None:
        self.running = False
        self.run_btn.configure(text="Run")
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def _schedule_tick(self) -> None:
        if not self.running:
            return
        batch = max(1, int(self.var_batch.get()))
        pa, pb, _, _ = self._params()
        k = int(self.var_k.get())
        for _ in range(batch):
            self.grid = step(self.grid, pa, pb, k, self.rng)
            self.generation += 1
        self._redraw()
        delay = max(0, int(self.var_delay.get()))
        self.after_id = self.root.after(delay, self._schedule_tick)

    def _redraw(self) -> None:
        rgb = grid_to_rgb(self.grid)
        if self.im is None:
            self.im = self.ax.imshow(
                rgb,
                interpolation="nearest",
                aspect="equal",
                origin="upper",
            )
        else:
            arr = self.im.get_array()
            if arr is None or arr.shape[:2] != rgb.shape[:2]:
                self.im.remove()
                self.im = self.ax.imshow(
                    rgb,
                    interpolation="nearest",
                    aspect="equal",
                    origin="upper",
                )
            else:
                self.im.set_data(rgb)
        self.ax.set_title(f"Generation {self.generation}")
        c = count_cells(self.grid)
        self.status.configure(
            text=f"A={c['A']}  B={c['B']}  Inhibited={c['Inhibited']}  Empty={c['Empty']}"
        )
        self.canvas.draw_idle()


def run_gui() -> None:
    root = tk.Tk()
    CAApp(root)
    root.mainloop()
