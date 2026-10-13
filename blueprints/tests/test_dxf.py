from __future__ import annotations

import math
from pathlib import Path

import ezdxf
from ezdxf.enums import InsertUnits
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import pytest
from shapely import affinity
from shapely.geometry import Polygon

from blueprint_core.output.dxf import DXFContractError, readback_dxf, write_dxf
from blueprint_core.models import LayoutFeature, LayoutPlan
from blueprint_core.output.preview import (
    _CORRECTION_FUNCTION_TITLE,
    _PREVIEW_FIGURE_SIZE,
    _PREVIEW_HEIGHT_RATIOS,
    _PREVIEW_WIDTH_RATIOS,
    _RADIAL_STRIP_TITLE,
    _comparison_title,
    _comparison_local_bounds,
    _draw_correction_function,
    _draw_radial_strip,
    _radial_references,
    _select_radial_strip,
    save_preview,
)


def _feature(
    feature_id: str,
    polygon: Polygon,
    *,
    layer: str,
    region: str,
    local_index: int,
) -> LayoutFeature:
    return LayoutFeature(
        feature_id=feature_id,
        region=region,
        parent_i=local_index,
        parent_j=0,
        group_id=0,
        local_index=local_index,
        layer=0,
        nominal_polygon=polygon,
        polygon=polygon,
        shift_um=(0.0, 0.0),
        dxf_layer=layer,
    )


def _layout() -> LayoutPlan:
    return LayoutPlan(
        geometry_kind="synthetic_polygons_v1",
        features=[
            _feature(
                "cavity/0/0/0/0",
                Polygon([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]),
                layer="ETCH",
                region="cavity",
                local_index=0,
            ),
            _feature(
                "marker/1/0/0/1",
                Polygon([(2.0, -1.0), (3.0, -1.0), (3.0, 1.0), (2.0, 1.0)]),
                layer="MARKER",
                region="marker",
                local_index=1,
            ),
        ],
        boundary=Polygon([(-0.5, -1.5), (3.5, -1.5), (3.5, 1.5), (-0.5, 1.5)]),
    )


def _radial_layout() -> LayoutPlan:
    features: list[LayoutFeature] = []
    for shell in range(3):
        x = float(shell)
        polygon = Polygon(
            [(x - 0.1, -0.1), (x + 0.2, 0.0), (x - 0.1, 0.1)]
        )
        feature = _feature(
            f"radial/{shell}",
            polygon,
            layer="ETCH",
            region="cavity" if shell <= 1 else "cladding",
            local_index=shell,
        )
        feature.metadata["parent_shell"] = shell
        features.append(feature)

    off_ray = _feature(
        "off-ray/2",
        Polygon([(0.9, 1.63), (1.2, 1.73), (0.9, 1.83)]),
        layer="ETCH",
        region="cladding",
        local_index=10,
    )
    off_ray.metadata["parent_shell"] = 2
    features.append(off_ray)
    return LayoutPlan(
        geometry_kind="synthetic_radial_v1",
        features=features,
        boundary=Polygon([(-0.5, -0.6), (2.5, -0.6), (2.5, 2.0), (-0.5, 2.0)]),
        metadata={
            "finite": {"cavity_layers": 1, "cladding_layers": 1},
            "write_field_center_um": [0.0, 0.0],
        },
    )


def test_radial_strip_selects_one_complete_center_to_edge_cell_ray() -> None:
    selection = _select_radial_strip(_radial_layout())

    assert selection is not None
    assert selection.shells == (0, 1, 2)
    assert [group[1][0].feature_id for group in selection.groups] == [
        "radial/0",
        "radial/1",
        "radial/2",
    ]
    assert selection.period_um == pytest.approx(1.0)
    assert selection.half_width_um == pytest.approx(1.0 / 3.0**0.5)
    assert selection.cavity_layers == 1
    references = _radial_references(selection)
    assert [reference.key for reference in references] == [
        "center",
        "cavity_boundary",
        "cladding_boundary",
    ]
    assert [reference.shell for reference in references] == [0, 1, 2]
    assert [
        _comparison_title(reference.title, reference)
        for reference in references
    ] == [
        "Center (shell 0)",
        "Cavity boundary (shell 1)",
        "Cladding boundary (shell 2)",
    ]
    shared_bounds = _comparison_local_bounds(
        references,
        {feature.feature_id: feature for feature in _radial_layout().features},
    )
    assert shared_bounds == pytest.approx((-0.13, -0.18, 0.23, 0.18))


