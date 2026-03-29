"""Command-line interface for the CA simulator."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ex1_ca.simulation import run_simulation


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Toroidal CA: Kill-the-Winner style two-strain competition.",
    )
    p.add_argument("--rows", type=int, default=200, help="Grid height (default 200).")
    p.add_argument("--cols", type=int, default=200, help="Grid width (default 200).")
    p.add_argument("--generations", type=int, default=500, help="Number of generations to run.")
    p.add_argument(
        "--p-a",
        type=float,
        default=0.35,
        help="Reproduction probability for strain A (P_A). Default 0.35.",
    )
    p.add_argument(
        "--p-b",
        type=float,
        default=0.12,
        help="Reproduction probability for strain B (P_B). Default 0.12.",
    )
    p.add_argument(
        "--k",
        type=int,
        default=4,
        help="Min healthy-A neighbors to trigger phage; use 9 to disable. Default 4.",
    )
    p.add_argument("--init-a", type=float, default=0.02, help="Initial fraction of A cells (default 0.02).")
    p.add_argument("--init-b", type=float, default=0.02, help="Initial fraction of B cells (default 0.02).")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional CSV path for population time series (generation, A, B, Inhibited, Empty).",
    )
    p.add_argument("--quiet", action="store_true", help="Do not print the last snapshot to stdout.")
    p.add_argument(
        "--gui",
        action="store_true",
        help="Open the interactive grid window (matplotlib + tkinter) instead of batch mode.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.gui:
        from ex1_ca.gui import run_gui

        run_gui()
        return 0

    _grid, history = run_simulation(
        rows=args.rows,
        cols=args.cols,
        generations=args.generations,
        p_a=args.p_a,
        p_b=args.p_b,
        k=args.k,
        frac_a=args.init_a,
        frac_b=args.init_b,
        seed=args.seed,
    )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["generation", "A", "B", "Inhibited", "Empty", "Total"])
            for gen, counts in enumerate(history):
                w.writerow(
                    [
                        gen,
                        counts["A"],
                        counts["B"],
                        counts["Inhibited"],
                        counts["Empty"],
                        counts["Total"],
                    ]
                )

    if not args.quiet:
        last = history[-1]
        print(
            f"After {args.generations} generations: "
            f"A={last['A']} B={last['B']} Inhibited={last['Inhibited']} Empty={last['Empty']}"
        )
    return 0
