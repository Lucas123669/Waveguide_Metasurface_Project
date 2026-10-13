"""Strict, geometry-neutral DXF output and independent read-back checks.

The writer intentionally emits a very small DXF dialect for fabrication:
model-space entities are closed, zero-width, two-dimensional ``LWPOLYLINE``
objects and drawing coordinates are micrometers.  No construction geometry,
blocks, text, hatches, or splines are introduced here.
"""

from __future__ import annotations

from collections.abc import Iterable
import hashlib
import math
from pathlib import Path
from typing import Any

import ezdxf
from ezdxf.enums import InsertUnits
from ezdxf.lldxf.validator import is_valid_layer_name
from shapely.geometry import Polygon

from ..models import LayoutPlan


MICROMETER_INSUNITS = int(InsertUnits.Microns)
_ALLOWED_ENTITY_TYPE = "LWPOLYLINE"


class DXFContractError(ValueError):
    """Raised when a layout or DXF violates the fabrication contract."""


def _polygon_vertices(polygon: Polygon, *, feature_id: str) -> list[tuple[float, float]]:
    if polygon.is_empty:
        raise DXFContractError(f"feature {feature_id!r} has empty geometry")
    if not polygon.is_valid:
        raise DXFContractError(f"feature {feature_id!r} has invalid geometry")
    if polygon.area <= 0.0:
        raise DXFContractError(f"feature {feature_id!r} has non-positive area")
    if polygon.interiors:
        raise DXFContractError(
            f"feature {feature_id!r} contains interior rings; the fabrication "
            "DXF contract requires one simple closed outline per feature"
        )

    coordinates = [(float(x), float(y)) for x, y in polygon.exterior.coords]
    if coordinates and coordinates[0] == coordinates[-1]:
        coordinates.pop()
    if len(coordinates) < 3 or len(set(coordinates)) < 3:
        raise DXFContractError(f"feature {feature_id!r} has fewer than three vertices")
    if not all(math.isfinite(value) for point in coordinates for value in point):
        raise DXFContractError(f"feature {feature_id!r} contains non-finite coordinates")
    return coordinates


def _validate_layer_name(name: str, *, feature_id: str) -> None:
    if not name or not is_valid_layer_name(name):
        raise DXFContractError(
            f"feature {feature_id!r} has an invalid DXF layer name: {name!r}"
        )


def _iter_drawing_entities(document: ezdxf.document.Drawing) -> Iterable[Any]:
    """Yield entities from every block record, including model/paper space.

    Checking block records, rather than model space alone, prevents a DXF from
    hiding an unsupported production entity inside an unreferenced block.
    """

    for block in document.blocks:
        yield from block


def _shoelace_area(points: list[tuple[float, float]]) -> float:
    return 0.5 * abs(
        sum(
            x0 * y1 - x1 * y0
            for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1])
        )
    )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_dxf(
    layout: LayoutPlan,
    path: str | Path,
    *,
    version: str = "R2010",
) -> dict[str, Any]:
    """Write *layout* as a flattened fabrication DXF and read it back.

    Each :class:`~blueprint_core.models.LayoutFeature` produces exactly one
    closed ``LWPOLYLINE`` on ``feature.dxf_layer``.  The returned dictionary is
    produced by :func:`readback_dxf`, so a successful call also proves that the
    serialized file satisfies the independent reader contract.
    """

    if not isinstance(layout, LayoutPlan):
        raise TypeError("layout must be a LayoutPlan")

    resolved_features: list[tuple[str, str, list[tuple[float, float]]]] = []
    layer_spellings: dict[str, str] = {}
    for feature in layout.features:
        _validate_layer_name(feature.dxf_layer, feature_id=feature.feature_id)
        normalized_layer = feature.dxf_layer.casefold()
        previous_spelling = layer_spellings.setdefault(
            normalized_layer, feature.dxf_layer
        )
        if previous_spelling != feature.dxf_layer:
            raise DXFContractError(
                "DXF layer names are case-insensitive; conflicting spellings "
                f"{previous_spelling!r} and {feature.dxf_layer!r} are not allowed"
            )
        vertices = _polygon_vertices(feature.polygon, feature_id=feature.feature_id)
        resolved_features.append((feature.feature_id, feature.dxf_layer, vertices))

    try:
        document = ezdxf.new(dxfversion=version, setup=False)
    except (ezdxf.DXFError, ValueError) as exc:
        raise DXFContractError(f"unsupported DXF version: {version!r}") from exc

    document.units = MICROMETER_INSUNITS
    document.header["$MEASUREMENT"] = 1
    modelspace = document.modelspace()

    for _, layer_name, vertices in resolved_features:
        if layer_name not in document.layers:
            document.layers.add(layer_name)
        modelspace.add_lwpolyline(
            vertices,
            format="xy",
            close=True,
            dxfattribs={"layer": layer_name},
        )

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.saveas(output_path)

    report = readback_dxf(output_path)
    expected_entity_count = len(resolved_features)
    expected_vertex_count = sum(len(item[2]) for item in resolved_features)
    expected_layers = sorted({item[1] for item in resolved_features})
    expected_points = [point for item in resolved_features for point in item[2]]
    expected_bbox = (
        [
            min(point[0] for point in expected_points),
            min(point[1] for point in expected_points),
            max(point[0] for point in expected_points),
            max(point[1] for point in expected_points),
        ]
        if expected_points
        else None
    )
    expected_area = sum(_shoelace_area(item[2]) for item in resolved_features)

    if report["entity_count"] != expected_entity_count:
        raise DXFContractError(
            "DXF round-trip entity count mismatch: "
            f"expected {expected_entity_count}, read {report['entity_count']}"
        )
    if report["closed_count"] != expected_entity_count:
        raise DXFContractError("DXF round-trip closed-entity count mismatch")
    if report["vertex_count"] != expected_vertex_count:
        raise DXFContractError("DXF round-trip vertex count mismatch")
    if report["layers"] != expected_layers:
        raise DXFContractError("DXF round-trip layer mismatch")
    if expected_bbox is None:
        if report["bbox"] is not None:
            raise DXFContractError("DXF round-trip bounding-box mismatch")
    elif report["bbox"] is None or not all(
        math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)
        for actual, expected in zip(report["bbox"], expected_bbox)
    ):
        raise DXFContractError("DXF round-trip bounding-box mismatch")
    if not math.isclose(
        report["area_um2"], expected_area, rel_tol=1e-12, abs_tol=1e-15
    ):
        raise DXFContractError("DXF round-trip area mismatch")
    return report


