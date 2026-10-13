"""Design-rule checks for corrected, grid-quantized blueprint layouts."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from numbers import Integral
from typing import Any, Iterable, Mapping, Sequence

from shapely.geometry import Polygon
from shapely.strtree import STRtree
from shapely.validation import explain_validity

from ..models import Coordinate, LayoutFeature, LayoutPlan


@dataclass(frozen=True, slots=True)
class DrcViolation:
    rule: str
    severity: str
    message: str
    feature_ids: tuple[str, ...] = ()
    measured: float | None = None
    limit: float | None = None
    unit: str | None = None
    location_um: Coordinate | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "feature_ids": list(self.feature_ids),
        }
        if self.measured is not None:
            result["measured"] = self.measured
        if self.limit is not None:
            result["limit"] = self.limit
        if self.unit is not None:
            result["unit"] = self.unit
        if self.location_um is not None:
            result["location_um"] = list(self.location_um)
        return result


@dataclass(slots=True)
class DrcReport:
    feature_count: int
    violations: list[DrcViolation] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    fail_on_warning: bool = False

    @property
    def error_count(self) -> int:
        return sum(item.severity == "error" for item in self.violations)

    @property
    def warning_count(self) -> int:
        return sum(item.severity == "warning" for item in self.violations)

    @property
    def passed(self) -> bool:
        return self.error_count == 0 and not (
            self.fail_on_warning and self.warning_count > 0
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "feature_count": self.feature_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "fail_on_warning": self.fail_on_warning,
            "metrics": dict(self.metrics),
            "violations": [item.to_dict() for item in self.violations],
        }

    def raise_for_errors(self) -> None:
        if not self.passed:
            first = next(
                (
                    item
                    for item in self.violations
                    if item.severity == "error" or self.fail_on_warning
                )
            )
            raise DrcError(
                f"DRC release gate failed with {self.error_count} error(s) and "
                f"{self.warning_count} warning(s); first: "
                f"[{first.rule}] {first.message}"
            )


class DrcError(RuntimeError):
    """Raised when a release gate is asked to accept a failing DRC report."""


def _finite_nonnegative(value: Any, *, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite non-negative number") from exc
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be a finite non-negative number")
    return result


def _length_um(
    config: Mapping[str, Any],
    *,
    um_keys: Sequence[str],
    nm_keys: Sequence[str],
    default: float = 0.0,
) -> float:
    present = [
        key for key in (*um_keys, *nm_keys) if key in config and config[key] is not None
    ]
    if len(present) > 1:
        raise ValueError("conflicting DRC fields: " + ", ".join(sorted(present)))
    if not present:
        return default
    key = present[0]
    value = _finite_nonnegative(config[key], name=key)
    return value / 1000.0 if key in nm_keys else value


def _severity(config: Mapping[str, Any], rule: str) -> str:
    mapping = config.get("severity_by_rule", config.get("severities", {}))
    value = mapping.get(rule, "error") if isinstance(mapping, Mapping) else "error"
    if value not in {"error", "warning"}:
        raise ValueError(f"DRC severity for {rule!r} must be error or warning")
    return value


def _minimum_edge_length(polygon: Polygon) -> float:
    minimum = math.inf
    rings = (polygon.exterior, *polygon.interiors)
    for ring in rings:
        coordinates = list(ring.coords)
        for first, second in zip(coordinates, coordinates[1:]):
            length = math.hypot(second[0] - first[0], second[1] - first[1])
            minimum = min(minimum, length)
    return minimum


def _minimum_hole_width(polygon: Polygon) -> float:
    """Return the short side of the polygon's minimum rotated rectangle."""

    rectangle = polygon.minimum_rotated_rectangle
    if not isinstance(rectangle, Polygon) or rectangle.is_empty:
        return 0.0
    coordinates = list(rectangle.exterior.coords)
    edge_lengths = [
        math.hypot(second[0] - first[0], second[1] - first[1])
        for first, second in zip(coordinates, coordinates[1:])
    ]
    positive = [value for value in edge_lengths if value > 0.0]
    return min(positive) if positive else 0.0


def _on_grid(value: float, step: float, origin: float, tolerance: float) -> bool:
    quotient = (value - origin) / step
    return abs(quotient - round(quotient)) * step <= tolerance


