from __future__ import annotations

import math

import numpy as np
import pytest

from blueprint_core.geometry import (
    CompactCellParameters,
    build_hex_layout,
    build_six_triangle_cell,
    rotate_points,
)


def geometry_mapping(
    *,
    shift_kind: str = "groups",
    profile: dict[str, object] | None = None,
    x_factor: float = 0.0,
    y_factor: float = 0.0,
    cavity_layers: int = 1,
    cladding_layers: int = 1,
    origin_um: list[float] | None = None,
    orientation_deg: float = 0.0,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "length_unit": "um",
        "lattice": {
            "kind": "triangular_hexagonal_v1",
            "period_um": 0.82,
            "origin_um": [0.0, 0.0] if origin_um is None else origin_um,
            "orientation_deg": orientation_deg,
        },
        "unit_cell": {
            "kind": "six_triangular_holes_fourier_v1",
            "radial_reference_fraction": 1.0 / 3.0,
            "edge_reference_nm": 230.0,
            "cavity": {"b0_nm": 245.0, "eta": 0.96, "zeta": 1.156},
            "cladding": {"b0_nm": 242.0, "eta": 0.98, "zeta": 0.93},
        },
        "finite": {
            "kind": "hex_shells_v1",
            "cavity_layers": cavity_layers,
            "cladding_layers": cladding_layers,
            "empty_buffer_periods": 0.5,
        },
        "cladding_shift": {
            "geometry": {"kind": shift_kind},
            "profile": {"kind": "uniform"} if profile is None else profile,
            "x_factor": x_factor,
            "y_factor": y_factor,
        },
    }


def polygon_coordinates(feature) -> np.ndarray:
    return np.asarray(feature.polygon.exterior.coords[:-1], dtype=float)


def test_six_triangle_cell_has_expected_count_and_c6_symmetry() -> None:
    cell = build_six_triangle_cell(
        period_um=0.82,
        radial_reference_fraction=1.0 / 3.0,
        edge_reference_nm=230.0,
        parameters=CompactCellParameters(b0_nm=245.0, eta=0.96, zeta=1.0),
    )

    assert len(cell.polygons) == 6
    assert cell.hole_parameters.shape == (6, 4)
    np.testing.assert_allclose(
        cell.hole_parameters[:, 0],
        np.full(6, 0.82 * (1.0 / 3.0) * 0.96),
        rtol=0.0,
        atol=1e-14,
    )
    np.testing.assert_allclose(
        cell.hole_parameters[:, 2],
        np.full(6, 0.245),
        rtol=0.0,
        atol=1e-14,
    )
    for index, polygon in enumerate(cell.polygons):
        np.testing.assert_allclose(
            polygon,
            rotate_points(cell.polygons[0], 60.0 * index),
            rtol=0.0,
            atol=2e-16,
        )


def test_small_hex_layout_counts_regions_and_zero_shift() -> None:
    plan = build_hex_layout(geometry_mapping())

    # Radius 1 contains seven cells; shell 2 contains twelve cells.
    assert plan.metadata["counts"] == {
        "cavity_cells": 7,
        "cladding_cells": 12,
        "cavity_features": 42,
        "cladding_features": 72,
        "total_features": 114,
    }
    assert len(plan.features) == 114
    assert len({feature.feature_id for feature in plan.features}) == 114
    assert sum(feature.region == "cavity" for feature in plan.features) == 42
    assert sum(feature.region == "cladding" for feature in plan.features) == 72
    assert {feature.layer for feature in plan.features if feature.region == "cavity"} == {0}
    assert {feature.layer for feature in plan.features if feature.region == "cladding"} == {1}
    for feature in plan.features:
        assert feature.shift_um == pytest.approx((0.0, 0.0), abs=1e-15)
        assert feature.polygon.equals_exact(feature.nominal_polygon, tolerance=0.0)
    assert plan.boundary.is_valid
    assert plan.boundary.exterior.is_ring


@pytest.mark.parametrize("shift_kind", ["groups", "ellipse"])
def test_cladding_shift_is_centrally_symmetric(shift_kind: str) -> None:
    plan = build_hex_layout(
        geometry_mapping(
            shift_kind=shift_kind,
            x_factor=0.05,
            y_factor=0.08,
            cavity_layers=1,
            cladding_layers=2,
            profile={"kind": "tanh_power", "scale_layers": 2.5, "power": 2.0},
        )
    )
    representatives = {
        (feature.parent_i, feature.parent_j): feature
        for feature in plan.features
        if feature.region == "cladding" and feature.local_index == 0
    }

    for (i, j), feature in representatives.items():
        opposite = representatives[(-i, -j)]
        np.testing.assert_allclose(
            feature.shift_um,
            -np.asarray(opposite.shift_um),
            rtol=0.0,
            atol=1e-14,
        )
        layer = feature.layer
        expected_envelope = math.tanh((layer / 2.5) ** 2.0)
        assert feature.metadata["shift_envelope"] == pytest.approx(expected_envelope)


def test_ellipse_shift_is_radial_and_inward() -> None:
    plan = build_hex_layout(
        geometry_mapping(
            shift_kind="ellipse",
            x_factor=0.04,
            y_factor=0.09,
        )
    )
    for feature in plan.features:
        if feature.region != "cladding" or feature.local_index != 0:
            continue
        parent = np.asarray(feature.metadata["canonical_parent_center_um"])
        shift = np.asarray(feature.shift_um)
        assert float(np.dot(parent, shift)) < 0.0
        cross_z = parent[0] * shift[1] - parent[1] * shift[0]
        assert cross_z == pytest.approx(0.0, abs=1e-14)


def test_origin_and_orientation_transform_polygons_boundary_and_shift() -> None:
    base = build_hex_layout(
        geometry_mapping(shift_kind="ellipse", x_factor=0.04, y_factor=0.08)
    )
    transformed = build_hex_layout(
        geometry_mapping(
            shift_kind="ellipse",
            x_factor=0.04,
            y_factor=0.08,
            origin_um=[2.0, -3.0],
            orientation_deg=30.0,
        )
    )
    angle = math.radians(30.0)
    rotation = np.array(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]]
    )
    translation = np.array([2.0, -3.0])

    for before, after in zip(base.features, transformed.features, strict=True):
        np.testing.assert_allclose(
            polygon_coordinates(after),
            polygon_coordinates(before) @ rotation.T + translation,
            rtol=0.0,
            atol=2e-15,
        )
        np.testing.assert_allclose(
            after.shift_um,
            np.asarray(before.shift_um) @ rotation.T,
            rtol=0.0,
            atol=2e-15,
        )
    np.testing.assert_allclose(
        np.asarray(transformed.boundary.exterior.coords[:-1]),
        np.asarray(base.boundary.exterior.coords[:-1]) @ rotation.T + translation,
        rtol=0.0,
        atol=2e-15,
    )


def test_geometry_mapping_is_strict_and_self_contained() -> None:
    value = geometry_mapping()
    value["lattice"]["implicit_period_fallback"] = 0.82
    with pytest.raises(ValueError, match="unknown fields"):
        build_hex_layout(value)

    missing = geometry_mapping()
    del missing["unit_cell"]["edge_reference_nm"]
    with pytest.raises(ValueError, match="missing required fields"):
        build_hex_layout(missing)

    conflicting_profile = geometry_mapping()
    conflicting_profile["cladding_shift"]["profile"] = {
        "kind": "uniform",
        "scale_layers": 2.0,
    }
    with pytest.raises(ValueError, match="unknown fields"):
        build_hex_layout(conflicting_profile)
