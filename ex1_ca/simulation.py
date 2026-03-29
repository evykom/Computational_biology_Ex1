"""Run the CA for many generations and record population counts per step."""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

from ex1_ca.cellular_automaton import EMPTY, INHIBITED, STRAIN_A, STRAIN_B, random_init, step

PopulationCounts = Dict[str, int]


def count_cells(grid: List[List[int]]) -> PopulationCounts:
    a = b = inh = empty = 0
    for row in grid:
        for c in row:
            if c == EMPTY:
                empty += 1
            elif c == STRAIN_A:
                a += 1
            elif c == STRAIN_B:
                b += 1
            else:
                inh += 1
    total = a + b + inh + empty
    return {
        "A": a,
        "B": b,
        "Inhibited": inh,
        "Empty": empty,
        "Total": total,
    }


def run_simulation(
    rows: int,
    cols: int,
    generations: int,
    p_a: float,
    p_b: float,
    k: int,
    frac_a: float,
    frac_b: float,
    seed: int | None,
) -> Tuple[List[List[int]], List[PopulationCounts]]:
    rng = random.Random(seed)
    grid = random_init(rows, cols, frac_a, frac_b, rng)
    history: List[PopulationCounts] = []
    for _ in range(generations):
        history.append(count_cells(grid))
        grid = step(grid, p_a, p_b, k, rng)
    history.append(count_cells(grid))
    return grid, history
