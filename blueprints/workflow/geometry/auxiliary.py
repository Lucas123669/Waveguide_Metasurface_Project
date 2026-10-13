"""Auxiliary air-etch geometry for outer windows and parameter labels."""

from __future__ import annotations

from dataclasses import replace
import math
from typing import Any, Mapping, Sequence

from shapely import affinity
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

from ..config import resolve_outer_window_radial_width_um
from ..models import LayoutFeature, LayoutPlan


OUTER_WINDOWS_KIND_V1 = "segmented_hex_etch_windows_v1"
OUTER_WINDOWS_KIND = "segmented_hex_ring_windows_v2"
PARAMETER_LABEL_KIND = "seven_segment_parameter_label_v1"


_DIGIT_SEGMENTS: dict[str, tuple[str, ...]] = {
    "0": ("a", "b", "c", "d", "e", "f"),
    "1": ("b", "c"),
    "2": ("a", "b", "g", "e", "d"),
    "3": ("a", "b", "c", "d", "g"),
    "4": ("f", "g", "b", "c"),
    "5": ("a", "f", "g", "c", "d"),
    "6": ("a", "f", "g", "e", "c", "d"),
    "7": ("a", "b", "c"),
    "8": ("a", "b", "c", "d", "e", "f", "g"),
    "9": ("a", "b", "c", "d", "f", "g"),
}


