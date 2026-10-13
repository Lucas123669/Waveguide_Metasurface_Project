from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
from shapely.geometry import Polygon

from blueprint_core.geometry.auxiliary import (
    add_auxiliary_geometry,
    build_outer_etch_windows,
    build_parameter_marker,
    parameter_label_text,
)
from blueprint_core.models import LayoutPlan


PARAMETER_PATH = Path(__file__).resolve().parents[1] / "main" / "parameter.json"


def _config() -> dict:
    return json.loads(PARAMETER_PATH.read_text(encoding="utf-8"))


def _hex_boundary(size_um: float = 20.0) -> Polygon:
    root3 = 3.0**0.5
    return Polygon(
        (
            (size_um / 2.0, 0.0),
            (size_um / 4.0, root3 * size_um / 4.0),
            (-size_um / 4.0, root3 * size_um / 4.0),
            (-size_um / 2.0, 0.0),
            (-size_um / 4.0, -root3 * size_um / 4.0),
            (size_um / 4.0, -root3 * size_um / 4.0),
        )
    )


def _empty_layout() -> LayoutPlan:
    return LayoutPlan("synthetic_hex", [], _hex_boundary(), {})


def _build_windows(
    boundary: Polygon,
    config: dict,
) -> list:
    return build_outer_etch_windows(
        boundary,
        config,
        geometry=_config()["geometry"],
    )


def test_outer_windows_create_six_disjoint_external_etch_features() -> None:
    config = _config()
    windows = _build_windows(
        _hex_boundary(),
        config["outer_etch_windows"],
    )

    assert len(windows) == 6
    assert {feature.region for feature in windows} == {"outer_etch_window"}
    assert {feature.dxf_layer for feature in windows} == {"ETCH"}
    assert all(feature.metadata["boundary_check"] is False for feature in windows)
    assert all(feature.polygon.is_valid and feature.polygon.area > 0.0 for feature in windows)
    for index, first in enumerate(windows):
        for second in windows[index + 1 :]:
            assert not first.polygon.intersects(second.polygon)


def test_parameter_marker_text_matches_compact_cell_parameters_exactly() -> None:
    config = _config()
    assert parameter_label_text(config["geometry"], config["markers"]) == (
        "245.0 0.96 1.156 — 242.0 0.98 0.93"
    )


def test_parameter_marker_is_centered_below_outer_windows() -> None:
    config = _config()
    layout = _empty_layout()
    windows = _build_windows(
        layout.boundary,
        config["outer_etch_windows"],
    )
    markers, display_text = build_parameter_marker(
        layout,
        config["geometry"],
        config["markers"],
        outer_windows=windows,
    )

    assert display_text == "245.0 0.96 1.156 — 242.0 0.98 0.93"
    assert len(markers) == 116
    assert {feature.region for feature in markers} == {"parameter_marker"}
    marker_min_x = min(feature.polygon.bounds[0] for feature in markers)
    marker_max_x = max(feature.polygon.bounds[2] for feature in markers)
    marker_max_y = max(feature.polygon.bounds[3] for feature in markers)
    window_min_y = min(feature.polygon.bounds[1] for feature in windows)
    assert 0.5 * (marker_min_x + marker_max_x) == pytest.approx(0.0, abs=1e-12)
    assert window_min_y - marker_max_y == pytest.approx(
        config["markers"]["top_clearance_um"]
    )
    assert all(feature.metadata["preview_comparison"] is False for feature in markers)


def test_auxiliary_summary_records_display_text_and_feature_counts() -> None:
    config = _config()
    augmented = add_auxiliary_geometry(
        _empty_layout(),
        geometry=config["geometry"],
        outer_etch_windows=config["outer_etch_windows"],
        markers=config["markers"],
    )

    summary = augmented.metadata["auxiliary_geometry"]
    assert augmented.feature_count == 122
    assert summary["outer_etch_windows"]["feature_count"] == 6
    assert summary["outer_etch_windows"]["radial_width_um"] == pytest.approx(9.0)
    assert summary["outer_etch_windows"]["finite_total_layers"] == 30
    assert summary["outer_etch_windows"]["radial_width_rule"] == {
        "kind": "linear_from_total_finite_layers_v1",
        "slope_um_per_total_layer": 0.4,
        "intercept_um": -3.0,
    }
    assert summary["parameter_marker"]["feature_count"] == 116
    assert summary["parameter_marker"]["display_text"] == (
        "245.0 0.96 1.156 — 242.0 0.98 0.93"
    )


def test_none_auxiliary_kinds_preserve_empty_layout() -> None:
    layout = _empty_layout()
    augmented = add_auxiliary_geometry(
        layout,
        geometry=_config()["geometry"],
        outer_etch_windows={"kind": "none"},
        markers={"kind": "none"},
    )
    assert augmented.feature_count == 0
    assert augmented.boundary.equals(layout.boundary)


