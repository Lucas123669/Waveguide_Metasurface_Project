from __future__ import annotations

import math

import pytest
from shapely.geometry import Polygon

from blueprint_core.fabrication.corrections import (
    CorrectionError,
    FeatureCorrection,
    apply_corrections,
    apply_feature_correction,
    evaluate_spatial_envelope,
    feature_correction_from_mapping,
    snap_polygon_to_grid,
    spatial_envelope_from_mapping,
    triangle_side_correction_from_mapping,
)
from blueprint_core.models import LayoutFeature, LayoutPlan


def _square(x: float = 0.0, y: float = 0.0, size: float = 1.0) -> Polygon:
    return Polygon(
        [(x, y), (x + size, y), (x + size, y + size), (x, y + size)]
    )


def _layout(polygon: Polygon | None = None) -> LayoutPlan:
    polygon = _square() if polygon is None else polygon
    feature = LayoutFeature(
        "cavity/0/0/0/0",
        "cavity",
        0,
        0,
        0,
        0,
        0,
        list(polygon.exterior.coords)[:-1],
        list(polygon.exterior.coords)[:-1],
        (0.0, 0.0),
    )
    return LayoutPlan("synthetic", [feature], _square(-5.0, -5.0, 10.0), {})


def test_layout_models_accept_coordinate_sequences_and_copy_metadata() -> None:
    metadata: dict[str, object] = {}
    layout = _layout()
    layout.metadata.update(metadata)
    assert isinstance(layout.features[0].polygon, Polygon)
    assert layout.feature_count == 1
    assert layout.bounds == pytest.approx((0.0, 0.0, 1.0, 1.0))


def test_positive_edge_offset_expands_opening_by_normal_distance() -> None:
    corrected = apply_feature_correction(
        _square(),
        FeatureCorrection(edge_offset_um=0.1, join_style="mitre"),
    )
    assert corrected.bounds == pytest.approx((-0.1, -0.1, 1.1, 1.1))
    assert corrected.area == pytest.approx(1.44)


def test_centroid_scales_keep_centroid_fixed() -> None:
    corrected = apply_feature_correction(
        _square(),
        FeatureCorrection(
            isotropic_scale=2.0,
            scale_x=0.5,
            scale_y=1.5,
            operator_order=("isotropic_scale", "anisotropic_scale_xy"),
        ),
    )
    assert corrected.centroid.coords[0] == pytest.approx((0.5, 0.5))
    assert corrected.bounds == pytest.approx((0.0, -1.0, 1.0, 2.0))


def test_nested_operator_values_and_order_are_respected() -> None:
    correction = feature_correction_from_mapping(
        {
            "operators": [
                {
                    "kind": "edge_offset",
                    "value_nm": 100.0,
                    "join_style": "miter",
                    "miter_limit": 5.0,
                },
                {"kind": "isotropic_scale", "factor": 2.0},
            ]
        }
    )
    assert correction.edge_offset_um == pytest.approx(0.1)
    assert correction.operator_order == ("edge_offset", "isotropic_scale")
    result = apply_feature_correction(_square(), correction)
    assert result.bounds == pytest.approx((-0.7, -0.7, 1.7, 1.7))


def test_constant_envelope_uses_target_units_and_field_normalization() -> None:
    envelope = spatial_envelope_from_mapping(
        {
            "kind": "constant",
            "target": "edge_offset_nm",
            "center_um": [0.0, 0.0],
            "half_size_um": [10.0, 20.0],
            "outside_policy": "error",
            "coefficients": [5.0],
        }
    )
    result = envelope.evaluate((5.0, -10.0))
    assert result.value == pytest.approx(0.005)
    assert (result.normalized_x, result.normalized_y) == pytest.approx((0.5, -0.5))


