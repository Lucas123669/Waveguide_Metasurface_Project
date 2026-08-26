import math
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from gwm_workflow.config import load_config
from gwm_workflow.phase_design import (
    beam_deflection,
    build_phase_targets,
    circular_phase_error,
    metalens_phase,
    wrap_phase,
)


def config(name):
    return load_config(os.path.join(os.path.dirname(__file__), "..", "configs", name))


def test_phase_wrap_and_distance():
    assert math.isclose(wrap_phase(3.0 * math.pi), -math.pi)
    assert circular_phase_error(math.pi - 0.1, -math.pi + 0.1) < 0.21


def test_beam_seed_has_one_radiating_direction():
    result = beam_deflection(1.55, 2.4, 0.575, -1.0)
    assert result["forward_radiates"]
    assert not result["reverse_radiates"]
    assert 15.0 < result["reported_angle_deg"] < 20.0


def test_deflector_target_count_and_periodicity():
    design = config("beam_deflector_1550nm.json")["design"]
    rows = build_phase_targets(design)
    assert len(rows) == design["atoms_per_supercell"] * design["supercell_count"]
    assert [row["atom_id"] for row in rows[:3]] == [
        "phase_plus_2pi_3_seed",
        "phase_zero_seed",
        "phase_minus_2pi_3_seed",
    ]


def test_metalens_phase_and_layout_are_finite():
    design = config("metalens_1550nm.json")["design"]
    assert -math.pi <= metalens_phase(0.0, 1.55, 3.1, 5.0) < math.pi
    rows = build_phase_targets(design)
    assert len(rows) == 40
    assert all(math.isfinite(row["phase_error_rad"]) for row in rows)


if __name__ == "__main__":
    test_phase_wrap_and_distance()
    test_beam_seed_has_one_radiating_direction()
    test_deflector_target_count_and_periodicity()
    test_metalens_phase_and_layout_are_finite()
    print("phase-design tests passed")