def _grid_contract(config: Mapping[str, Any]) -> tuple[float, Coordinate] | None:
    nested = config.get("grid", {})
    if nested is None:
        nested = {}
    if isinstance(nested, (int, float)):
        nested = {"step_um": nested}
    if not isinstance(nested, Mapping):
        raise ValueError("drc.grid must be an object or numeric um step")
    if nested.get("enabled") is False:
        return None
    merged = dict(nested)
    for key in ("grid_um", "address_grid_um", "writer_grid_um", "grid_nm", "address_grid_nm"):
        if key in config and key not in merged:
            merged[key] = config[key]
    step = _length_um(
        merged,
        um_keys=("step_um", "grid_um", "address_grid_um", "writer_grid_um"),
        nm_keys=("step_nm", "grid_nm", "address_grid_nm"),
    )
    if step == 0.0:
        return None
    origin_raw = merged.get("origin_um", (0.0, 0.0))
    try:
        origin_x, origin_y = origin_raw
    except (TypeError, ValueError) as exc:
        raise ValueError("DRC grid origin_um must contain two values") from exc
    origin = (float(origin_x), float(origin_y))
    if not all(math.isfinite(value) for value in origin):
        raise ValueError("DRC grid origin coordinates must be finite")
    return step, origin


def _candidate_indices(
    result: Iterable[Any],
    *,
    geometry_id_to_index: Mapping[int, int],
) -> Iterable[int]:
    """Normalize Shapely 2 integer queries and Shapely 1 geometry queries."""

    for item in result:
        if isinstance(item, Integral):
            yield int(item)
        else:
            index = geometry_id_to_index.get(id(item))
            if index is not None:
                yield index


def _location(polygon: Polygon) -> Coordinate:
    point = polygon.representative_point()
    return (float(point.x), float(point.y))


def _coerce_keep_outs(config: Mapping[str, Any]) -> list[Polygon]:
    raw_items = config.get("keep_outs", config.get("keepout_polygons", ()))
    if raw_items is None:
        return []
    if not isinstance(raw_items, Sequence) or isinstance(raw_items, (str, bytes)):
        raise ValueError("DRC keep_outs must be a list of polygons")
    polygons: list[Polygon] = []
    for index, value in enumerate(raw_items):
        if isinstance(value, Mapping):
            value = value.get("polygon_um", value.get("vertices_um"))
        if value is None:
            raise ValueError(f"keep_outs[{index}] has no polygon_um")
        polygon = value if isinstance(value, Polygon) else Polygon(value)
        if polygon.is_empty or not polygon.is_valid:
            raise ValueError(f"keep_outs[{index}] must be a valid non-empty polygon")
        polygons.append(polygon)
    return polygons


