from __future__ import annotations

import csv
from pathlib import Path

import pytest

from blueprint_core.fabrication.sem_calibration import (
    SIDE_TO_EDGE_OFFSET,
    derive_sem_correction_profile,
    evaluate_radial_even_polynomial,
    read_sem_measurements,
    write_correction_csv,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data" / "SEM_air_hole_size.csv"


def _profile():
    measurements = read_sem_measurements(SOURCE)
    return measurements, derive_sem_correction_profile(
        measurements,
        total_shells=40,
        period_um=0.82,
        target_cd_nm=220.0,
        reference_min_layer=22,
        fit_order=2,
        process_gain=1.0,
        source_sha256="a" * 64,
    )


def test_real_sem_csv_is_strictly_reproducible() -> None:
    measurements = read_sem_measurements(SOURCE)

    assert len(measurements) == 29
    assert measurements[0].layer_outside_in == 1
    assert measurements[0].samples_nm == pytest.approx((307.0, 310.89, 300.0))
    assert measurements[0].trimmed_mean_nm == pytest.approx(307.0)
    assert measurements[-1].layer_outside_in == 35
    assert measurements[-1].trimmed_mean_nm == pytest.approx(220.405625)


def test_profile_maps_outer_layers_to_parent_shells_and_fills_missing_rows() -> None:
    _, profile = _profile()

    assert len(profile.rows) == 40
    assert profile.rows[0]["layer_outside_in"] == 1
    assert profile.rows[0]["parent_shell"] == 40
    assert profile.rows[-1]["layer_outside_in"] == 40
    assert profile.rows[-1]["parent_shell"] == 1
    assert profile.rows[23]["data_status"] == "interpolated"
    assert profile.rows[35]["data_status"] == "inner_reference_hold"
    assert profile.reference_sem_nm == pytest.approx(220.341325)


def test_triangle_side_compensation_converts_to_parallel_edge_offset() -> None:
    _, profile = _profile()
    outer = profile.rows[0]

    assert outer["tabulated_side_compensation_nm"] == pytest.approx(
        profile.target_cd_nm - 307.0
    )
    assert outer["tabulated_edge_offset_nm"] == pytest.approx(
        outer["tabulated_side_compensation_nm"] / SIDE_TO_EDGE_OFFSET
    )


def test_radial_fit_anchors_center_to_target_and_has_stable_coefficients() -> None:
    _, profile = _profile()

    assert profile.target_cd_nm == pytest.approx(220.0)
    assert profile.coefficients_nm == pytest.approx(
        (-0.09853204031556974, 5.134538035287714, -30.140260018739795),
        abs=1e-12,
    )
    assert evaluate_radial_even_polynomial(
        0.0, profile.coefficients_nm
    ) == pytest.approx(-0.09853204031556974, abs=1e-12)
    assert evaluate_radial_even_polynomial(1.0, profile.coefficients_nm) == pytest.approx(
        -25.104254023767652, abs=1e-12
    )
    assert profile.fit_rmse_edge_offset_nm == pytest.approx(0.5664, abs=1e-4)
    assert profile.fit_max_abs_edge_offset_nm < 1.34


def test_correction_csv_is_complete_and_self_describing(tmp_path: Path) -> None:
    _, profile = _profile()
    output = tmp_path / "correction.csv"

    write_correction_csv(output, profile)
    with output.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 40
    assert rows[0]["fit_kind"] == "radial_even_polynomial"
    assert rows[0]["fit_order"] == "2"
    assert float(rows[0]["target_cd_nm"]) == pytest.approx(220.0)
    assert float(rows[0]["fit_c0_edge_offset_nm"]) == pytest.approx(
        -0.09853204031556974
    )
    assert float(rows[0]["envelope_radius_um"]) == pytest.approx(32.8)
    assert rows[0]["source_sha256"] == "a" * 64