def _number(value: object, name: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    resolved = float(value)
    if not math.isfinite(resolved):
        raise ValueError(f"{name} must be finite")
    if positive and resolved <= 0.0:
        raise ValueError(f"{name} must be positive")
    return resolved


def _rounded_polygon(polygon: Polygon, radius_um: float, quad_segments: int) -> Polygon:
    if radius_um <= 0.0:
        return polygon
    rounded = polygon.buffer(
        -radius_um,
        join_style="round",
        quad_segs=quad_segments,
    ).buffer(
        radius_um,
        join_style="round",
        quad_segs=quad_segments,
    )
    if not isinstance(rounded, Polygon) or rounded.is_empty or not rounded.is_valid:
        raise ValueError("outer etch window corner radius collapses the polygon")
    return rounded


def _build_outer_etch_windows_v1(
    boundary: Polygon,
    config: Mapping[str, Any],
) -> list[LayoutFeature]:
    """Build six trapezoidal windows around a counter-clockwise hex boundary."""

    if config.get("kind") == "none":
        return []
    if config.get("kind") != OUTER_WINDOWS_KIND_V1:
        raise ValueError(f"unsupported outer etch window kind: {config.get('kind')!r}")
    reference = str(config["reference"])
    if reference != "finite_boundary":
        raise ValueError("outer etch windows currently require reference='finite_boundary'")

    inner_clearance = _number(
        config["inner_clearance_um"], "outer_etch_windows.inner_clearance_um", positive=True
    )
    radial_width = _number(
        config["radial_width_um"], "outer_etch_windows.radial_width_um", positive=True
    )
    end_clearance = _number(
        config["inner_end_clearance_um"],
        "outer_etch_windows.inner_end_clearance_um",
    )
    extension = _number(
        config["outer_tangential_extension_um"],
        "outer_etch_windows.outer_tangential_extension_um",
    )
    radius = _number(config["corner_radius_um"], "outer_etch_windows.corner_radius_um")
    quad_segments = int(config["arc_segments_per_quadrant"])
    layer = str(config["dxf_layer"])

    oriented = orient(boundary, sign=1.0)
    vertices = list(oriented.exterior.coords[:-1])
    if len(vertices) != 6:
        raise ValueError("segmented hex etch windows require a six-vertex finite boundary")

    features: list[LayoutFeature] = []
    for side_index, (start, end) in enumerate(zip(vertices, vertices[1:] + vertices[:1])):
        x0, y0 = (float(start[0]), float(start[1]))
        x1, y1 = (float(end[0]), float(end[1]))
        dx = x1 - x0
        dy = y1 - y0
        length = math.hypot(dx, dy)
        if 2.0 * end_clearance >= length:
            raise ValueError(
                "outer_etch_windows.inner_end_clearance_um must be less than half "
                "the finite-boundary side length"
            )
        tx, ty = dx / length, dy / length
        # A counter-clockwise polygon has its interior on the left of each edge.
        nx, ny = ty, -tx
        inner_start = (
            x0 + tx * end_clearance + nx * inner_clearance,
            y0 + ty * end_clearance + ny * inner_clearance,
        )
        inner_end = (
            x1 - tx * end_clearance + nx * inner_clearance,
            y1 - ty * end_clearance + ny * inner_clearance,
        )
        outer_start = (
            inner_start[0] - tx * extension + nx * radial_width,
            inner_start[1] - ty * extension + ny * radial_width,
        )
        outer_end = (
            inner_end[0] + tx * extension + nx * radial_width,
            inner_end[1] + ty * extension + ny * radial_width,
        )
        polygon = Polygon((inner_start, inner_end, outer_end, outer_start))
        if polygon.is_empty or not polygon.is_valid:
            raise ValueError(f"outer etch window side {side_index} is invalid")
        polygon = _rounded_polygon(polygon, radius, quad_segments)
        local_angle = math.degrees(math.atan2(ty, tx))
        features.append(
            LayoutFeature(
                feature_id=f"outer_etch_window/side{side_index}",
                region="outer_etch_window",
                parent_i=side_index,
                parent_j=0,
                group_id=side_index,
                local_index=0,
                layer=0,
                nominal_polygon=polygon,
                polygon=polygon,
                shift_um=(0.0, 0.0),
                dxf_layer=layer,
                metadata={
                    "auxiliary_kind": OUTER_WINDOWS_KIND_V1,
                    "side_index": side_index,
                    "local_axis_angle_deg": local_angle,
                    "boundary_check": False,
                    "preview_comparison": False,
                },
            )
        )

    for index, first in enumerate(features):
        for second in features[index + 1 :]:
            if first.polygon.intersects(second.polygon):
                raise ValueError(
                    f"outer etch windows {first.feature_id} and {second.feature_id} overlap"
                )
    return features




def _unit_vector(
    start: tuple[float, float],
    end: tuple[float, float],
) -> tuple[tuple[float, float], float]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length <= 0.0:
        raise ValueError("outer etch window contains a zero-length edge")
    return (dx / length, dy / length), length


def _selective_corner_fillet(
    vertices: Sequence[tuple[float, float]],
    *,
    rounded_indices: set[int],
    radius_um: float,
    arc_segments_per_quadrant: int,
) -> Polygon:
    """Fillet selected convex vertices while preserving unselected vertices."""

    base = Polygon(vertices)
    if radius_um <= 0.0:
        return base
    if arc_segments_per_quadrant <= 0:
        raise ValueError("arc_segments_per_quadrant must be positive")

    signed_twice_area = sum(
        first[0] * second[1] - second[0] * first[1]
        for first, second in zip(vertices, vertices[1:] + vertices[:1])
    )
    orientation_sign = 1.0 if signed_twice_area > 0.0 else -1.0
    resolved: list[tuple[float, float]] = []
    vertex_count = len(vertices)

    for index, vertex in enumerate(vertices):
        if index not in rounded_indices:
            resolved.append(vertex)
            continue

        previous = vertices[(index - 1) % vertex_count]
        following = vertices[(index + 1) % vertex_count]
        toward_previous, previous_length = _unit_vector(vertex, previous)
        toward_following, following_length = _unit_vector(vertex, following)
        cosine = max(
            -1.0,
            min(
                1.0,
                toward_previous[0] * toward_following[0]
                + toward_previous[1] * toward_following[1],
            ),
        )
        interior_angle = math.acos(cosine)
        if interior_angle <= 0.0 or interior_angle >= math.pi:
            raise ValueError("outer etch window fillet requires a convex corner")
        tangent_distance = radius_um / math.tan(interior_angle / 2.0)
        if tangent_distance >= min(previous_length, following_length):
            raise ValueError(
                "outer_etch_windows.inner_corner_radius_um is too large for "
                "the inner edge or adjacent radial edge"
            )

        first_tangent = (
            vertex[0] + toward_previous[0] * tangent_distance,
            vertex[1] + toward_previous[1] * tangent_distance,
        )
        second_tangent = (
            vertex[0] + toward_following[0] * tangent_distance,
            vertex[1] + toward_following[1] * tangent_distance,
        )
        bisector_x = toward_previous[0] + toward_following[0]
        bisector_y = toward_previous[1] + toward_following[1]
        bisector_length = math.hypot(bisector_x, bisector_y)
        if bisector_length <= 0.0:
            raise ValueError("outer etch window fillet has no interior bisector")
        center_distance = radius_um / math.sin(interior_angle / 2.0)
        center = (
            vertex[0] + bisector_x / bisector_length * center_distance,
            vertex[1] + bisector_y / bisector_length * center_distance,
        )
        start_angle = math.atan2(
            first_tangent[1] - center[1], first_tangent[0] - center[0]
        )
        end_angle = math.atan2(
            second_tangent[1] - center[1], second_tangent[0] - center[0]
        )
        if orientation_sign > 0.0:
            sweep = (end_angle - start_angle) % (2.0 * math.pi)
        else:
            sweep = -((start_angle - end_angle) % (2.0 * math.pi))
        segment_count = max(
            1,
            math.ceil(
                abs(sweep) / (math.pi / 2.0) * arc_segments_per_quadrant
            ),
        )
        for arc_index in range(segment_count + 1):
            angle = start_angle + sweep * arc_index / segment_count
            resolved.append(
                (
                    center[0] + radius_um * math.cos(angle),
                    center[1] + radius_um * math.sin(angle),
                )
            )

    rounded = Polygon(resolved)
    if rounded.is_empty or not rounded.is_valid or rounded.area <= 0.0:
        raise ValueError("outer etch window selective fillet produced invalid geometry")
    return rounded


def _build_outer_etch_windows_v2(
    boundary: Polygon,
    config: Mapping[str, Any],
    geometry: Mapping[str, Any] | None,
) -> list[LayoutFeature]:
    """Build six radial-sided segments with an explicit adjacent-side gap."""

    inner_clearance = _number(
        config["inner_clearance_um"], "outer_etch_windows.inner_clearance_um"
    )
    if inner_clearance < 0.0:
        raise ValueError("outer_etch_windows.inner_clearance_um must be non-negative")
    radial_width = resolve_outer_window_radial_width_um(config, geometry)
    finite_total_layers = None
    radial_width_rule = None
    if "radial_width" in config:
        if geometry is None:
            raise ValueError(
                "geometry is required to resolve outer_etch_windows.radial_width"
            )
        finite = geometry["finite"]
        finite_total_layers = int(finite["cavity_layers"]) + int(
            finite["cladding_layers"]
        )
        radial_width_rule = dict(config["radial_width"])
    parallel_side_gap = _number(
        config["parallel_side_gap_um"],
        "outer_etch_windows.parallel_side_gap_um",
        positive=True,
    )
    radius = _number(
        config["inner_corner_radius_um"],
        "outer_etch_windows.inner_corner_radius_um",
    )
    if radius < 0.0:
        raise ValueError(
            "outer_etch_windows.inner_corner_radius_um must be non-negative"
        )
    quad_segments = int(config["arc_segments_per_quadrant"])
    layer = str(config["dxf_layer"])

    oriented = orient(boundary, sign=1.0)
    vertices = [
        (float(point[0]), float(point[1]))
        for point in oriented.exterior.coords[:-1]
    ]
    if len(vertices) != 6:
        raise ValueError("segmented hex ring windows require a six-vertex finite boundary")
    center = (float(oriented.centroid.x), float(oriented.centroid.y))

    side_vectors: list[tuple[tuple[float, float], tuple[float, float], float]] = []
    for start, end in zip(vertices, vertices[1:] + vertices[:1]):
        (tx, ty), side_length = _unit_vector(start, end)
        side_vectors.append(((tx, ty), (ty, -tx), side_length))

    vertex_trims: list[float] = []
    intrinsic_gaps: list[float] = []
    for vertex_index, vertex in enumerate(vertices):
        previous_tangent, previous_normal, _ = side_vectors[vertex_index - 1]
        following_tangent, following_normal, _ = side_vectors[vertex_index]
        radial, _ = _unit_vector(center, vertex)
        gap_normal = (-radial[1], radial[0])
        previous_inner = (
            vertex[0] + previous_normal[0] * inner_clearance,
            vertex[1] + previous_normal[1] * inner_clearance,
        )
        following_inner = (
            vertex[0] + following_normal[0] * inner_clearance,
            vertex[1] + following_normal[1] * inner_clearance,
        )
        separation = (
            following_inner[0] - previous_inner[0],
            following_inner[1] - previous_inner[1],
        )
        intrinsic_gap = (
            separation[0] * gap_normal[0] + separation[1] * gap_normal[1]
        )
        trim_gain = (
            (previous_tangent[0] + following_tangent[0]) * gap_normal[0]
            + (previous_tangent[1] + following_tangent[1]) * gap_normal[1]
        )
        if trim_gain < 0.0:
            intrinsic_gap = -intrinsic_gap
            trim_gain = -trim_gain
        if trim_gain <= 1e-12:
            raise ValueError(
                "segmented hex ring windows cannot resolve the parallel-side gap "
                "for this boundary"
            )
        if parallel_side_gap + 1e-12 < intrinsic_gap:
            raise ValueError(
                "outer_etch_windows.parallel_side_gap_um must be at least the "
                "clearance-induced adjacent-side gap"
            )
        vertex_trims.append((parallel_side_gap - intrinsic_gap) / trim_gain)
        intrinsic_gaps.append(intrinsic_gap)

    features: list[LayoutFeature] = []
    for side_index, (start, end) in enumerate(
        zip(vertices, vertices[1:] + vertices[:1])
    ):
        (tx, ty), (nx, ny), side_length = side_vectors[side_index]
        start_trim = vertex_trims[side_index]
        end_trim = vertex_trims[(side_index + 1) % len(vertices)]
        if start_trim + end_trim >= side_length:
            raise ValueError(
                "outer_etch_windows.parallel_side_gap_um collapses an inner edge"
            )
        start_radial, _ = _unit_vector(center, start)
        end_radial, _ = _unit_vector(center, end)
        start_projection = start_radial[0] * nx + start_radial[1] * ny
        end_projection = end_radial[0] * nx + end_radial[1] * ny
        if start_projection <= 0.0 or end_projection <= 0.0:
            raise ValueError(
                "segmented hex ring windows require the boundary centroid to "
                "lie inside a convex six-sided boundary"
            )

        inner_start = (
            start[0] + nx * inner_clearance + tx * start_trim,
            start[1] + ny * inner_clearance + ty * start_trim,
        )
        inner_end = (
            end[0] + nx * inner_clearance - tx * end_trim,
            end[1] + ny * inner_clearance - ty * end_trim,
        )
        outer_start = (
            inner_start[0]
            + start_radial[0] * radial_width / start_projection,
            inner_start[1]
            + start_radial[1] * radial_width / start_projection,
        )
        outer_end = (
            inner_end[0] + end_radial[0] * radial_width / end_projection,
            inner_end[1] + end_radial[1] * radial_width / end_projection,
        )
        polygon = _selective_corner_fillet(
            (inner_start, inner_end, outer_end, outer_start),
            rounded_indices={0, 1},
            radius_um=radius,
            arc_segments_per_quadrant=quad_segments,
        )
        features.append(
            LayoutFeature(
                feature_id=f"outer_etch_window/side{side_index}",
                region="outer_etch_window",
                parent_i=side_index,
                parent_j=0,
                group_id=side_index,
                local_index=0,
                layer=0,
                nominal_polygon=polygon,
                polygon=polygon,
                shift_um=(0.0, 0.0),
                dxf_layer=layer,
                metadata={
                    "auxiliary_kind": OUTER_WINDOWS_KIND,
                    "side_index": side_index,
                    "local_axis_angle_deg": math.degrees(math.atan2(ty, tx)),
                    "reference_side_length_um": side_length,
                    "inner_reference_length_um": math.dist(inner_start, inner_end),
                    "inner_clearance_um": inner_clearance,
                    "radial_width_um": radial_width,
                    "radial_width_rule": radial_width_rule,
                    "finite_total_layers": finite_total_layers,
                    "parallel_side_gap_um": parallel_side_gap,
                    "clearance_induced_start_gap_um": intrinsic_gaps[side_index],
                    "start_tangential_trim_um": start_trim,
                    "end_tangential_trim_um": end_trim,
                    "inner_corner_radius_um": radius,
                    "rounded_inner_corner_count": 2 if radius > 0.0 else 0,
                    "outer_corner_radius_um": 0.0,
                    "boundary_check": False,
                    "preview_comparison": False,
                },
            )
        )

    for index, first in enumerate(features):
        for second in features[index + 1 :]:
            intersection = first.polygon.intersection(second.polygon)
            if intersection.area > 1e-12:
                raise ValueError(
                    f"outer etch windows {first.feature_id} and "
                    f"{second.feature_id} overlap"
                )
            if first.polygon.intersects(second.polygon):
                raise ValueError(
                    f"outer etch windows {first.feature_id} and "
                    f"{second.feature_id} touch despite positive parallel-side gap"
                )
    return features


def build_outer_etch_windows(
    boundary: Polygon,
    config: Mapping[str, Any],
    *,
    geometry: Mapping[str, Any] | None = None,
) -> list[LayoutFeature]:
    """Build configured etch windows around a six-sided finite boundary."""

    kind = config.get("kind")
    if kind == "none":
        return []
    if kind not in {OUTER_WINDOWS_KIND_V1, OUTER_WINDOWS_KIND}:
        raise ValueError(f"unsupported outer etch window kind: {kind!r}")
    if str(config["reference"]) != "finite_boundary":
        raise ValueError("outer etch windows currently require reference='finite_boundary'")
    if kind == OUTER_WINDOWS_KIND_V1:
        return _build_outer_etch_windows_v1(boundary, config)
    return _build_outer_etch_windows_v2(boundary, config, geometry)


def _fixed(value: object, decimals: int, *, trim: bool) -> str:
    text = f"{float(value):.{decimals}f}"
    if trim and "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def parameter_label_text(
    geometry: Mapping[str, Any],
    config: Mapping[str, Any],
) -> str:
    """Resolve the exact calculator-style text from compact cell parameters."""

    unit_cell = geometry["unit_cell"]
    cavity = unit_cell["cavity"]
    cladding = unit_cell["cladding"]
    b0_decimals = int(config["b0_decimals"])
    eta_decimals = int(config["eta_decimals"])
    zeta_decimals = int(config["zeta_max_decimals"])
    trim_zeta = bool(config["trim_zeta_trailing_zeros"])

    def cell_text(cell: Mapping[str, Any]) -> str:
        return " ".join(
            (
                _fixed(cell["b0_nm"], b0_decimals, trim=False),
                _fixed(cell["eta"], eta_decimals, trim=False),
                _fixed(cell["zeta"], zeta_decimals, trim=trim_zeta),
            )
        )

    return f"{cell_text(cavity)} — {cell_text(cladding)}"