def test_v2_inner_edges_are_symmetrically_trimmed_for_parallel_gap() -> None:
    config = _config()["outer_etch_windows"].copy()
    config["inner_corner_radius_um"] = 0.0
    boundary = _hex_boundary()
    windows = _build_windows(boundary, config)

    boundary_vertices = list(boundary.exterior.coords[:-1])
    for window, first, second in zip(
        windows,
        boundary_vertices,
        boundary_vertices[1:] + boundary_vertices[:1],
    ):
        side_length = math.dist(first, second)
        start_trim = window.metadata["start_tangential_trim_um"]
        end_trim = window.metadata["end_tangential_trim_um"]
        inner_length = math.dist(*list(window.polygon.exterior.coords[:2]))
        assert inner_length == pytest.approx(side_length - start_trim - end_trim)
        assert window.metadata["inner_reference_length_um"] == pytest.approx(
            inner_length
        )
        assert start_trim == pytest.approx(end_trim)
        assert start_trim == pytest.approx(
            (config["parallel_side_gap_um"] - config["inner_clearance_um"])
            / math.sqrt(3.0)
        )


def test_v2_explicit_height_clearance_and_parallel_gap_are_exact() -> None:
    config = _config()["outer_etch_windows"].copy()
    config["inner_corner_radius_um"] = 0.0
    boundary = _hex_boundary()
    windows = _build_windows(boundary, config)
    boundary_vertices = list(boundary.exterior.coords[:-1])

    for window, start, end in zip(
        windows,
        boundary_vertices,
        boundary_vertices[1:] + boundary_vertices[:1],
    ):
        points = list(window.polygon.exterior.coords[:-1])
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        tx, ty = dx / length, dy / length
        nx, ny = ty, -tx
        assert (
            (points[0][0] - start[0]) * nx
            + (points[0][1] - start[1]) * ny
        ) == pytest.approx(config["inner_clearance_um"])
        assert (
            (points[3][0] - points[0][0]) * nx
            + (points[3][1] - points[0][1]) * ny
        ) == pytest.approx(9.0)

    for index, current in enumerate(windows):
        following = windows[(index + 1) % len(windows)]
        current_points = list(current.polygon.exterior.coords[:-1])
        following_points = list(following.polygon.exterior.coords[:-1])
        edge_dx = current_points[2][0] - current_points[1][0]
        edge_dy = current_points[2][1] - current_points[1][1]
        edge_length = math.hypot(edge_dx, edge_dy)
        separation_dx = following_points[0][0] - current_points[1][0]
        separation_dy = following_points[0][1] - current_points[1][1]
        gap = abs(
            edge_dx / edge_length * separation_dy
            - edge_dy / edge_length * separation_dx
        )
        assert gap == pytest.approx(config["parallel_side_gap_um"])


def test_v2_parallel_gap_cannot_be_smaller_than_clearance_induced_gap() -> None:
    config = _config()["outer_etch_windows"].copy()
    config["parallel_side_gap_um"] = 1.0

    with pytest.raises(ValueError, match="clearance-induced"):
        _build_windows(_hex_boundary(), config)


def test_v2_layer_rule_requires_geometry_at_low_level() -> None:
    config = _config()["outer_etch_windows"]

    with pytest.raises(ValueError, match="geometry is required"):
        build_outer_etch_windows(_hex_boundary(), config)


def test_v2_fixed_height_remains_available_for_historical_low_level_calls() -> None:
    config = _config()["outer_etch_windows"].copy()
    config.pop("radial_width")
    config["radial_width_um"] = 7.5
    config["inner_corner_radius_um"] = 0.0

    windows = build_outer_etch_windows(_hex_boundary(), config)

    assert {window.metadata["radial_width_um"] for window in windows} == {7.5}
    assert all(window.metadata["radial_width_rule"] is None for window in windows)
    assert all(window.metadata["finite_total_layers"] is None for window in windows)


def test_v2_adjacent_trapezoid_radial_edges_are_parallel() -> None:
    config = _config()["outer_etch_windows"].copy()
    config["inner_corner_radius_um"] = 0.0
    windows = _build_windows(_hex_boundary(), config)

    for index, current in enumerate(windows):
        following = windows[(index + 1) % len(windows)]
        current_points = list(current.polygon.exterior.coords[:-1])
        following_points = list(following.polygon.exterior.coords[:-1])
        current_edge = (
            current_points[2][0] - current_points[1][0],
            current_points[2][1] - current_points[1][1],
        )
        following_edge = (
            following_points[3][0] - following_points[0][0],
            following_points[3][1] - following_points[0][1],
        )
        cross_product = (
            current_edge[0] * following_edge[1]
            - current_edge[1] * following_edge[0]
        )
        assert cross_product == pytest.approx(0.0, abs=1e-12)


def test_v2_rounds_only_two_inner_corners_and_preserves_outer_vertices() -> None:
    config = _config()["outer_etch_windows"].copy()
    sharp_config = config.copy()
    sharp_config["inner_corner_radius_um"] = 0.0
    sharp = _build_windows(_hex_boundary(), sharp_config)
    rounded = _build_windows(_hex_boundary(), config)

    for sharp_window, rounded_window in zip(sharp, rounded):
        sharp_points = list(sharp_window.polygon.exterior.coords[:-1])
        rounded_points = list(rounded_window.polygon.exterior.coords[:-1])
        for inner_vertex in sharp_points[:2]:
            assert all(
                math.dist(inner_vertex, candidate) > 1e-9
                for candidate in rounded_points
            )
        for outer_vertex in sharp_points[2:]:
            assert any(
                math.dist(outer_vertex, candidate) < 1e-12
                for candidate in rounded_points
            )
        assert rounded_window.metadata["inner_corner_radius_um"] == pytest.approx(
            config["inner_corner_radius_um"]
        )
        assert rounded_window.metadata["rounded_inner_corner_count"] == 2
        assert rounded_window.metadata["outer_corner_radius_um"] == 0.0
