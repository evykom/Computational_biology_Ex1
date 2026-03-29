"""
Core CA rules: toroidal grid, synchronous update, reproduction conflict handling.

I count only healthy A cells toward the phage density threshold K (not Inhibited).
When several parents try to fill the same empty cell in one generation, I shuffle
the attempts and keep the first claim per target cell so only one strain wins.
"""

from __future__ import annotations

import random
from typing import List, Sequence, Tuple

# Cell states (ints for fast comparison in hot loops)
EMPTY = 0
STRAIN_A = 1
STRAIN_B = 2
INHIBITED = 3

Neighbor = Tuple[int, int]


def make_grid(rows: int, cols: int) -> List[List[int]]:
    return [[EMPTY for _ in range(cols)] for _ in range(rows)]


def _wrap(i: int, j: int, rows: int, cols: int) -> Neighbor:
    return i % rows, j % cols


def iter_moore8(i: int, j: int, rows: int, cols: int) -> Sequence[Neighbor]:
    out: List[Neighbor] = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            out.append(_wrap(i + di, j + dj, rows, cols))
    return out


def count_strain_a_neighbors(grid: List[List[int]], i: int, j: int, rows: int, cols: int) -> int:
    n = 0
    for ni, nj in iter_moore8(i, j, rows, cols):
        if grid[ni][nj] == STRAIN_A:
            n += 1
    return n


def random_init(
    rows: int,
    cols: int,
    frac_a: float,
    frac_b: float,
    rng: random.Random,
) -> List[List[int]]:
    """Place approximately frac_a / frac_b of cells as A / B on an otherwise empty grid."""
    total = rows * cols
    n_a = min(int(round(total * frac_a)), total)
    n_b = min(int(round(total * frac_b)), total - n_a)
    coords = [(i, j) for i in range(rows) for j in range(cols)]
    rng.shuffle(coords)
    grid = make_grid(rows, cols)
    k = 0
    for _ in range(n_a):
        i, j = coords[k]
        k += 1
        grid[i][j] = STRAIN_A
    for _ in range(n_b):
        i, j = coords[k]
        k += 1
        grid[i][j] = STRAIN_B
    return grid


def step(
    grid: List[List[int]],
    p_a: float,
    p_b: float,
    k: int,
    rng: random.Random,
) -> List[List[int]]:
    """
    One synchronous generation: inhibited cells clear, phage activation on A,
    then stochastic reproduction into cells that were empty at the start of the step.
    """
    rows = len(grid)
    cols = len(grid[0])
    next_grid = make_grid(rows, cols)
    will_inhibit = [[False] * cols for _ in range(rows)]

    for i in range(rows):
        for j in range(cols):
            state = grid[i][j]
            if state == INHIBITED:
                next_grid[i][j] = EMPTY
            elif state == STRAIN_A:
                if count_strain_a_neighbors(grid, i, j, rows, cols) >= k:
                    will_inhibit[i][j] = True
                    next_grid[i][j] = INHIBITED
                else:
                    next_grid[i][j] = STRAIN_A
            elif state == STRAIN_B:
                next_grid[i][j] = STRAIN_B
            else:
                next_grid[i][j] = EMPTY

    attempts: List[Tuple[int, int, int, int, int]] = []
    for i in range(rows):
        for j in range(cols):
            state = grid[i][j]
            if state == INHIBITED:
                continue
            if state == STRAIN_A and will_inhibit[i][j]:
                continue
            if state not in (STRAIN_A, STRAIN_B):
                continue

            empties: List[Neighbor] = []
            for ni, nj in iter_moore8(i, j, rows, cols):
                if grid[ni][nj] == EMPTY:
                    empties.append((ni, nj))
            if not empties:
                continue

            p = p_a if state == STRAIN_A else p_b
            if rng.random() >= p:
                continue

            ti, tj = empties[rng.randrange(len(empties))]
            strain = STRAIN_A if state == STRAIN_A else STRAIN_B
            attempts.append((ti, tj, strain, i, j))

    rng.shuffle(attempts)
    winner: dict[Tuple[int, int], int] = {}
    for ti, tj, strain, _pi, _pj in attempts:
        key = (ti, tj)
        if key in winner:
            continue
        winner[key] = strain

    for (ti, tj), strain in winner.items():
        if grid[ti][tj] == EMPTY:
            next_grid[ti][tj] = strain

    return next_grid