def _horizontal_stick(
    x: float,
    center_y: float,
    length: float,
    thickness: float,
    bevel: float,
) -> Polygon:
    half = thickness / 2.0
    resolved_bevel = min(bevel, half, length / 2.0)
    return Polygon(
        (
            (x, center_y),
            (x + resolved_bevel, center_y - half),
            (x + length - resolved_bevel, center_y - half),
            (x + length, center_y),
            (x + length - resolved_bevel, center_y + half),
            (x + resolved_bevel, center_y + half),
        )
    )


def _vertical_stick(
    center_x: float,
    y: float,
    length: float,
    thickness: float,
    bevel: float,
) -> Polygon:
    half = thickness / 2.0
    resolved_bevel = min(bevel, half, length / 2.0)
    return Polygon(
        (
            (center_x, y),
            (center_x + half, y + resolved_bevel),
            (center_x + half, y + length - resolved_bevel),
            (center_x, y + length),
            (center_x - half, y + length - resolved_bevel),
            (center_x - half, y + resolved_bevel),
        )
    )


def _digit_segment_polygons(
    digit: str,
    x: float,
    *,
    height: float,
    width: float,
    thickness: float,
    gap: float,
    bevel: float,
) -> list[tuple[str, Polygon]]:
    horizontal_x = x + thickness / 2.0 + gap
    horizontal_length = width - thickness - 2.0 * gap
    vertical_length = height / 2.0 - 1.5 * thickness - 2.0 * gap
    if horizontal_length <= 0.0 or vertical_length <= 0.0:
        raise ValueError("seven-segment glyph dimensions leave no positive segment length")
    lower_y = thickness + gap
    upper_y = height / 2.0 + thickness / 2.0 + gap
    left_x = x + thickness / 2.0
    right_x = x + width - thickness / 2.0
    candidates = {
        "a": _horizontal_stick(
            horizontal_x, height - thickness / 2.0, horizontal_length, thickness, bevel
        ),
        "g": _horizontal_stick(
            horizontal_x, height / 2.0, horizontal_length, thickness, bevel
        ),
        "d": _horizontal_stick(
            horizontal_x, thickness / 2.0, horizontal_length, thickness, bevel
        ),
        "f": _vertical_stick(
            left_x, upper_y, vertical_length, thickness, bevel
        ),
        "b": _vertical_stick(
            right_x, upper_y, vertical_length, thickness, bevel
        ),
        "e": _vertical_stick(
            left_x, lower_y, vertical_length, thickness, bevel
        ),
        "c": _vertical_stick(
            right_x, lower_y, vertical_length, thickness, bevel
        ),
    }
    return [(name, candidates[name]) for name in _DIGIT_SEGMENTS[digit]]


