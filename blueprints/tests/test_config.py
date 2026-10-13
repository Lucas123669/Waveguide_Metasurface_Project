from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from blueprint_core.config import (
    load_blueprint_config,
    resolve_outer_window_radial_width_um,
)


PARAMETER_PATH = Path(__file__).resolve().parents[1] / "main" / "parameter.json"


def _write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "parameter.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _data() -> dict:
    return json.loads(PARAMETER_PATH.read_text(encoding="utf-8"))


def test_checked_in_engineering_config_is_self_contained() -> None:
    config = load_blueprint_config(PARAMETER_PATH)
    assert config.release_status == "engineering_preview"
    assert not config.is_released
    assert config.data["geometry"]["lattice"]["period_um"] == pytest.approx(0.82)
    assert config.data["geometry"]["finite"] == {
        "kind": "hex_shells_v1",
        "cavity_layers": 15,
        "cladding_layers": 15,
        "empty_buffer_periods": 0.5,
    }
    assert config.data["geometry"]["cladding_shift"]["x_factor"] == 0.0
    assert config.data["outer_etch_windows"]["kind"] == "segmented_hex_ring_windows_v2"
    assert config.data["outer_etch_windows"]["inner_clearance_um"] == pytest.approx(3.8)
    assert config.data["outer_etch_windows"]["radial_width"] == {
        "kind": "linear_from_total_finite_layers_v1",
        "slope_um_per_total_layer": 0.4,
        "intercept_um": -3.0,
    }
    assert resolve_outer_window_radial_width_um(
        config.data["outer_etch_windows"],
        config.data["geometry"],
    ) == pytest.approx(9.0)
    assert config.data["outer_etch_windows"]["parallel_side_gap_um"] == pytest.approx(5.0)
    assert config.data["outer_etch_windows"]["inner_corner_radius_um"] == pytest.approx(3.0)
    assert config.data["markers"]["kind"] == "seven_segment_parameter_label_v1"
    assert config.data["fabrication"]["profile_id"] == "sem-air-hole-220nm-radial-v1"
    assert config.data["fabrication"]["revision"] == "1"
    triangle = config.data['fabrication']['triangle_side_correction']
    assert triangle['global_delta_nm'] == pytest.approx(-10.0)
    assert triangle['envelope_modulation_strength'] == pytest.approx(1.0)
    assert triangle['regions'] == ['cavity', 'cladding']
    assert config.data['fabrication']['local_correction']['default']['operators'][0][
        'value_nm'
    ] == pytest.approx(0.0)
    assert config.data["fabrication"]["spatial_envelope"]["regions"] == [
        "cavity",
        "cladding",
    ]
    assert config.data["dose"]["kind"] == "unassigned"
    assert (
        config.data["export"]["preview_layout"]
        == "radial_three_position_correction_compact_wide_v4"
    )
    assert config.output_root == (PARAMETER_PATH.parent / ".out").resolve()
    assert len(config.identity_sha256) == 64


def test_unknown_fields_are_rejected(tmp_path: Path) -> None:
    data = _data()
    data["geometry"]["lattice"]["hidden_period"] = 0.82
    with pytest.raises(ValueError, match="unknown fields"):
        load_blueprint_config(_write(tmp_path, data))


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("outer_etch_windows", "parallel_side_gap_um"),
        ("markers", "digit_height_um"),
    ],
)
def test_auxiliary_geometry_requires_positive_dimensions(
    tmp_path: Path,
    section: str,
    field: str,
) -> None:
    data = _data()
    data[section][field] = 0.0
    with pytest.raises(ValueError, match="must be positive"):
        load_blueprint_config(_write(tmp_path, data))


@pytest.mark.parametrize("regions", [[], ["cavity", "cavity"]])
def test_spatial_envelope_regions_must_be_nonempty_and_unique(
    tmp_path: Path,
    regions: list[str],
) -> None:
    data = _data()
    data["fabrication"]["spatial_envelope"]["regions"] = regions
    with pytest.raises(ValueError, match="regions"):
        load_blueprint_config(_write(tmp_path, data))


def test_triangle_side_correction_strength_zero_is_valid(tmp_path: Path) -> None:
    data = _data()
    data['fabrication']['triangle_side_correction'][
        'envelope_modulation_strength'
    ] = 0.0
    config = load_blueprint_config(_write(tmp_path, data))
    assert config.data['fabrication']['triangle_side_correction'][
        'envelope_modulation_strength'
    ] == pytest.approx(0.0)


def test_triangle_side_correction_rejects_negative_strength(
    tmp_path: Path,
) -> None:
    data = _data()
    data['fabrication']['triangle_side_correction'][
        'envelope_modulation_strength'
    ] = -0.1
    with pytest.raises(ValueError, match='must be non-negative'):
        load_blueprint_config(_write(tmp_path, data))


def test_triangle_side_and_envelope_regions_must_match(tmp_path: Path) -> None:
    data = _data()
    data['fabrication']['triangle_side_correction']['regions'] = ['cavity']
    with pytest.raises(ValueError, match='must exactly match'):
        load_blueprint_config(_write(tmp_path, data))


def test_region_specific_local_correction_is_strict(tmp_path: Path) -> None:
    data = _data()
    data["fabrication"]["local_correction"]["by_region"]["parameter_marker"][
        "hidden_bias_nm"
    ] = 10.0
    with pytest.raises(ValueError, match="unknown fields"):
        load_blueprint_config(_write(tmp_path, data))


def test_release_gate_rejects_unassigned_process(tmp_path: Path) -> None:
    data = _data()
    data["project"]["release_status"] = "released"
    data["export"]["mode"] = "released"
    data["fabrication"]["profile_id"] = "engineering-unassigned"
    with pytest.raises(ValueError, match="calibrated fabrication.profile_id"):
        load_blueprint_config(_write(tmp_path, data))