def test_radial_strip_plot_contract_locks_title_bounds_and_overlays() -> None:
    layout = _radial_layout()
    figure = Figure(figsize=(8.0, 2.0), dpi=100)
    FigureCanvasAgg(figure)
    axis = figure.add_subplot(1, 1, 1)

    _draw_radial_strip(
        axis,
        layout,
        {feature.feature_id: feature for feature in layout.features},
    )

    assert axis.get_title(loc="left") == _RADIAL_STRIP_TITLE
    assert _RADIAL_STRIP_TITLE == "Radial cell strip"
    assert "nominal" not in _RADIAL_STRIP_TITLE.casefold()
    assert "corrected" not in _RADIAL_STRIP_TITLE.casefold()
    assert axis.get_xlim() == pytest.approx((-0.5, 2.5))
    assert axis.get_ylim() == pytest.approx(
        (-1.0 / 3.0**0.5, 1.0 / 3.0**0.5)
    )
    assert [label.get_text() for label in axis.get_xticklabels()] == ["0", "1", "2"]
    assert len(axis.collections) == 3
    assert [len(collection.get_paths()) for collection in axis.collections[:2]] == [3, 3]
    assert axis.collections[2].get_offsets().shape == (3, 2)
    assert len(axis.lines) == 1
    figure.clear()


def test_preview_layout_contract_is_compact_with_wide_side_panels() -> None:
    assert _PREVIEW_FIGURE_SIZE == (15.7, 8.2)
    assert _PREVIEW_WIDTH_RATIOS == (2.10, 0.85, 1.90)
    assert _PREVIEW_HEIGHT_RATIOS == (1.0, 1.0, 0.36)
    assert _PREVIEW_WIDTH_RATIOS[0] > _PREVIEW_WIDTH_RATIOS[2]
    assert _PREVIEW_WIDTH_RATIOS[2] > _PREVIEW_WIDTH_RATIOS[1]


def test_correction_function_plot_contract_uses_actual_radial_envelope() -> None:
    layout = _radial_layout()
    selection = _select_radial_strip(layout)
    assert selection is not None
    references = _radial_references(selection)
    figure = Figure(figsize=(4.0, 4.0), dpi=100)
    FigureCanvasAgg(figure)
    axis = figure.add_subplot(1, 1, 1)

    _draw_correction_function(
        axis,
        selection,
        references,
        {
            "spatial_envelope": {
                "kind": "radial_even_polynomial",
                "target": "edge_offset_nm",
                "center_um": [0.0, 0.0],
                "half_size_um": [2.0, 2.0],
                "outside_policy": "clip",
                "coefficients": [0.0, 1.0],
            },
            'triangle_side_correction': {
                'kind': 'equilateral_parallel_edge_v1',
                'global_delta_nm': -10.0,
                'envelope_modulation_strength': 1.0,
                'regions': ['cavity', 'cladding'],
            },
            "fabrication": {
                "local_correction": {
                    "default": {
                        "operators": [
                            {
                                "kind": "edge_offset",
                                "value_nm": -2.886751345948129,
                                "join_style": "miter",
                                "miter_limit": 5.0,
                            }
                        ]
                    }
                },
                "corner_strategy": {"kind": "sharp"},
            },
        },
    )

    assert axis.get_title(loc="left") == _CORRECTION_FUNCTION_TITLE
    assert axis.get_xlabel() == "Parent shell (center → edge)"
    assert axis.get_ylabel() == "Triangle side-length correction (nm)"
    assert axis.get_xlim() == pytest.approx((0.0, 2.0))
    assert [label.get_text() for label in axis.get_xticklabels()] == ["0", "1", "2"]
    assert len(axis.lines) == 2
    assert len(axis.lines[0].get_xdata()) == 241
    assert axis.lines[0].get_ydata()[0] == pytest.approx(-10.0)
    assert axis.lines[0].get_ydata()[-1] == pytest.approx(
        -10.0 + 2.0 * math.sqrt(3.0)
    )
    assert axis.collections[0].get_offsets()[0, 1] == pytest.approx(-10.0)
    assert len(axis.collections) == 1
    assert axis.collections[0].get_offsets().shape == (3, 2)
    assert "Fabrication summary" not in {
        axis.get_title(loc="left"),
        _RADIAL_STRIP_TITLE,
    }
    figure.clear()