def test_radial_even_envelope_is_symmetric_and_clips_explicitly() -> None:
    config = {
        "kind": "radial_even_polynomial",
        "target": "edge_offset_nm",
        "center_um": [0.0, 0.0],
        "half_size_um": [10.0, 20.0],
        "outside_policy": "clip",
        "coefficients": [1.0, 2.0],
    }
    center = evaluate_spatial_envelope(config, (0.0, 0.0))
    positive = evaluate_spatial_envelope(config, (10.0, 0.0))
    negative = evaluate_spatial_envelope(config, (-10.0, 0.0))
    clipped = evaluate_spatial_envelope(config, (20.0, 0.0))
    diagonal_clipped = evaluate_spatial_envelope(config, (10.0, 20.0))
    assert center.value == pytest.approx(0.001)
    assert positive.value == pytest.approx(0.003)
    assert negative.value == pytest.approx(positive.value)
    assert clipped.value == pytest.approx(positive.value)
    assert diagonal_clipped.value == pytest.approx(positive.value)
    assert diagonal_clipped.normalized_x == pytest.approx(1.0 / math.sqrt(2.0))
    assert diagonal_clipped.normalized_y == pytest.approx(1.0 / math.sqrt(2.0))


def test_envelope_outside_error_is_not_silently_extrapolated() -> None:
    config = {
        "kind": "radial_even_polynomial",
        "target": "isotropic_scale_delta",
        "center_um": [0.0, 0.0],
        "half_size_um": [1.0, 1.0],
        "outside_policy": "error",
        "coefficients": [0.0, 0.1],
    }
    with pytest.raises(CorrectionError, match="outside"):
        evaluate_spatial_envelope(config, (1.1, 0.0))


def test_separable_envelope_supports_asymmetric_xy_coefficients() -> None:
    envelope = spatial_envelope_from_mapping(
        {
            "kind": "separable_even_polynomial_xy",
            "target": "edge_offset_nm",
            "center_um": [0.0, 0.0],
            "half_size_um": [10.0, 20.0],
            "outside_policy": "error",
            "coefficients": [0.0, [2.0], [3.0]],
        }
    )
    assert envelope.evaluate((10.0, 0.0)).value == pytest.approx(0.002)
    assert envelope.evaluate((0.0, 20.0)).value == pytest.approx(0.003)
    assert envelope.evaluate((-10.0, -20.0)).value == pytest.approx(0.005)


def test_spatial_envelope_region_scope_excludes_auxiliary_air_features() -> None:
    cavity_polygon = _square(0.0, 0.0)
    marker_polygon = _square(5.0, 0.0)
    features = [
        LayoutFeature(
            "cavity/0",
            "cavity",
            0,
            0,
            0,
            0,
            0,
            list(cavity_polygon.exterior.coords)[:-1],
            list(cavity_polygon.exterior.coords)[:-1],
            (0.5, 0.5),
        ),
        LayoutFeature(
            "marker/0",
            "parameter_marker",
            0,
            0,
            0,
            0,
            0,
            list(marker_polygon.exterior.coords)[:-1],
            list(marker_polygon.exterior.coords)[:-1],
            (5.5, 0.5),
        ),
    ]
    layout = LayoutPlan("synthetic", features, _square(-1.0, -1.0, 8.0), {})
    fabrication = {
        'triangle_side_correction': {
            'kind': 'equilateral_parallel_edge_v1',
            'global_delta_nm': -10.0,
            'envelope_modulation_strength': 0.5,
            'regions': ['cavity', 'cladding'],
        },
        "spatial_envelope": {
            "kind": "constant",
            "target": "edge_offset_nm",
            "center_um": [0.0, 0.0],
            "half_size_um": [1.0, 1.0],
            "outside_policy": "error",
            "coefficients": [10.0],
            "regions": ["cavity", "cladding"],
        }
    }
    result = apply_corrections(
        layout,
        fabrication,
        {"kind": "unassigned", "response": {"kind": "pass_through"}},
        {},
    )

    cavity, marker = result.features
    applied_offset_um = 0.005 - 10.0 / (2.0 * math.sqrt(3.0)) / 1000.0
    assert cavity.polygon.bounds == pytest.approx(
        (
            -applied_offset_um,
            -applied_offset_um,
            1.0 + applied_offset_um,
            1.0 + applied_offset_um,
        )
    )
    triangle_metadata = cavity.metadata['correction']['triangle_side_correction']
    assert triangle_metadata['global_edge_offset_um'] == pytest.approx(
        -10.0 / (2.0 * math.sqrt(3.0)) / 1000.0
    )
    assert triangle_metadata['raw_envelope']['value'] == pytest.approx(0.01)
    assert triangle_metadata['modulated_envelope']['value'] == pytest.approx(0.005)
    assert triangle_metadata['applied_side_delta_nm'] == pytest.approx(
        -10.0 + 2.0 * math.sqrt(3.0) * 5.0
    )
    assert cavity.metadata["correction"]["envelope"]["applied"] is True
    assert marker.polygon.equals_exact(marker_polygon, tolerance=0.0)
    assert marker.metadata['correction']['triangle_side_correction']['applied'] is False
    assert marker.metadata["correction"]["envelope"]["value"] == 0.0
    assert marker.metadata["correction"]["envelope"]["applied"] is False
    assert result.metadata["correction_pipeline"]["spatial_envelope_regions"] == [
        "cavity",
        "cladding",
    ]