def readback_dxf(path: str | Path) -> dict[str, Any]:
    """Read a DXF independently and enforce the fabrication entity contract.

    The summary is deliberately JSON-serializable so callers can merge it into
    the single layout report without creating another sidecar file.
    """

    input_path = Path(path)
    try:
        document = ezdxf.readfile(input_path)
    except (OSError, ezdxf.DXFError) as exc:
        raise DXFContractError(f"cannot read DXF file: {input_path}") from exc

    if int(document.units) != MICROMETER_INSUNITS:
        raise DXFContractError(
            "DXF units must be micrometers "
            f"(INSUNITS={MICROMETER_INSUNITS}), found INSUNITS={document.units}"
        )

    entities = list(_iter_drawing_entities(document))
    forbidden_types = sorted(
        {entity.dxftype() for entity in entities if entity.dxftype() != _ALLOWED_ENTITY_TYPE}
    )
    if forbidden_types:
        raise DXFContractError(
            "DXF contains forbidden entities: " + ", ".join(forbidden_types)
        )

    layers: set[str] = set()
    all_points: list[tuple[float, float]] = []
    vertex_count = 0
    closed_count = 0
    total_area_um2 = 0.0

    for entity in entities:
        if not entity.closed:
            raise DXFContractError("DXF contains an open LWPOLYLINE")
        closed_count += 1
        if abs(float(entity.dxf.get("elevation", 0.0))) > 1e-12:
            raise DXFContractError("DXF contains a non-planar LWPOLYLINE")
        if entity.has_arc:
            raise DXFContractError("DXF contains a bulged LWPOLYLINE")
        if entity.has_width:
            raise DXFContractError("DXF contains a non-zero-width LWPOLYLINE")

        points = [
            (float(x), float(y))
            for x, y in entity.get_points(format="xy")
        ]
        if len(points) < 3 or len(set(points)) < 3:
            raise DXFContractError("DXF contains a degenerate LWPOLYLINE")
        if not all(math.isfinite(value) for point in points for value in point):
            raise DXFContractError("DXF contains non-finite coordinates")

        layers.add(str(entity.dxf.layer))
        all_points.extend(points)
        vertex_count += len(points)
        total_area_um2 += _shoelace_area(points)

    bbox: list[float] | None
    if all_points:
        x_values, y_values = zip(*all_points)
        bbox = [
            float(min(x_values)),
            float(min(y_values)),
            float(max(x_values)),
            float(max(y_values)),
        ]
    else:
        bbox = None

    return {
        "version": document.acad_release,
        "dxf_version": document.dxfversion,
        "units": "micrometers",
        "insunits": int(document.units),
        "layers": sorted(layers),
        "entity_count": len(entities),
        "closed_count": closed_count,
        "vertex_count": vertex_count,
        "bbox": bbox,
        "area_um2": float(total_area_um2),
        "sha256": _file_sha256(input_path),
    }


__all__ = [
    "DXFContractError",
    "MICROMETER_INSUNITS",
    "readback_dxf",
    "write_dxf",
]