def run_drc(layout: LayoutPlan, drc: Mapping[str, Any]) -> DrcReport:
    """Run geometry and fabrication checks and return a structured report.

    Pairwise checks use an STRtree and only inspect nearby candidates, avoiding
    an all-pairs scan for production layouts with tens of thousands of holes.
    """

    config = dict(drc)
    minimum_width = _length_um(
        config,
        um_keys=("min_hole_width_um",),
        nm_keys=("min_hole_width_nm",),
    )
    minimum_edge = _length_um(
        config,
        um_keys=("min_edge_um", "min_edge_length_um"),
        nm_keys=("min_edge_nm", "min_edge_length_nm"),
    )
    minimum_bridge = _length_um(
        config,
        um_keys=("min_bridge_um", "min_silicon_bridge_um"),
        nm_keys=("min_bridge_nm", "min_silicon_bridge_nm"),
    )
    boundary_clearance = _length_um(
        config,
        um_keys=("boundary_clearance_um", "die_clearance_um"),
        nm_keys=("boundary_clearance_nm", "die_clearance_nm"),
    )
    tolerance = _length_um(
        config,
        um_keys=("tolerance_um",),
        nm_keys=("tolerance_nm",),
        default=1e-9,
    )
    area_tolerance = _finite_nonnegative(
        config.get("area_tolerance_um2", max(tolerance * tolerance, 1e-24)),
        name="area_tolerance_um2",
    )
    grid = _grid_contract(config)
    if grid is None:
        pipeline = layout.metadata.get("correction_pipeline", {})
        if isinstance(pipeline, Mapping) and pipeline.get("grid_um") is not None:
            grid = (
                _finite_nonnegative(pipeline["grid_um"], name="layout grid_um"),
                tuple(pipeline.get("grid_origin_um", (0.0, 0.0))),
            )
    grid_tolerance = (
        _length_um(
            config,
            um_keys=("grid_tolerance_um",),
            nm_keys=("grid_tolerance_nm",),
            default=max(tolerance, (grid[0] * 1e-8 if grid else tolerance)),
        )
        if grid
        else tolerance
    )
    report = DrcReport(
        feature_count=layout.feature_count,
        fail_on_warning=bool(config.get("fail_on_warning", False)),
    )
    violations = report.violations

    def add(
        rule: str,
        message: str,
        *,
        feature_ids: tuple[str, ...] = (),
        measured: float | None = None,
        limit: float | None = None,
        unit: str | None = None,
        location_um: Coordinate | None = None,
    ) -> None:
        violations.append(
            DrcViolation(
                rule=rule,
                severity=_severity(config, rule),
                message=message,
                feature_ids=feature_ids,
                measured=measured,
                limit=limit,
                unit=unit,
                location_um=location_um,
            )
        )

    identifiers: dict[str, int] = {}
    valid_entries: list[tuple[int, LayoutFeature, Polygon]] = []
    minimum_width_seen = math.inf
    minimum_edge_seen = math.inf

    for index, feature in enumerate(layout.features):
        identifiers[feature.feature_id] = identifiers.get(feature.feature_id, 0) + 1
        polygon = feature.polygon
        feature_ids = (feature.feature_id,)
        if polygon.is_empty or polygon.area <= area_tolerance:
            add(
                "degenerate_polygon",
                "feature is empty or has negligible area",
                feature_ids=feature_ids,
                measured=float(polygon.area),
                limit=area_tolerance,
                unit="um^2",
            )
            continue
        if len(set((float(x), float(y)) for x, y, *_ in polygon.exterior.coords[:-1])) < 3:
            add(
                "degenerate_polygon",
                "feature exterior has fewer than three distinct vertices",
                feature_ids=feature_ids,
            )
            continue
        if not polygon.is_valid:
            add(
                "polygon_validity",
                explain_validity(polygon),
                feature_ids=feature_ids,
                location_um=_location(polygon),
            )
            continue

        valid_entries.append((index, feature, polygon))
        width = _minimum_hole_width(polygon)
        edge = _minimum_edge_length(polygon)
        minimum_width_seen = min(minimum_width_seen, width)
        minimum_edge_seen = min(minimum_edge_seen, edge)
        if minimum_width and width + tolerance < minimum_width:
            add(
                "min_hole_width",
                "feature width is below the configured minimum",
                feature_ids=feature_ids,
                measured=width,
                limit=minimum_width,
                unit="um",
                location_um=_location(polygon),
            )
        if minimum_edge and edge + tolerance < minimum_edge:
            add(
                "min_edge_length",
                "polygon edge is below the configured minimum",
                feature_ids=feature_ids,
                measured=edge,
                limit=minimum_edge,
                unit="um",
                location_um=_location(polygon),
            )

        if grid:
            step, origin = grid
            off_grid = next(
                (
                    (float(x), float(y))
                    for ring in (polygon.exterior, *polygon.interiors)
                    for x, y, *_ in ring.coords
                    if not (
                        _on_grid(float(x), step, origin[0], grid_tolerance)
                        and _on_grid(float(y), step, origin[1], grid_tolerance)
                    )
                ),
                None,
            )
            if off_grid is not None:
                add(
                    "address_grid",
                    "feature contains a vertex outside the writer address grid",
                    feature_ids=feature_ids,
                    limit=step,
                    unit="um",
                    location_um=off_grid,
                )

    for feature_id, count in identifiers.items():
        if count > 1:
            add(
                "duplicate_feature_id",
                f"feature_id occurs {count} times",
                feature_ids=(feature_id,),
                measured=float(count),
                limit=1.0,
            )

    boundary = layout.boundary
    if boundary is not None:
        if boundary.is_empty or not boundary.is_valid:
            add(
                "boundary_validity",
                "layout boundary must be a valid non-empty polygon",
            )
            boundary = None
    elif boundary_clearance or config.get("require_boundary", False):
        add("boundary_missing", "boundary checks requested but layout has no boundary")

    minimum_boundary_clearance_seen = math.inf
    if boundary is not None:
        for _, feature, polygon in valid_entries:
            if feature.metadata.get("boundary_check", True) is False:
                continue
            if not boundary.covers(polygon):
                add(
                    "boundary_containment",
                    "feature is not fully contained by the layout boundary",
                    feature_ids=(feature.feature_id,),
                    location_um=_location(polygon),
                )
                continue
            clearance = float(polygon.distance(boundary.boundary))
            minimum_boundary_clearance_seen = min(
                minimum_boundary_clearance_seen, clearance
            )
            if boundary_clearance and clearance + tolerance < boundary_clearance:
                add(
                    "boundary_clearance",
                    "feature-to-boundary clearance is below the configured minimum",
                    feature_ids=(feature.feature_id,),
                    measured=clearance,
                    limit=boundary_clearance,
                    unit="um",
                    location_um=_location(polygon),
                )

    keep_outs = _coerce_keep_outs(config)
    for _, feature, polygon in valid_entries:
        for keepout_index, keepout in enumerate(keep_outs):
            if polygon.intersects(keepout):
                add(
                    "keep_out",
                    f"feature intersects keep-out polygon {keepout_index}",
                    feature_ids=(feature.feature_id,),
                    location_um=_location(polygon.intersection(keepout)),
                )

    allowed_layers = config.get("allowed_dxf_layers")
    if allowed_layers is not None:
        if not isinstance(allowed_layers, Sequence) or isinstance(allowed_layers, (str, bytes)):
            raise ValueError("allowed_dxf_layers must be a list")
        allowed = set(str(value) for value in allowed_layers)
        for feature in layout.features:
            if feature.dxf_layer not in allowed:
                add(
                    "dxf_layer",
                    f"DXF layer {feature.dxf_layer!r} is not in the production allowlist",
                    feature_ids=(feature.feature_id,),
                )

    minimum_bridge_seen = math.inf
    if valid_entries:
        geometries = [entry[2] for entry in valid_entries]
        tree = STRtree(geometries)
        geometry_id_to_index = {id(geometry): index for index, geometry in enumerate(geometries)}
        checked_pairs: set[tuple[int, int]] = set()
        for tree_index, (_, first_feature, first_geometry) in enumerate(valid_entries):
            query_geometry = (
                first_geometry.buffer(minimum_bridge + tolerance)
                if minimum_bridge
                else first_geometry
            )
            candidates = _candidate_indices(
                tree.query(query_geometry),
                geometry_id_to_index=geometry_id_to_index,
            )
            for other_tree_index in candidates:
                if other_tree_index == tree_index:
                    continue
                pair = tuple(sorted((tree_index, other_tree_index)))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                _, second_feature, second_geometry = valid_entries[other_tree_index]
                feature_ids = (first_feature.feature_id, second_feature.feature_id)
                if first_geometry.equals(second_geometry):
                    add(
                        "duplicate_polygon",
                        "two features have the same polygon geometry",
                        feature_ids=feature_ids,
                        location_um=_location(first_geometry),
                    )
                    continue
                if first_geometry.intersects(second_geometry):
                    intersection = first_geometry.intersection(second_geometry)
                    add(
                        "feature_overlap",
                        "two fabrication features overlap or touch",
                        feature_ids=feature_ids,
                        measured=float(intersection.area),
                        limit=0.0,
                        unit="um^2",
                        location_um=_location(intersection),
                    )
                    continue
                distance = float(first_geometry.distance(second_geometry))
                minimum_bridge_seen = min(minimum_bridge_seen, distance)
                if minimum_bridge and distance + tolerance < minimum_bridge:
                    add(
                        "min_bridge",
                        "silicon bridge between features is below the configured minimum",
                        feature_ids=feature_ids,
                        measured=distance,
                        limit=minimum_bridge,
                        unit="um",
                    )

    report.metrics.update(
        {
            "valid_polygon_count": len(valid_entries),
            "minimum_hole_width_um": (
                None if math.isinf(minimum_width_seen) else minimum_width_seen
            ),
            "minimum_edge_length_um": (
                None if math.isinf(minimum_edge_seen) else minimum_edge_seen
            ),
            "minimum_bridge_um": (
                None if math.isinf(minimum_bridge_seen) else minimum_bridge_seen
            ),
            "minimum_boundary_clearance_um": (
                None
                if math.isinf(minimum_boundary_clearance_seen)
                else minimum_boundary_clearance_seen
            ),
            "address_grid_um": grid[0] if grid else None,
        }
    )
    return report


__all__ = [
    "DrcError",
    "DrcReport",
    "DrcViolation",
    "run_drc",
]
