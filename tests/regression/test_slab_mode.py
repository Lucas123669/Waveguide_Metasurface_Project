"""Regression test: L01 case_001 slab-mode effective indices vs known values."""

import os
import sys

case_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "experiments", "l01_huang_2023", "case_001_slab_mode")
)
sys.path.insert(0, os.path.join(case_root, "scripts"))

from slab_mode_solver import load_config, solve_modes  # noqa: E402


def test_tm0_matches_known_value():
    config = load_config(os.path.join(case_root, "params.json"))
    roots, _ = solve_modes(config, tm=True)
    assert abs(roots[0] - 1.5507) < 0.005, f"TM0 n_eff={roots[0]:.4f}"


def test_te0_matches_known_value():
    config = load_config(os.path.join(case_root, "params.json"))
    roots, _ = solve_modes(config, tm=False)
    assert abs(roots[0] - 1.6759) < 0.005, f"TE0 n_eff={roots[0]:.4f}"