def test_triangle_side_correction_converts_single_side_delta_to_edge_offset() -> None:
    correction = triangle_side_correction_from_mapping(
        {
            'kind': 'equilateral_parallel_edge_v1',
            'global_delta_nm': -10.0,
            'envelope_modulation_strength': 0.0,
            'regions': ['cavity', 'cladding'],
        }
    )
    assert correction.global_edge_offset_um == pytest.approx(
        -10.0 / (2.0 * math.sqrt(3.0)) / 1000.0
    )
    assert correction.envelope_modulation_strength == pytest.approx(0.0)
    assert correction.applies_to('cavity')
    assert not correction.applies_to('parameter_marker')


def test_grid_snap_is_bounded_and_rejects_collapsed_polygons() -> None:
    polygon = Polygon([(0.04, 0.04), (0.96, 0.04), (0.96, 0.96), (0.04, 0.96)])
    snapped = snap_polygon_to_grid(polygon, 0.1)
    assert snapped.bounds == pytest.approx((0.0, 0.0, 1.0, 1.0))
    assert polygon.hausdorff_distance(snapped) <= math.sqrt(2.0) * 0.05 + 1e-12

    tiny = Polygon([(0.01, 0.01), (0.02, 0.01), (0.01, 0.02)])
    with pytest.raises(CorrectionError, match="collapsed"):
        snap_polygon_to_grid(tiny, 0.1)


def test_cli_facing_pipeline_combines_local_envelope_transform_dose_and_grid() -> None:
    fabrication = {
        "local_correction": {
            "operators": [
                {
                    "kind": "edge_offset",
                    "value_nm": 10.0,
                    "join_style": "miter",
                    "miter_limit": 5.0,
                }
            ]
        },
        "spatial_envelope": {
            "kind": "constant",
            "target": "edge_offset_nm",
            "center_um": [0.0, 0.0],
            "half_size_um": [10.0, 10.0],
            "outside_policy": "error",
            "coefficients": [5.0],
        },
        "grid_nm": 1.0,
        "corner_strategy": {"kind": "sharp"},
        "scale_correction_ppm": {"x": 0.0, "y": 0.0},
    }
    dose = {
        "kind": "unassigned",
        "value": None,
        "unit": None,
        "response": {"kind": "pass_through"},
        "encoder": {"kind": "external_recipe"},
    }
    result = apply_corrections(
        _layout(),
        fabrication,
        dose,
        {
            "rotation_deg": 0.0,
            "mirror_x": False,
            "mirror_y": False,
            "translation_um": [1.0, -2.0],
        },
    )
    feature = result.features[0]
    assert feature.polygon.bounds == pytest.approx((0.985, -2.015, 2.015, -0.985))
    assert feature.nominal_polygon.bounds == pytest.approx((1.0, -2.0, 2.0, -1.0))
    assert feature.dxf_layer == "ETCH"
    assert feature.metadata["correction"]["effective"]["edge_offset_um"] == pytest.approx(0.015)
    assert result.metadata["correction_pipeline"]["grid_um"] == pytest.approx(0.001)