def _append_marker_feature(
    features: list[LayoutFeature],
    polygon: Polygon,
    *,
    character_index: int,
    segment_name: str,
    display_text: str,
    layer: str,
) -> None:
    feature_index = len(features)
    features.append(
        LayoutFeature(
            feature_id=(
                f"parameter_marker/char{character_index}/"
                f"segment{segment_name}/{feature_index}"
            ),
            region="parameter_marker",
            parent_i=character_index,
            parent_j=0,
            group_id=character_index,
            local_index=feature_index,
            layer=0,
            nominal_polygon=polygon,
            polygon=polygon,
            shift_um=(0.0, 0.0),
            dxf_layer=layer,
            metadata={
                "auxiliary_kind": PARAMETER_LABEL_KIND,
                "display_text": display_text,
                "character_index": character_index,
                "segment_name": segment_name,
                "local_axis_angle_deg": 0.0,
                "boundary_check": False,
                "preview_comparison": False,
            },
        )
    )


def build_parameter_marker(
    layout: LayoutPlan,
    geometry: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    outer_windows: Sequence[LayoutFeature],
) -> tuple[list[LayoutFeature], str | None]:
    """Build a centered seven-segment label below the selected reference geometry."""

    if config.get("kind") == "none":
        return [], None
    if config.get("kind") != PARAMETER_LABEL_KIND:
        raise ValueError(f"unsupported parameter marker kind: {config.get('kind')!r}")
    if config["source"] != "geometry.unit_cell.cavity_cladding":
        raise ValueError(
            "parameter marker currently requires source="
            "'geometry.unit_cell.cavity_cladding'"
        )

    height = _number(config["digit_height_um"], "markers.digit_height_um", positive=True)
    width = _number(config["digit_width_um"], "markers.digit_width_um", positive=True)
    thickness = _number(
        config["segment_thickness_um"], "markers.segment_thickness_um", positive=True
    )
    gap = _number(config["segment_gap_um"], "markers.segment_gap_um")
    bevel = _number(config["segment_bevel_um"], "markers.segment_bevel_um")
    digit_spacing = _number(config["digit_spacing_um"], "markers.digit_spacing_um")
    decimal_size = _number(config["decimal_size_um"], "markers.decimal_size_um", positive=True)
    decimal_gap = _number(config["decimal_gap_um"], "markers.decimal_gap_um")
    value_spacing = _number(config["value_spacing_um"], "markers.value_spacing_um")
    group_spacing = _number(config["group_spacing_um"], "markers.group_spacing_um")
    dash_length = _number(config["dash_length_um"], "markers.dash_length_um", positive=True)
    dash_thickness = _number(
        config["dash_thickness_um"], "markers.dash_thickness_um", positive=True
    )
    top_clearance = _number(config["top_clearance_um"], "markers.top_clearance_um", positive=True)
    center_x = _number(config["center_x_um"], "markers.center_x_um")
    layer = str(config["dxf_layer"])
    display_text = parameter_label_text(geometry, config)
    groups = display_text.split(" — ")
    if len(groups) != 2:
        raise ValueError("parameter marker text must resolve to exactly two groups")

    features: list[LayoutFeature] = []
    cursor_x = 0.0
    character_index = 0
    for group_index, group in enumerate(groups):
        values = group.split(" ")
        for value_index, value in enumerate(values):
            for token_index, character in enumerate(value):
                if character in _DIGIT_SEGMENTS:
                    for segment_name, polygon in _digit_segment_polygons(
                        character,
                        cursor_x,
                        height=height,
                        width=width,
                        thickness=thickness,
                        gap=gap,
                        bevel=bevel,
                    ):
                        _append_marker_feature(
                            features,
                            polygon,
                            character_index=character_index,
                            segment_name=segment_name,
                            display_text=display_text,
                            layer=layer,
                        )
                    cursor_x += width
                elif character == ".":
                    cursor_x += decimal_gap
                    polygon = Polygon(
                        (
                            (cursor_x + decimal_size / 2.0, 0.0),
                            (cursor_x + decimal_size, decimal_size / 2.0),
                            (cursor_x + decimal_size / 2.0, decimal_size),
                            (cursor_x, decimal_size / 2.0),
                        )
                    )
                    _append_marker_feature(
                        features,
                        polygon,
                        character_index=character_index,
                        segment_name="decimal",
                        display_text=display_text,
                        layer=layer,
                    )
                    cursor_x += decimal_size
                else:  # pragma: no cover - guarded by the formatter above
                    raise ValueError(f"unsupported seven-segment character: {character!r}")
                character_index += 1
                if token_index != len(value) - 1:
                    cursor_x += digit_spacing
            if value_index != len(values) - 1:
                cursor_x += value_spacing
        if group_index == 0:
            cursor_x += group_spacing
            dash = _horizontal_stick(
                cursor_x,
                height / 2.0,
                dash_length,
                dash_thickness,
                bevel,
            )
            _append_marker_feature(
                features,
                dash,
                character_index=character_index,
                segment_name="long_dash",
                display_text=display_text,
                layer=layer,
            )
            character_index += 1
            cursor_x += dash_length + group_spacing

    if not features:
        raise ValueError("parameter marker resolved to no fabrication segments")
    min_x = min(feature.polygon.bounds[0] for feature in features)
    max_x = max(feature.polygon.bounds[2] for feature in features)
    max_y = max(feature.polygon.bounds[3] for feature in features)
    if config["anchor"] == "below_outer_etch_windows" and outer_windows:
        reference_min_y = min(feature.polygon.bounds[1] for feature in outer_windows)
    elif config["anchor"] in {"below_outer_etch_windows", "below_finite_boundary"}:
        if layout.boundary is None:
            raise ValueError("parameter marker anchor requires a finite boundary")
        reference_min_y = float(layout.boundary.bounds[1])
    else:
        raise ValueError(f"unsupported parameter marker anchor: {config['anchor']!r}")
    offset_x = center_x - 0.5 * (min_x + max_x)
    offset_y = reference_min_y - top_clearance - max_y
    translated: list[LayoutFeature] = []
    for feature in features:
        polygon = affinity.translate(feature.polygon, xoff=offset_x, yoff=offset_y)
        translated.append(
            replace(
                feature,
                nominal_polygon=polygon,
                polygon=polygon,
            )
        )
    return translated, display_text


