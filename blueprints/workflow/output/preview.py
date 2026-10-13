"""One-page visual quality check for nominal and corrected layouts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import PatchCollection
from matplotlib.figure import Figure
from matplotlib.patches import Polygon as PolygonPatch
from shapely.geometry import Polygon

from ..fabrication.corrections import (
    spatial_envelope_from_mapping,
    triangle_side_correction_from_mapping,
)
from ..fabrication.sem_calibration import SIDE_TO_EDGE_OFFSET
from ..models import LayoutFeature, LayoutPlan


_REGION_COLORS = {
    "cavity": "#255f85",
    "cladding": "#8db8cf",
    "outer_etch_window": "#c7793f",
    "parameter_marker": "#4f4f4f",
    "marker": "#5f6368",
    "die": "#8a8a8a",
}

_RADIAL_STRIP_TITLE = "Radial cell strip"
_CORRECTION_FUNCTION_TITLE = "Applied side-length correction along radial strip"
_CORRECTION_SAMPLE_COUNT = 241
_PREVIEW_FIGURE_SIZE = (15.7, 8.2)
_PREVIEW_WIDTH_RATIOS = (2.10, 0.85, 1.90)
_PREVIEW_HEIGHT_RATIOS = (1.0, 1.0, 0.36)
_PREVIEW_CONSTRAINED_PADS = {
    "w_pad": 0.02,
    "h_pad": 0.02,
    "wspace": 0.015,
    "hspace": 0.02,
}
_COMPARISON_HSPACE = 0.04
_POSITION_STYLES = (
    ("center", "Center", "center", "#2b83ba"),
    ("cavity_boundary", "Cavity boundary", "cavity boundary", "#d28e39"),
    ("cladding_boundary", "Cladding boundary", "cladding boundary", "#9b5a83"),
)


@dataclass(frozen=True, slots=True)
class _RadialStripSelection:
    groups: tuple[tuple[int, tuple[LayoutFeature, ...], tuple[float, float]], ...]
    origin_um: tuple[float, float]
    direction: tuple[float, float]
    transverse: tuple[float, float]
    period_um: float
    half_width_um: float
    cavity_layers: int | None

    @property
    def shells(self) -> tuple[int, ...]:
        return tuple(group[0] for group in self.groups)


@dataclass(frozen=True, slots=True)
class _RadialReference:
    key: str
    title: str
    plot_label: str
    shell: int
    feature: LayoutFeature
    cell_center_um: tuple[float, float]
    color: str


def _region_color(region: str) -> str:
    lowered = region.casefold()
    for name, color in _REGION_COLORS.items():
        if name in lowered:
            return color
    return "#4f86a6"


def _draw_global(axis: Any, layout: LayoutPlan) -> None:
    patches: list[PolygonPatch] = []
    colors: list[str] = []
    for feature in layout.features:
        coordinates = list(feature.polygon.exterior.coords)
        if len(coordinates) < 4:
            continue
        patches.append(PolygonPatch(coordinates, closed=True))
        colors.append(_region_color(feature.region))

    if patches:
        collection = PatchCollection(
            patches,
            facecolors=colors,
            edgecolors="none",
            linewidths=0.0,
            rasterized=True,
        )
        axis.add_collection(collection)
    else:
        axis.text(
            0.5,
            0.5,
            "No fabrication features",
            ha="center",
            va="center",
            color="#666666",
            transform=axis.transAxes,
        )

    display_bounds = layout.bounds
    if layout.boundary is not None and not layout.boundary.is_empty:
        bx, by = layout.boundary.exterior.xy
        axis.plot(bx, by, color="#555555", linewidth=0.7)
        boundary_bounds = tuple(float(value) for value in layout.boundary.bounds)
        if display_bounds is None:
            display_bounds = boundary_bounds
        else:
            display_bounds = (
                min(display_bounds[0], boundary_bounds[0]),
                min(display_bounds[1], boundary_bounds[1]),
                max(display_bounds[2], boundary_bounds[2]),
                max(display_bounds[3], boundary_bounds[3]),
            )

    if display_bounds is not None:
        _set_bounds(axis, display_bounds, fraction=0.025)
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlabel("x (µm)")
    axis.set_ylabel("y (µm)")
    axis.set_title("Corrected layout", loc="left", fontsize=10)


def _set_bounds(
    axis: Any,
    bounds: tuple[float, float, float, float],
    *,
    fraction: float,
) -> None:
    min_x, min_y, max_x, max_y = bounds
    width = max_x - min_x
    height = max_y - min_y
    reference = max(width, height, 1e-6)
    pad_x = max(width * fraction, reference * 0.01)
    pad_y = max(height * fraction, reference * 0.01)
    axis.set_xlim(min_x - pad_x, max_x + pad_x)
    axis.set_ylim(min_y - pad_y, max_y + pad_y)


def _representative_features(
    layout: LayoutPlan,
) -> tuple[LayoutFeature | None, LayoutFeature | None]:
    candidates = [
        feature
        for feature in layout.features
        if feature.metadata.get("preview_comparison", True) is not False
    ]
    if not candidates:
        return None, None

    center_value = layout.metadata.get("write_field_center_um")
    if (
        isinstance(center_value, Sequence)
        and not isinstance(center_value, (str, bytes))
        and len(center_value) == 2
    ):
        center = (float(center_value[0]), float(center_value[1]))
    elif layout.bounds is not None:
        center = (
            0.5 * (layout.bounds[0] + layout.bounds[2]),
            0.5 * (layout.bounds[1] + layout.bounds[3]),
        )
    else:  # pragma: no cover - guarded by the non-empty feature list
        center = (0.0, 0.0)

    def distance_squared(feature: LayoutFeature) -> float:
        x, y = feature.centroid_um
        return (x - center[0]) ** 2 + (y - center[1]) ** 2

    return (
        min(candidates, key=distance_squared),
        max(candidates, key=distance_squared),
    )


def _matching_nominal_polygon(
    nominal_by_id: Mapping[str, LayoutFeature], corrected_feature: LayoutFeature
) -> Polygon:
    nominal_feature = nominal_by_id.get(corrected_feature.feature_id)
    if nominal_feature is not None:
        return nominal_feature.polygon
    return corrected_feature.nominal_polygon


def _cell_center(features: Sequence[LayoutFeature]) -> tuple[float, float]:
    centroids = [feature.nominal_centroid_um for feature in features]
    return (
        sum(point[0] for point in centroids) / len(centroids),
        sum(point[1] for point in centroids) / len(centroids),
    )


def _select_radial_strip(layout: LayoutPlan) -> _RadialStripSelection | None:
    """Select one complete parent-cell ray from shell zero to the edge."""

    grouped: dict[tuple[int, int], list[LayoutFeature]] = {}
    for feature in layout.features:
        if feature.region not in {"cavity", "cladding"}:
            continue
        if feature.metadata.get("preview_comparison", True) is False:
            continue
        shell = feature.metadata.get("parent_shell")
        if type(shell) is not int or shell < 0:
            continue
        grouped.setdefault((feature.parent_i, feature.parent_j), []).append(feature)
    if not grouped:
        return None

    cells: list[tuple[int, tuple[LayoutFeature, ...], tuple[float, float]]] = []
    for features in grouped.values():
        shells = {int(feature.metadata["parent_shell"]) for feature in features}
        if len(shells) != 1:
            continue
        ordered = tuple(sorted(features, key=lambda feature: feature.local_index))
        cells.append((shells.pop(), ordered, _cell_center(ordered)))
    if not cells:
        return None

    center_cells = [cell for cell in cells if cell[0] == 0]
    if not center_cells:
        return None
    origin = center_cells[0][2]
    max_shell = max(cell[0] for cell in cells)
    if max_shell <= 0:
        return None
    outer_cells = [cell for cell in cells if cell[0] == max_shell]

    def outward_key(
        cell: tuple[int, tuple[LayoutFeature, ...], tuple[float, float]],
    ) -> tuple[float, float]:
        dx = cell[2][0] - origin[0]
        dy = cell[2][1] - origin[1]
        return (dx, -abs(dy))

    target = max(outer_cells, key=outward_key)
    dx = target[2][0] - origin[0]
    dy = target[2][1] - origin[1]
    distance = math.hypot(dx, dy)
    if distance <= 0.0:
        return None
    direction = (dx / distance, dy / distance)
    transverse = (-direction[1], direction[0])
    period = distance / max_shell
    ray_tolerance = max(period * 0.15, 1e-9)

    selected: list[
        tuple[int, tuple[LayoutFeature, ...], tuple[float, float]]
    ] = []
    for cell in cells:
        offset_x = cell[2][0] - origin[0]
        offset_y = cell[2][1] - origin[1]
        longitudinal = offset_x * direction[0] + offset_y * direction[1]
        perpendicular = offset_x * transverse[0] + offset_y * transverse[1]
        if longitudinal >= -ray_tolerance and abs(perpendicular) <= ray_tolerance:
            selected.append(cell)
    selected.sort(key=lambda cell: cell[0])
    if tuple(cell[0] for cell in selected) != tuple(range(max_shell + 1)):
        return None

    finite = layout.metadata.get("finite", {})
    cavity_layers_raw = finite.get("cavity_layers") if isinstance(finite, Mapping) else None
    cavity_layers = (
        cavity_layers_raw
        if type(cavity_layers_raw) is int and 0 <= cavity_layers_raw < max_shell
        else None
    )
    return _RadialStripSelection(
        groups=tuple(selected),
        origin_um=origin,
        direction=direction,
        transverse=transverse,
        period_um=period,
        half_width_um=period / math.sqrt(3.0),
        cavity_layers=cavity_layers,
    )


def _radial_references(
    selection: _RadialStripSelection | None,
) -> tuple[_RadialReference, ...]:
    """Resolve the three comparison triangles from the selected radial cells."""

    if selection is None:
        return ()
    groups_by_shell = {shell: (features, center) for shell, features, center in selection.groups}
    max_shell = selection.shells[-1]
    shell_by_key: dict[str, int | None] = {
        "center": 0,
        "cavity_boundary": selection.cavity_layers,
        "cladding_boundary": max_shell,
    }
    references: list[_RadialReference] = []
    for key, title, plot_label, color in _POSITION_STYLES:
        shell = shell_by_key[key]
        if shell is None or shell not in groups_by_shell:
            continue
        features, center = groups_by_shell[shell]
        if not features:
            continue
        references.append(
            _RadialReference(
                key=key,
                title=title,
                plot_label=plot_label,
                shell=shell,
                feature=features[0],
                cell_center_um=center,
                color=color,
            )
        )
    return tuple(references)


def _local_polygon_coordinates(
    polygon: Polygon,
    origin_um: tuple[float, float],
) -> list[tuple[float, float]]:
    return [
        (float(x) - origin_um[0], float(y) - origin_um[1])
        for x, y in polygon.exterior.coords
    ]


def _comparison_local_bounds(
    references: Sequence[_RadialReference],
    nominal_by_id: Mapping[str, LayoutFeature],
) -> tuple[float, float, float, float] | None:
    bounds: list[tuple[float, float, float, float]] = []
    for reference in references:
        nominal_polygon = _matching_nominal_polygon(
            nominal_by_id, reference.feature
        )
        for polygon in (nominal_polygon, reference.feature.polygon):
            min_x, min_y, max_x, max_y = polygon.bounds
            origin_x, origin_y = reference.cell_center_um
            bounds.append(
                (
                    float(min_x) - origin_x,
                    float(min_y) - origin_y,
                    float(max_x) - origin_x,
                    float(max_y) - origin_y,
                )
            )
    if not bounds:
        return None
    min_x = min(item[0] for item in bounds)
    min_y = min(item[1] for item in bounds)
    max_x = max(item[2] for item in bounds)
    max_y = max(item[3] for item in bounds)
    center_x = 0.5 * (min_x + max_x)
    center_y = 0.5 * (min_y + max_y)
    half_span = 0.6 * max(max_x - min_x, max_y - min_y, 1e-6)
    return (
        center_x - half_span,
        center_y - half_span,
        center_x + half_span,
        center_y + half_span,
    )


def _reference_tick_shells(selection: _RadialStripSelection) -> list[int]:
    max_shell = selection.shells[-1]
    ticks = {
        0,
        max_shell,
        *(round(max_shell * fraction / 4.0) for fraction in range(1, 4)),
    }
    if selection.cavity_layers is not None:
        ticks.add(selection.cavity_layers)
    return sorted(ticks)


def _project_polygon(
    polygon: Polygon,
    selection: _RadialStripSelection,
) -> list[tuple[float, float]]:
    projected: list[tuple[float, float]] = []
    for x, y in polygon.exterior.coords:
        offset_x = float(x) - selection.origin_um[0]
        offset_y = float(y) - selection.origin_um[1]
        projected.append(
            (
                offset_x * selection.direction[0]
                + offset_y * selection.direction[1],
                offset_x * selection.transverse[0]
                + offset_y * selection.transverse[1],
            )
        )
    return projected


def _draw_radial_strip(
    axis: Any,
    corrected: LayoutPlan,
    nominal_by_id: Mapping[str, LayoutFeature],
    *,
    selection: _RadialStripSelection | None = None,
    references: Sequence[_RadialReference] | None = None,
) -> None:
    selection = _select_radial_strip(corrected) if selection is None else selection
    axis.set_title(_RADIAL_STRIP_TITLE, loc="left", fontsize=9)
    axis.set_xlabel("Parent shell along radial strip (center → edge)", fontsize=8)
    axis.set_ylabel("transverse (µm)", fontsize=8)
    axis.tick_params(labelsize=7, direction="out", length=3, width=0.8)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    if selection is None:
        axis.text(
            0.5,
            0.5,
            "Radial parent-cell path unavailable",
            ha="center",
            va="center",
            color="#666666",
            fontsize=8,
            transform=axis.transAxes,
        )
        return

    resolved_references = (
        _radial_references(selection) if references is None else tuple(references)
    )
    nominal_patches: list[PolygonPatch] = []
    corrected_patches: list[PolygonPatch] = []
    shell_positions: dict[int, float] = {}
    for shell, features, center in selection.groups:
        offset_x = center[0] - selection.origin_um[0]
        offset_y = center[1] - selection.origin_um[1]
        shell_positions[shell] = (
            offset_x * selection.direction[0]
            + offset_y * selection.direction[1]
        )
        for feature in features:
            nominal_polygon = _matching_nominal_polygon(nominal_by_id, feature)
            nominal_patches.append(
                PolygonPatch(
                    _project_polygon(nominal_polygon, selection),
                    closed=True,
                )
            )
            corrected_patches.append(
                PolygonPatch(
                    _project_polygon(feature.polygon, selection),
                    closed=True,
                )
            )

    axis.add_collection(
        PatchCollection(
            nominal_patches,
            facecolor="#d9d9d9",
            edgecolor="#5f6368",
            linewidth=0.55,
            rasterized=True,
        )
    )
    axis.add_collection(
        PatchCollection(
            corrected_patches,
            facecolor="#2b83ba",
            edgecolor="#174a69",
            linewidth=0.55,
            alpha=0.62,
            rasterized=True,
        )
    )

    max_shell = selection.shells[-1]
    axis.set_xlim(
        -0.5 * selection.period_um,
        shell_positions[max_shell] + 0.5 * selection.period_um,
    )
    axis.set_ylim(-selection.half_width_um, selection.half_width_um)
    axis.set_aspect("equal", adjustable="box")
    tick_shells = _reference_tick_shells(selection)
    axis.set_xticks([shell_positions[shell] for shell in tick_shells])
    axis.set_xticklabels([str(shell) for shell in tick_shells])

    if selection.cavity_layers is not None:
        cavity_shell = selection.cavity_layers
        boundary_x = 0.5 * (
            shell_positions[cavity_shell] + shell_positions[cavity_shell + 1]
        )
        axis.axvline(boundary_x, color="#6b6b6b", linewidth=0.7)

    if resolved_references:
        marker_y = selection.half_width_um * 0.62
        axis.scatter(
            [shell_positions[reference.shell] for reference in resolved_references],
            [marker_y] * len(resolved_references),
            c=[reference.color for reference in resolved_references],
            marker="v",
            s=22,
            linewidths=0.0,
            zorder=5,
        )
        label_y = selection.half_width_um * 0.92
        for reference in resolved_references:
            if reference.shell == 0:
                horizontal_alignment = "left"
            elif reference.shell == max_shell:
                horizontal_alignment = "right"
            else:
                horizontal_alignment = "center"
            axis.text(
                shell_positions[reference.shell],
                label_y,
                reference.plot_label,
                ha=horizontal_alignment,
                va="top",
                fontsize=6.5,
                color=reference.color,
            )


def _draw_comparison(
    axis: Any,
    reference: _RadialReference | None,
    nominal_by_id: Mapping[str, LayoutFeature],
    *,
    title: str,
    shared_bounds: tuple[float, float, float, float] | None,
) -> None:
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlabel("local x (µm)", fontsize=7)
    axis.set_ylabel("local y (µm)", fontsize=7)
    axis.tick_params(labelsize=6.5, direction="out", length=2.5, width=0.7)
    axis.set_title(title, loc="left", fontsize=8.5)

    if reference is None:
        axis.text(
            0.5,
            0.5,
            "Representative triangle unavailable",
            ha="center",
            va="center",
            color="#666666",
            fontsize=7.5,
            transform=axis.transAxes,
        )
        return

    nominal_polygon = _matching_nominal_polygon(
        nominal_by_id, reference.feature
    )
    corrected_polygon = reference.feature.polygon
    nominal_coordinates = _local_polygon_coordinates(
        nominal_polygon, reference.cell_center_um
    )
    corrected_coordinates = _local_polygon_coordinates(
        corrected_polygon, reference.cell_center_um
    )
    axis.fill(
        [point[0] for point in nominal_coordinates],
        [point[1] for point in nominal_coordinates],
        facecolor="#d9d9d9",
        edgecolor="#5f6368",
        linewidth=0.9,
    )
    axis.fill(
        [point[0] for point in corrected_coordinates],
        [point[1] for point in corrected_coordinates],
        facecolor="#2b83ba",
        edgecolor="#174a69",
        linewidth=0.9,
        alpha=0.60,
    )
    if shared_bounds is not None:
        axis.set_xlim(shared_bounds[0], shared_bounds[2])
        axis.set_ylim(shared_bounds[1], shared_bounds[3])
    axis.text(
        0.02,
        0.02,
        reference.feature.feature_id,
        ha="left",
        va="bottom",
        fontsize=6.0,
        color="#404040",
        transform=axis.transAxes,
    )


def _comparison_title(
    title: str,
    reference: _RadialReference | None,
) -> str:
    if reference is None:
        return title
    return f"{title} (shell {reference.shell})"


def _draw_correction_function(
    axis: Any,
    selection: _RadialStripSelection | None,
    references: Sequence[_RadialReference],
    preview_context: Mapping[str, Any],
) -> None:
    axis.set_title(_CORRECTION_FUNCTION_TITLE, loc="left", fontsize=10)
    axis.set_xlabel("Parent shell (center → edge)", fontsize=8)
    axis.set_ylabel("Triangle side-length correction (nm)", fontsize=8)
    axis.tick_params(labelsize=7, direction="out", length=3, width=0.8)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    envelope_config = preview_context.get("spatial_envelope")
    if selection is None or not isinstance(envelope_config, Mapping):
        axis.text(
            0.5,
            0.5,
            "Spatial correction function unavailable",
            ha="center",
            va="center",
            color="#666666",
            fontsize=8,
            transform=axis.transAxes,
        )
        return

    try:
        envelope = spatial_envelope_from_mapping(envelope_config)
        triangle_side = triangle_side_correction_from_mapping(
            preview_context.get('triangle_side_correction')
        )
    except (TypeError, ValueError):
        axis.text(
            0.5,
            0.5,
            "Invalid spatial correction function",
            ha="center",
            va="center",
            color="#666666",
            fontsize=8,
            transform=axis.transAxes,
        )
        return
    if envelope.target != "edge_offset_um":
        axis.text(
            0.5,
            0.5,
            f"Unsupported correction target: {envelope.target}",
            ha="center",
            va="center",
            color="#666666",
            fontsize=8,
            transform=axis.transAxes,
        )
        return

    max_shell = selection.shells[-1]
    shell_values = [
        max_shell * index / (_CORRECTION_SAMPLE_COUNT - 1)
        for index in range(_CORRECTION_SAMPLE_COUNT)
    ]

    def triangle_side_change_nm(shell: float) -> float:
        distance = selection.period_um * shell
        position = (
            selection.origin_um[0] + selection.direction[0] * distance,
            selection.origin_um[1] + selection.direction[1] * distance,
        )
        if selection.cavity_layers is None or shell <= selection.cavity_layers:
            region = "cavity"
        else:
            region = "cladding"
        raw_envelope_edge_offset_um = envelope.evaluate(position).value
        if triangle_side.applies_to(region):
            return (
                triangle_side.global_delta_nm
                + 1000.0
                * SIDE_TO_EDGE_OFFSET
                * triangle_side.envelope_modulation_strength
                * raw_envelope_edge_offset_um
            )
        return 1000.0 * SIDE_TO_EDGE_OFFSET * raw_envelope_edge_offset_um

    correction_values = [triangle_side_change_nm(shell) for shell in shell_values]
    axis.plot(
        shell_values,
        correction_values,
        color="#255f85",
        linewidth=1.6,
    )
    axis.axhline(0.0, color="#b0b0b0", linewidth=0.7)
    axis.set_xlim(0.0, float(max_shell))
    tick_shells = _reference_tick_shells(selection)
    axis.set_xticks(tick_shells)
    axis.set_xticklabels([str(shell) for shell in tick_shells])

    all_values = [0.0, *correction_values]
    value_min = min(all_values)
    value_max = max(all_values)
    value_span = value_max - value_min
    padding = 0.10 * value_span if value_span > 1e-12 else max(abs(value_max) * 0.1, 0.1)
    axis.set_ylim(value_min - padding, value_max + padding)

    if references:
        marker_values = [
            triangle_side_change_nm(reference.shell) for reference in references
        ]
        axis.scatter(
            [reference.shell for reference in references],
            marker_values,
            c=[reference.color for reference in references],
            s=30,
            edgecolors="white",
            linewidths=0.6,
            zorder=5,
        )
        for reference, marker_value in zip(references, marker_values):
            horizontal_alignment = (
                "left"
                if reference.shell == 0
                else "right" if reference.shell == max_shell else "center"
            )
            horizontal_offset = 4 if reference.shell == 0 else -4 if reference.shell == max_shell else 0
            axis.annotate(
                reference.plot_label,
                (reference.shell, marker_value),
                xytext=(horizontal_offset, 7),
                textcoords="offset points",
                ha=horizontal_alignment,
                va="bottom",
                fontsize=6.5,
                color=reference.color,
            )
    axis.text(
        0.02,
        0.02,
        str(envelope.kind),
        ha="left",
        va="bottom",
        fontsize=7,
        color="#505050",
        transform=axis.transAxes,
    )


def save_preview(
    nominal: LayoutPlan,
    corrected: LayoutPlan,
    summary: Mapping[str, Any],
    path: str | Path,
    *,
    dpi: int = 220,
) -> Path:
    """Save one compact PNG containing geometry and fabrication QA context.

    Panel order is fixed: the full corrected layout; center, cavity-boundary,
    and cladding-boundary nominal/corrected triangle comparisons; the applied
    radial correction function; then the matching one-cell-wide radial strip.
    """

    if not isinstance(nominal, LayoutPlan) or not isinstance(corrected, LayoutPlan):
        raise TypeError("nominal and corrected must be LayoutPlan objects")
    if not isinstance(summary, Mapping):
        raise TypeError("summary must be a mapping")
    if not isinstance(dpi, int) or isinstance(dpi, bool) or dpi <= 0:
        raise ValueError("dpi must be a positive integer")

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure = Figure(
        figsize=_PREVIEW_FIGURE_SIZE,
        dpi=dpi,
        constrained_layout=True,
    )
    layout_engine = figure.get_layout_engine()
    if layout_engine is None:  # pragma: no cover - constrained layout is explicit
        raise RuntimeError("preview constrained-layout engine is unavailable")
    layout_engine.set(**_PREVIEW_CONSTRAINED_PADS)
    FigureCanvasAgg(figure)
    grid = figure.add_gridspec(
        3,
        3,
        width_ratios=_PREVIEW_WIDTH_RATIOS,
        height_ratios=_PREVIEW_HEIGHT_RATIOS,
    )
    global_axis = figure.add_subplot(grid[0:2, 0])
    comparison_grid = grid[0:2, 1].subgridspec(
        3,
        1,
        hspace=_COMPARISON_HSPACE,
    )
    comparison_axes = [
        figure.add_subplot(comparison_grid[index, 0]) for index in range(3)
    ]
    correction_axis = figure.add_subplot(grid[0:2, 2])
    radial_axis = figure.add_subplot(grid[2, :])

    _draw_global(global_axis, corrected)
    nominal_by_id = {feature.feature_id: feature for feature in nominal.features}
    selection = _select_radial_strip(corrected)
    references = _radial_references(selection)
    references_by_key = {reference.key: reference for reference in references}
    shared_bounds = _comparison_local_bounds(references, nominal_by_id)
    for axis, (key, title, _plot_label, _color) in zip(
        comparison_axes, _POSITION_STYLES
    ):
        reference = references_by_key.get(key)
        _draw_comparison(
            axis,
            reference,
            nominal_by_id,
            title=_comparison_title(title, reference),
            shared_bounds=shared_bounds,
        )

    _draw_correction_function(
        correction_axis,
        selection,
        references,
        summary,
    )
    _draw_radial_strip(
        radial_axis,
        corrected,
        nominal_by_id,
        selection=selection,
        references=references,
    )

    figure.savefig(output_path, dpi=dpi, format="png", facecolor="white")
    figure.clear()
    return output_path


__all__ = ["save_preview"]
