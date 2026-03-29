"""Cellular automaton for Exercise 1 (spatial ecology, Kill-the-Winner dynamics)."""

from ex1_ca.cellular_automaton import (
    EMPTY,
    STRAIN_A,
    STRAIN_B,
    INHIBITED,
    make_grid,
    random_init,
    step,
)

__all__ = [
    "EMPTY",
    "STRAIN_A",
    "STRAIN_B",
    "INHIBITED",
    "make_grid",
    "random_init",
    "step",
]