def add_auxiliary_geometry(
    layout: LayoutPlan,
    *,
    geometry: Mapping[str, Any],
    outer_etch_windows: Mapping[str, Any],
    markers: Mapping[str, Any],
) -> LayoutPlan:
    """Append enabled auxiliary air features while preserving the finite boundary."""

    if layout.boundary is None and outer_etch_windows.get("kind") != "none":
        raise ValueError("outer etch windows require a finite layout boundary")
    windows = (
        []
        if layout.boundary is None
        else build_outer_etch_windows(
            layout.boundary,
            outer_etch_windows,
            geometry=geometry,
        )
    )
    marker_features, display_text = build_parameter_marker(
        layout,
        geometry,
        markers,
        outer_windows=windows,
    )
    metadata = dict(layout.metadata)
    metadata["auxiliary_geometry"] = {
        "outer_etch_windows": {
            "kind": outer_etch_windows["kind"],
            "feature_count": len(windows),
            "radial_width_um": (
                windows[0].metadata.get("radial_width_um") if windows else None
            ),
            "radial_width_rule": (
                windows[0].metadata.get("radial_width_rule") if windows else None
            ),
            "finite_total_layers": (
                windows[0].metadata.get("finite_total_layers") if windows else None
            ),
        },
        "parameter_marker": {
            "kind": markers["kind"],
            "display_text": display_text,
            "feature_count": len(marker_features),
        },
    }
    return layout.with_features(
        [*layout.features, *windows, *marker_features],
        metadata=metadata,
    )


__all__ = [
    "OUTER_WINDOWS_KIND",
    "PARAMETER_LABEL_KIND",
    "add_auxiliary_geometry",
    "build_outer_etch_windows",
    "build_parameter_marker",
    "parameter_label_text",
    "resolve_outer_window_radial_width_um",
]