def test_dxf_roundtrip_preserves_flat_closed_polygons(tmp_path: Path) -> None:
    output_path = tmp_path / "layout.dxf"
    report = write_dxf(_layout(), output_path)

    assert output_path.is_file()
    assert report["version"] == "R2010"
    assert report["dxf_version"] == "AC1024"
    assert report["units"] == "micrometers"
    assert report["insunits"] == int(InsertUnits.Microns)
    assert report["layers"] == ["ETCH", "MARKER"]
    assert report["entity_count"] == 2
    assert report["closed_count"] == 2
    assert report["vertex_count"] == 7
    assert report["bbox"] == pytest.approx([0.0, -1.0, 3.0, 1.0])
    assert report["area_um2"] == pytest.approx(2.5)
    assert len(report["sha256"]) == 64

    document = ezdxf.readfile(output_path)
    entities = list(document.modelspace())
    assert int(document.units) == int(InsertUnits.Microns)
    assert [entity.dxftype() for entity in entities] == ["LWPOLYLINE", "LWPOLYLINE"]
    assert all(entity.closed for entity in entities)
    assert all(not entity.has_arc and not entity.has_width for entity in entities)
    assert {entity.dxf.layer for entity in entities} == {"ETCH", "MARKER"}
    assert readback_dxf(output_path) == report


def test_readback_rejects_forbidden_entities(tmp_path: Path) -> None:
    path = tmp_path / "line.dxf"
    document = ezdxf.new("R2010", setup=False)
    document.units = int(InsertUnits.Microns)
    document.modelspace().add_line((0.0, 0.0), (1.0, 1.0))
    document.saveas(path)

    with pytest.raises(DXFContractError, match="forbidden entities: LINE"):
        readback_dxf(path)


def test_save_preview_combines_layout_comparisons_and_summary(tmp_path: Path) -> None:
    nominal = _radial_layout()
    corrected_features = []
    for feature in nominal.features:
        corrected_polygon = affinity.scale(
            feature.polygon,
            xfact=1.08,
            yfact=1.08,
            origin="centroid",
        )
        corrected_features.append(feature.with_geometry(corrected_polygon))
    corrected = nominal.with_features(
        corrected_features,
        metadata={"write_field_center_um": [0.0, 0.0]},
    )
    preview_path = tmp_path / "preview.png"

    returned_path = save_preview(
        nominal,
        corrected,
        {
            "spatial_envelope": {
                "kind": "radial_even_polynomial",
                "target": "edge_offset_nm",
                "center_um": [0.0, 0.0],
                "half_size_um": [2.0, 2.0],
                "outside_policy": "clip",
                "coefficients": [1.0, 4.0],
            },
            "fabrication": {
                "local_correction": {
                    "default": {"operators": []},
                },
                "corner_strategy": {"kind": "sharp"},
            },
            "correction": {"local": {"isotropic_scale": 1.08}},
            "dose": {"kind": "unassigned"},
            "drc": {"status": "pass", "error_count": 0},
        },
        preview_path,
        dpi=120,
    )

    assert returned_path == preview_path
    assert preview_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert preview_path.stat().st_size > 10_000
