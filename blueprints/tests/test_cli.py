from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from blueprint_core.cli import (
    BLUEPRINT_PROJECT_ROOT,
    _finalize_staging,
    build_parser,
    generate_blueprint,
)
from blueprint_core.config import load_blueprint_config
from blueprint_core.output.reporting import case_name, dxf_artifact_name


SOURCE_PARAMETER = Path(__file__).resolve().parents[1] / "main" / "parameter.json"


def _is_regular_output(path: Path) -> bool:
    resolved = str(path.resolve())
    if os.name == "nt":
        resolved = "\\\\?\\" + resolved
    return os.path.isfile(resolved) and not os.path.islink(resolved)


def _small_data() -> dict:
    data = json.loads(SOURCE_PARAMETER.read_text(encoding="utf-8"))
    data["project"]["name"] = "small_cli_contract"
    data["geometry"]["finite"]["cavity_layers"] = 1
    data["geometry"]["finite"]["cladding_layers"] = 1
    data["fabrication"]["spatial_envelope"]["half_size_um"] = [5.0, 5.0]
    data["outer_etch_windows"] = {"kind": "none"}
    data["markers"] = {"kind": "none"}
    data["source_trace"] = None
    return data


def _write_config(tmp_path: Path, data: dict, name: str = "parameter.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _small_config(tmp_path: Path) -> Path:
    return _write_config(tmp_path, _small_data())


def _make_process_ready(data: dict) -> None:
    data["fabrication"].update(
        {
            "profile_id": "calibrated-test-profile",
            "revision": "1",
            "provenance": "unit-test calibration fixture",
        }
    )
    data["dose"].update(
        {
            "kind": "scalar",
            "value": 100.0,
            "unit": "uC/cm^2",
        }
    )
    data["layout"]["polarity"] = "clear"
    for key in (
        "min_hole_width_nm",
        "min_edge_nm",
        "min_bridge_nm",
        "boundary_clearance_nm",
    ):
        data["drc"][key] = 0.0


def test_default_cli_config_is_in_main_directory() -> None:
    args = build_parser().parse_args([])
    assert args.config == BLUEPRINT_PROJECT_ROOT / "main" / "parameter.json"
    assert args.config == SOURCE_PARAMETER


def test_checked_in_config_has_parameter_readable_dxf_name() -> None:
    config = load_blueprint_config(SOURCE_PARAMETER)
    resolved_case_name = case_name(config.data, config.identity_sha256)
    resolved_dxf_name = dxf_artifact_name(config.data, config.identity_sha256)
    assert config.identity_sha256[:8] not in resolved_case_name
    assert config.identity_sha256[:8] not in resolved_dxf_name
    assert resolved_case_name == (
        "dxf_15-15_cav(245-0.96-1.156)_clad(242-0.98-0.93)_"
        "shift(0-0)_(-10,1)"
    )
    assert resolved_dxf_name == (
        "dxf_15-15_cav(245-0.96-1.156)_clad(242-0.98-0.93)_"
        "shift(0-0)_sem-air-hole-220nm-radial-v1-unassigned-r1_(-10,1).dxf"
    )


def test_generate_engineering_layout_keeps_three_file_contract(tmp_path: Path) -> None:
    config = load_blueprint_config(_small_config(tmp_path))
    result = generate_blueprint(config)
    dxf_name = dxf_artifact_name(config.data, config.identity_sha256)

    assert result.drc.passed
    assert result.feature_count == 114
    assert result.output_files == (
        dxf_name,
        "layout_report.json",
        "preview.png",
    )
    assert result.case_dir is not None
    output_entries = list(result.case_dir.iterdir())
    assert {path.name for path in output_entries} == set(result.output_files)
    assert all(_is_regular_output(path) for path in output_entries)

    report = json.loads((result.case_dir / "layout_report.json").read_text(encoding="utf-8"))
    assert report["outputs"]["artifact_count"] == 3
    assert report["outputs"]["artifact_names"] == sorted(result.output_files)
    assert set(report["outputs"]["sha256"]) == {
        dxf_name,
        "preview.png",
    }
    assert report["outputs"]["sha256_exclusions"] == {
        "layout_report.json": "self-referential artifact"
    }
    assert report["dxf"]["entity_count"] == 114
    assert report["drc"]["passed"] is True
    assert report["config"]["resolved"]["dose"]["kind"] == "unassigned"
    source = report["software"]["blueprint_source"]
    assert len(source["tree_sha256"]) == 64
    assert source["file_count"] == len(source["files"])
    assert "workflow/cli.py" in source["files"]
    assert isinstance(source["git"]["available"], bool)


def test_released_and_engineering_artifacts_have_distinct_identity_and_names(
    tmp_path: Path,
) -> None:
    engineering_data = _small_data()
    _make_process_ready(engineering_data)
    released_data = json.loads(json.dumps(engineering_data))
    released_data["project"]["release_status"] = "released"
    released_data["export"]["mode"] = "released"
    released_data['fabrication']['triangle_side_correction'][
        'global_delta_nm'
    ] = -9.0

    engineering = load_blueprint_config(
        _write_config(tmp_path, engineering_data, "engineering.json")
    )
    released = load_blueprint_config(
        _write_config(tmp_path, released_data, "released.json")
    )
    assert engineering.identity_sha256 != released.identity_sha256

    engineering_result = generate_blueprint(engineering)
    released_result = generate_blueprint(released)
    assert engineering_result.case_name != released_result.case_name
    assert engineering_result.case_name.endswith('_(-10,1)')
    assert released_result.case_name.endswith('_(-9,1)')
    assert engineering_result.case_name == case_name(
        engineering.data, engineering.identity_sha256
    )
    assert released_result.case_name == case_name(
        released.data, released.identity_sha256
    )
    engineering_dxf = dxf_artifact_name(engineering.data, engineering.identity_sha256)
    released_dxf = dxf_artifact_name(released.data, released.identity_sha256)
    assert engineering_dxf != released_dxf
    assert engineering_result.output_files == (
        engineering_dxf,
        "layout_report.json",
        "preview.png",
    )
    assert released_result.output_files == (
        released_dxf,
        "layout_report.json",
        "preview.png",
    )
    assert engineering_result.case_dir != released_result.case_dir

    assert released_result.case_dir is not None
    released_entries = list(released_result.case_dir.iterdir())
    assert len(released_entries) == 3
    assert all(_is_regular_output(path) for path in released_entries)
    released_report = json.loads(
        (released_result.case_dir / "layout_report.json").read_text(encoding="utf-8")
    )
    assert released_report["release_status"] == "released"
    assert released_report["outputs"]["artifact_names"] == [
        released_dxf,
        "layout_report.json",
        "preview.png",
    ]
    assert set(released_report["outputs"]["sha256"]) == {
        released_dxf,
        "preview.png",
    }


def test_output_affecting_export_settings_change_identity(tmp_path: Path) -> None:
    first_data = _small_data()
    second_data = json.loads(json.dumps(first_data))
    second_data["export"]["dpi"] += 1

    first = load_blueprint_config(_write_config(tmp_path, first_data, "first.json"))
    second = load_blueprint_config(_write_config(tmp_path, second_data, "second.json"))

    assert first.identity_sha256 != second.identity_sha256


def test_preflight_writes_nothing(tmp_path: Path) -> None:
    config = load_blueprint_config(_small_config(tmp_path))
    result = generate_blueprint(config, preflight_only=True)
    assert result.preflight_only
    assert result.case_dir is None
    assert result.output_files == ()
    assert not config.output_root.exists()


def test_existing_case_is_never_overwritten(tmp_path: Path) -> None:
    config = load_blueprint_config(_small_config(tmp_path))
    generate_blueprint(config)
    with pytest.raises(FileExistsError, match="already exists"):
        generate_blueprint(config)


def test_staging_finalize_rejects_unknown_directories(tmp_path: Path) -> None:
    staging = tmp_path / ".staging-case"
    staging.mkdir()
    expected = {"dxf_fixture.dxf", "preview.png", "layout_report.json"}
    for name in expected:
        (staging / name).write_bytes(b"fixture")
    (staging / "unexpected").mkdir()

    with pytest.raises(RuntimeError, match="non-regular entries"):
        _finalize_staging(staging, tmp_path / "target", expected)


def test_staging_finalize_rechecks_target_before_rename(tmp_path: Path) -> None:
    staging = tmp_path / ".staging-case"
    staging.mkdir()
    expected = {"dxf_fixture.dxf", "preview.png", "layout_report.json"}
    for name in expected:
        (staging / name).write_bytes(b"fixture")
    target = tmp_path / "target"
    target.mkdir()

    with pytest.raises(FileExistsError, match="already exists"):
        _finalize_staging(staging, target, expected)
    assert staging.is_dir()