def test_output_root_cannot_escape_project(tmp_path: Path) -> None:
    data = _data()
    data["export"]["output_root"] = "../outside"
    with pytest.raises(ValueError, match="must stay inside"):
        load_blueprint_config(_write(tmp_path, data))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("flatten", False, "export.flatten must be true in v1"),
        (
            "debug_artifacts",
            True,
            "export.debug_artifacts=true is not supported in v1",
        ),
        (
            "preview_layout",
            "legacy_summary_v1",
            "export.preview_layout",
        ),
    ],
)
def test_v1_rejects_unsupported_export_modes(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    data = _data()
    data["export"][field] = value
    with pytest.raises(ValueError, match=message):
        load_blueprint_config(_write(tmp_path, data))


def test_scalar_dose_requires_value_and_unit(tmp_path: Path) -> None:
    data = deepcopy(_data())
    data["dose"]["kind"] = "scalar"
    with pytest.raises(TypeError, match="dose.value"):
        load_blueprint_config(_write(tmp_path, data))


@pytest.mark.parametrize("power", [-0.5, 0.0, 0.5, 1.0])
def test_tanh_power_profile_requires_power_greater_than_one(
    tmp_path: Path,
    power: float,
) -> None:
    data = _data()
    data["geometry"]["cladding_shift"]["profile"] = {
        "kind": "tanh_power",
        "scale_layers": 3.0,
        "power": power,
    }
    with pytest.raises(ValueError, match="power must be greater than 1"):
        load_blueprint_config(_write(tmp_path, data))


def test_tanh_power_profile_accepts_power_above_one(tmp_path: Path) -> None:
    data = _data()
    data["geometry"]["cladding_shift"]["profile"] = {
        "kind": "tanh_power",
        "scale_layers": 3.0,
        "power": 1.000001,
    }

    config = load_blueprint_config(_write(tmp_path, data))

    assert config.data["geometry"]["cladding_shift"]["profile"][
        "power"
    ] == pytest.approx(1.000001)


def test_v2_outer_windows_allow_zero_inner_clearance(tmp_path: Path) -> None:
    data = _data()
    data["outer_etch_windows"]["inner_clearance_um"] = 0.0

    config = load_blueprint_config(_write(tmp_path, data))

    assert config.data["outer_etch_windows"]["inner_clearance_um"] == 0.0


@pytest.mark.parametrize(
    ("cavity_layers", "cladding_layers", "expected_height_um"),
    [
        (15, 15, 9.0),
        (20, 20, 13.0),
        (20, 15, 11.0),
    ],
)
def test_v2_outer_window_height_follows_total_finite_layers(
    tmp_path: Path,
    cavity_layers: int,
    cladding_layers: int,
    expected_height_um: float,
) -> None:
    data = _data()
    data["geometry"]["finite"]["cavity_layers"] = cavity_layers
    data["geometry"]["finite"]["cladding_layers"] = cladding_layers

    config = load_blueprint_config(_write(tmp_path, data))

    assert resolve_outer_window_radial_width_um(
        config.data["outer_etch_windows"],
        config.data["geometry"],
    ) == pytest.approx(expected_height_um)


def test_v2_outer_window_height_rule_requires_positive_slope(
    tmp_path: Path,
) -> None:
    data = _data()
    data["outer_etch_windows"]["radial_width"][
        "slope_um_per_total_layer"
    ] = 0.0

    with pytest.raises(ValueError, match="must be positive"):
        load_blueprint_config(_write(tmp_path, data))


def test_v2_outer_window_height_rule_must_resolve_positive(
    tmp_path: Path,
) -> None:
    data = _data()
    data["geometry"]["finite"]["cavity_layers"] = 1
    data["geometry"]["finite"]["cladding_layers"] = 1

    with pytest.raises(ValueError, match="non-positive height"):
        load_blueprint_config(_write(tmp_path, data))


def test_v2_outer_window_rejects_fixed_height_and_rule_together(
    tmp_path: Path,
) -> None:
    data = _data()
    data["outer_etch_windows"]["radial_width_um"] = 9.0

    with pytest.raises(ValueError, match="exactly one"):
        load_blueprint_config(_write(tmp_path, data))


def test_v2_outer_window_height_rule_rejects_unknown_fields(
    tmp_path: Path,
) -> None:
    data = _data()
    data["outer_etch_windows"]["radial_width"]["hidden_scale"] = 1.0

    with pytest.raises(ValueError, match="unknown fields"):
        load_blueprint_config(_write(tmp_path, data))


def test_v2_outer_windows_reject_v1_only_fields(tmp_path: Path) -> None:
    data = _data()
    data["outer_etch_windows"]["inner_end_clearance_um"] = 1.0

    with pytest.raises(ValueError, match="unknown fields"):
        load_blueprint_config(_write(tmp_path, data))


def test_v1_outer_windows_remain_loadable_for_historical_configs(
    tmp_path: Path,
) -> None:
    data = _data()
    data["outer_etch_windows"] = {
        "kind": "segmented_hex_etch_windows_v1",
        "reference": "finite_boundary",
        "inner_clearance_um": 2.5,
        "radial_width_um": 8.0,
        "inner_end_clearance_um": 3.0,
        "outer_tangential_extension_um": 1.5,
        "corner_radius_um": 1.0,
        "arc_segments_per_quadrant": 8,
        "dxf_layer": "ETCH",
    }

    config = load_blueprint_config(_write(tmp_path, data))

    assert (
        config.data["outer_etch_windows"]["kind"]
        == "segmented_hex_etch_windows_v1"
    )
