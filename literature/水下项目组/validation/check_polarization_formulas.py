"""Independent algebra checks, NOT an author implementation or experiment.

Run: python check_polarization_formulas.py --output polarization_formula_checks.json
Requires numpy. Checks equations transcribed from the provided PDFs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def run_checks() -> dict:
    h = np.array([[1, .5, 0, .5], [.5, 1, .5, 0],
                  [0, .5, 1, .5], [.5, 0, .5, 1]], dtype=float)
    null_vector = np.array([1., -1., 1., -1.])
    background, modulation = 1., .6
    phase = np.linspace(-np.pi, np.pi, 101)
    signals = background + modulation * np.cos(
        phase[:, None] + np.array([0., np.pi/2, np.pi, 3*np.pi/2]))
    observations = signals @ h.T
    recovered = observations - background
    published_eq37 = observations - 2*background
    # Common additive offsets cancel in the ordinary four-step differences.
    delta_correct = np.arctan2(recovered[:, 3]-recovered[:, 1],
                               recovered[:, 0]-recovered[:, 2])
    delta_published = np.arctan2(published_eq37[:, 3]-published_eq37[:, 1],
                                 published_eq37[:, 0]-published_eq37[:, 2])
    theta, phi, kx = np.pi/4, np.pi/3, 0.
    ex, ey = np.cos(kx+phi), np.cos(kx-phi)
    incoherent = ex**2*np.cos(theta)**2 + ey**2*np.sin(theta)**2
    coherent = (ex*np.cos(theta) + ey*np.sin(theta))**2
    si12 = (np.sqrt(2)*np.cos(phi)*np.cos(kx))**2
    si13 = 2*np.cos(phi)**2 * (1+np.cos(2*kx))
    si15 = np.cos(phi)**2 * (1+np.cos(2*kx))
    checks = {
        "UW02_ideal_H_rank": int(np.linalg.matrix_rank(h)),
        "UW02_ideal_H_singular_values": np.linalg.svd(h, compute_uv=False).tolist(),
        "UW02_null_vector_residual": float(np.linalg.norm(h @ null_vector)),
        "UW02_subtract_A_max_recovery_error": float(np.max(np.abs(recovered-signals))),
        "UW02_published_subtract_2A_max_recovery_error": float(np.max(np.abs(published_eq37-signals))),
        "UW02_common_offset_four_step_phase_difference_max_rad":
            float(np.max(np.abs(np.angle(np.exp(1j*(delta_correct-delta_published)))))),
        "UW03_test_theta_phi_kx_rad": [theta, phi, kx],
        "UW03_main_eq4_intensity_test": float(incoherent),
        "UW03_coherent_analyzer_intensity_test": float(coherent),
        "UW03_SI12_squared_test": float(si12),
        "UW03_SI13_published_test": float(si13),
        "UW03_SI15_test": float(si15),
        "UW02_sin_squared_1_to_1p5_degree_leakage_percent":
            (np.sin(np.deg2rad([1., 1.5]))**2 * 100).tolist(),
    }
    assert checks["UW02_ideal_H_rank"] == 3
    assert checks["UW02_null_vector_residual"] < 1e-12
    assert checks["UW02_subtract_A_max_recovery_error"] < 1e-12
    assert abs(checks["UW02_published_subtract_2A_max_recovery_error"]-1) < 1e-12
    assert checks["UW02_common_offset_four_step_phase_difference_max_rad"] < 1e-12
    assert abs(coherent-incoherent) > .1
    assert abs(si12-si15) < 1e-12
    assert abs(si13-2*si12) < 1e-12
    return {
        "description": "Independent equation consistency checks; not experimental verification, not author code.",
        "sources": {"UW02": "10.1002/lpor.202502703 equations 34-37, page 14 error analysis",
                    "UW03": "10.1021/acs.nanolett.5c02789 equations 4-5 and SI equations S12-S15"},
        "caveats": ["A is the same background defined in equations 34-35; a different code normalization may change the interpretation.",
                    "A common intensity offset can cancel in four-step phase differences; this does not validate DoLP or absolute intensity.",
                    "The incoherent and analyzer examples are different observation models, illustrating the missing cross term.",
                    "No device simulation, author dataset, water propagation or reconstructed point cloud was tested."],
        "checks": checks,
        "assertions_passed": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(run_checks(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
