from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from blueprint_core.quality.drc import DrcError, run_drc
from blueprint_core.models import LayoutFeature, LayoutPlan


def _feature(identifier: str, polygon: Polygon) -> LayoutFeature:
    return LayoutFeature(
        identifier,
        "cavity",
        0,
        0,
        0,
        0,
        0,
        polygon,
        polygon,
        (0.0, 0.0),
    )


def _square(x: float, y: float, size: float = 1.0) -> Polygon:
    return Polygon([(x, y), (x + size, y), (x + size, y + size), (x, y + size)])


def _plan(*features: LayoutFeature, boundary: Polygon | None = None) -> LayoutPlan:
    return LayoutPlan(
        "synthetic",
        list(features),
        boundary if boundary is not None else _square(-2.0, -2.0, 10.0),
        {},
    )


def _rules(**updates: object) -> dict[str, object]:
    rules: dict[str, object] = {
        "min_hole_width_nm": None,
        "min_edge_nm": None,
        "min_bridge_nm": None,
        "boundary_clearance_nm": None,
        "fail_on_warning": False,
    }
    rules.update(updates)
    return rules


def _rule_names(report) -> set[str]:
    return {violation.rule for violation in report.violations}


def test_clean_layout_passes_nullable_engineering_rules() -> None:
    report = run_drc(
        _plan(_feature("a", _square(0.0, 0.0))),
        _rules(),
    )
    assert report.passed
    assert report.to_dict()["error_count"] == 0
    assert report.metrics["valid_polygon_count"] == 1


def test_minimum_width_and_edge_are_checked_independently() -> None:
    thin = _feature("thin", _square(0.0, 0.0, 0.05))
    report = run_drc(
        _plan(thin),
        _rules(min_hole_width_nm=100.0, min_edge_nm=60.0),
    )
    assert {"min_hole_width", "min_edge_length"}.issubset(_rule_names(report))
    assert not report.passed


def test_duplicate_overlap_and_duplicate_id_are_detected() -> None:
    first = _feature("same", _square(0.0, 0.0))
    duplicate = _feature("same", _square(0.0, 0.0))
    overlap = _feature("overlap", _square(0.5, 0.0))
    report = run_drc(_plan(first, duplicate, overlap), _rules())
    names = _rule_names(report)
    assert "duplicate_feature_id" in names
    assert "duplicate_polygon" in names
    assert "feature_overlap" in names


def test_minimum_bridge_uses_polygon_distance() -> None:
    first = _feature("a", _square(0.0, 0.0))
    second = _feature("b", _square(1.05, 0.0))
    report = run_drc(_plan(first, second), _rules(min_bridge_nm=100.0))
    bridge = next(item for item in report.violations if item.rule == "min_bridge")
    assert bridge.measured == pytest.approx(0.05)
    assert bridge.limit == pytest.approx(0.1)


def test_boundary_containment_and_clearance_are_checked() -> None:
    boundary = _square(0.0, 0.0, 2.0)
    near = _feature("near", _square(0.05, 0.5, 0.5))
    outside = _feature("outside", _square(1.8, 0.5, 0.5))
    report = run_drc(
        _plan(near, outside, boundary=boundary),
        _rules(boundary_clearance_nm=100.0),
    )
    assert "boundary_clearance" in _rule_names(report)
    assert "boundary_containment" in _rule_names(report)


def test_external_auxiliary_feature_skips_only_finite_boundary_check() -> None:
    boundary = _square(0.0, 0.0, 2.0)
    internal = _feature("internal", _square(0.5, 0.5, 0.5))
    external = _feature("external", _square(3.0, 0.0, 1.0))
    external.region = "outer_etch_window"
    external.metadata["boundary_check"] = False
    report = run_drc(
        _plan(internal, external, boundary=boundary),
        _rules(),
    )
    assert report.passed
    assert "boundary_containment" not in _rule_names(report)
    assert report.metrics["valid_polygon_count"] == 2


def test_address_grid_can_come_from_layout_correction_metadata() -> None:
    feature = _feature("off-grid", _square(0.0004, 0.0))
    plan = _plan(feature)
    plan.metadata["correction_pipeline"] = {
        "grid_um": 0.001,
        "grid_origin_um": [0.0, 0.0],
    }
    report = run_drc(plan, _rules())
    assert "address_grid" in _rule_names(report)


def test_degenerate_polygon_and_layer_allowlist_are_reported() -> None:
    degenerate = Polygon([(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)])
    feature = _feature("bad", degenerate)
    feature.dxf_layer = "ANNOTATION"
    report = run_drc(
        _plan(feature),
        {**_rules(), "allowed_dxf_layers": ["ETCH"]},
    )
    assert {"degenerate_polygon", "dxf_layer"}.issubset(_rule_names(report))


def test_warning_policy_controls_release_gate() -> None:
    thin = _feature("thin", _square(0.0, 0.0, 0.05))
    warning_rules = {
        **_rules(min_hole_width_nm=100.0),
        "severity_by_rule": {"min_hole_width": "warning"},
    }
    report = run_drc(_plan(thin), warning_rules)
    assert report.passed
    strict_report = run_drc(
        _plan(thin),
        {**warning_rules, "fail_on_warning": True},
    )
    assert not strict_report.passed
    with pytest.raises(DrcError):
        strict_report.raise_for_errors()
