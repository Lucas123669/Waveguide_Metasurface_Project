"""Standalone nominal geometry for the active finite hexagonal lattice."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from numbers import Integral

import numpy as np

from ..models import LayoutFeature, LayoutPlan

from ._validation import (
    require_exact_keys,
    require_integer,
    require_mapping,
    require_number,
    require_vector2,
)
from .six_triangle_cell import (
    SIX_TRIANGLE_CELL_KIND,
    CompactCellParameters,
    SixTriangleCell,
    build_six_triangle_cell,
    unit_cell_boundary,
)


HEX_LATTICE_KIND = "triangular_hexagonal_v1"
HEX_FINITE_KIND = "hex_shells_v1"
GROUPS_SHIFT_KIND = "groups"
ELLIPSE_SHIFT_KIND = "ellipse"
UNIFORM_PROFILE_KIND = "uniform"
TANH_POWER_PROFILE_KIND = "tanh_power"

_X_SHIFT_SIDE_INDICES = (0, 2, 3, 5)
_X_SHIFT_CORNER_INDICES = (0, 3)
_Y_SHIFT_SIDE_INDICES = (1, 4)
_Y_SHIFT_CORNER_INDICES = (1, 2, 4, 5)


@dataclass(frozen=True)
class LatticePoint:
    i: int
    j: int
    shell: int
    x: float
    y: float


@dataclass(frozen=True)
class ShiftProfile:
    kind: str
    scale_layers: float | None = None
    power: float | None = None

    @classmethod
    def from_mapping(cls, value: object, path: str) -> "ShiftProfile":
        mapping = require_mapping(value, path)
        kind = mapping.get("kind")
        if not isinstance(kind, str):
            raise TypeError(f"{path}.kind must be a string")
        if kind == UNIFORM_PROFILE_KIND:
            require_exact_keys(mapping, path, {"kind"})
            return cls(kind=kind)
        if kind == TANH_POWER_PROFILE_KIND:
            require_exact_keys(mapping, path, {"kind", "scale_layers", "power"})
            scale_layers = require_number(
                mapping["scale_layers"],
                f"{path}.scale_layers",
                positive=True,
            )
            power = require_number(mapping["power"], f"{path}.power")
            if power <= 1.0:
                raise ValueError(f"{path}.power must be greater than 1")
            return cls(kind=kind, scale_layers=scale_layers, power=power)
        raise ValueError(
            f"{path}.kind must be '{UNIFORM_PROFILE_KIND}' or "
            f"'{TANH_POWER_PROFILE_KIND}'"
        )

    def envelope(self, layer: int) -> float:
        if not isinstance(layer, Integral):
            raise TypeError("cladding shift layer must be an integer")
        normalized_layer = int(layer)
        if normalized_layer < 0:
            raise ValueError("cladding shift layer must be non-negative")
        if normalized_layer == 0:
            return 0.0
        if self.kind == UNIFORM_PROFILE_KIND:
            return 1.0
        return math.tanh(
            (normalized_layer / float(self.scale_layers)) ** float(self.power)
        )

    def to_dict(self) -> dict[str, float | str]:
        if self.kind == UNIFORM_PROFILE_KIND:
            return {"kind": self.kind}
        return {
            "kind": self.kind,
            "scale_layers": float(self.scale_layers),
            "power": float(self.power),
        }


@dataclass(frozen=True)
class HexLayoutSpec:
    period_um: float
    origin_um: tuple[float, float]
    orientation_deg: float
    radial_reference_fraction: float
    edge_reference_nm: float
    cavity_cell: CompactCellParameters
    cladding_cell: CompactCellParameters
    cavity_layers: int
    cladding_layers: int
    empty_buffer_periods: float
    shift_kind: str
    shift_profile: ShiftProfile
    x_factor: float
    y_factor: float

    @classmethod
    def from_mapping(cls, value: object) -> "HexLayoutSpec":
        geometry = require_mapping(value, "geometry")
        require_exact_keys(
            geometry,
            "geometry",
            {
                "schema_version",
                "length_unit",
                "lattice",
                "unit_cell",
                "finite",
                "cladding_shift",
            },
        )
        schema_version = require_integer(
            geometry["schema_version"], "geometry.schema_version"
        )
        if schema_version != 1:
            raise ValueError("geometry.schema_version must be 1")
        if geometry["length_unit"] != "um":
            raise ValueError("geometry.length_unit must be 'um'")

        lattice = require_mapping(geometry["lattice"], "geometry.lattice")
        require_exact_keys(
            lattice,
            "geometry.lattice",
            {"kind", "period_um", "origin_um", "orientation_deg"},
        )
        if lattice["kind"] != HEX_LATTICE_KIND:
            raise ValueError(f"geometry.lattice.kind must be '{HEX_LATTICE_KIND}'")

        unit_cell = require_mapping(geometry["unit_cell"], "geometry.unit_cell")
        require_exact_keys(
            unit_cell,
            "geometry.unit_cell",
            {
                "kind",
                "radial_reference_fraction",
                "edge_reference_nm",
                "cavity",
                "cladding",
            },
        )
        if unit_cell["kind"] != SIX_TRIANGLE_CELL_KIND:
            raise ValueError(
                f"geometry.unit_cell.kind must be '{SIX_TRIANGLE_CELL_KIND}'"
            )

        finite = require_mapping(geometry["finite"], "geometry.finite")
        require_exact_keys(
            finite,
            "geometry.finite",
            {
                "kind",
                "cavity_layers",
                "cladding_layers",
                "empty_buffer_periods",
            },
        )
        if finite["kind"] != HEX_FINITE_KIND:
            raise ValueError(f"geometry.finite.kind must be '{HEX_FINITE_KIND}'")

        cladding_shift = require_mapping(
            geometry["cladding_shift"], "geometry.cladding_shift"
        )
        require_exact_keys(
            cladding_shift,
            "geometry.cladding_shift",
            {"geometry", "profile", "x_factor", "y_factor"},
        )
        shift_geometry = require_mapping(
            cladding_shift["geometry"],
            "geometry.cladding_shift.geometry",
        )
        require_exact_keys(
            shift_geometry,
            "geometry.cladding_shift.geometry",
            {"kind"},
        )
        shift_kind = shift_geometry["kind"]
        if shift_kind not in {GROUPS_SHIFT_KIND, ELLIPSE_SHIFT_KIND}:
            raise ValueError(
                "geometry.cladding_shift.geometry.kind must be "
                f"'{GROUPS_SHIFT_KIND}' or '{ELLIPSE_SHIFT_KIND}'"
            )

        return cls(
            period_um=require_number(
                lattice["period_um"], "geometry.lattice.period_um", positive=True
            ),
            origin_um=require_vector2(
                lattice["origin_um"], "geometry.lattice.origin_um"
            ),
            orientation_deg=require_number(
                lattice["orientation_deg"], "geometry.lattice.orientation_deg"
            ),
            radial_reference_fraction=require_number(
                unit_cell["radial_reference_fraction"],
                "geometry.unit_cell.radial_reference_fraction",
                positive=True,
            ),
            edge_reference_nm=require_number(
                unit_cell["edge_reference_nm"],
                "geometry.unit_cell.edge_reference_nm",
                positive=True,
            ),
            cavity_cell=CompactCellParameters.from_mapping(
                unit_cell["cavity"], "geometry.unit_cell.cavity"
            ),
            cladding_cell=CompactCellParameters.from_mapping(
                unit_cell["cladding"], "geometry.unit_cell.cladding"
            ),
            cavity_layers=require_integer(
                finite["cavity_layers"],
                "geometry.finite.cavity_layers",
                positive=True,
            ),
            cladding_layers=require_integer(
                finite["cladding_layers"],
                "geometry.finite.cladding_layers",
                positive=True,
            ),
            empty_buffer_periods=require_number(
                finite["empty_buffer_periods"],
                "geometry.finite.empty_buffer_periods",
                non_negative=True,
            ),
            shift_kind=str(shift_kind),
            shift_profile=ShiftProfile.from_mapping(
                cladding_shift["profile"], "geometry.cladding_shift.profile"
            ),
            x_factor=require_number(
                cladding_shift["x_factor"],
                "geometry.cladding_shift.x_factor",
                non_negative=True,
            ),
            y_factor=require_number(
                cladding_shift["y_factor"],
                "geometry.cladding_shift.y_factor",
                non_negative=True,
            ),
        )


def index_shell(i: int, j: int) -> int:
    return max(abs(i), abs(j), abs(i + j))


def lattice_points(
    max_shell: int,
    period_um: float,
    min_shell: int = 0,
) -> tuple[LatticePoint, ...]:
    if type(max_shell) is not int or max_shell < 0:
        raise ValueError("max_shell must be a non-negative integer")
    if type(min_shell) is not int or min_shell < 0 or min_shell > max_shell:
        raise ValueError("min_shell must be an integer between zero and max_shell")
    period = require_number(period_um, "period_um", positive=True)
    points: list[LatticePoint] = []
    for i in range(-max_shell, max_shell + 1):
        for j in range(-max_shell, max_shell + 1):
            shell = index_shell(i, j)
            if not min_shell <= shell <= max_shell:
                continue
            points.append(
                LatticePoint(
                    i=i,
                    j=j,
                    shell=shell,
                    x=period * (i + 0.5 * j),
                    y=period * math.sqrt(3.0) * j / 2.0,
                )
            )
    return tuple(points)


def _cladding_shift_group(kind: str, index: int) -> str:
    if kind == "side":
        return "y" if index in _Y_SHIFT_SIDE_INDICES else "x"
    if kind == "corner":
        return "y" if index in _Y_SHIFT_CORNER_INDICES else "x"
    raise ValueError(f"unknown normal-fan feature kind: {kind}")


def _ideal_bulk_hex_vertices(radius: int, period_um: float) -> np.ndarray:
    indices = np.array(
        [
            [radius, 0],
            [0, radius],
            [-radius, radius],
            [-radius, 0],
            [0, -radius],
            [radius, -radius],
        ],
        dtype=float,
    )
    return np.column_stack(
        [
            period_um * (indices[:, 0] + 0.5 * indices[:, 1]),
            period_um * math.sqrt(3.0) * indices[:, 1] / 2.0,
        ]
    )


def _normal_fan_feature(
    point: LatticePoint,
    radius: int,
    period_um: float,
) -> tuple[str, int]:
    position = np.array([point.x, point.y], dtype=float)
    vertices = _ideal_bulk_hex_vertices(radius, period_um)
    best_distance = math.inf
    best_kind = "side"
    best_index = 0
    for index, start in enumerate(vertices):
        end = vertices[(index + 1) % len(vertices)]
        edge = end - start
        fraction = float(np.dot(position - start, edge) / np.dot(edge, edge))
        clipped_fraction = float(np.clip(fraction, 0.0, 1.0))
        distance = float(
            np.sum((position - (start + clipped_fraction * edge)) ** 2)
        )
        if distance < best_distance:
            best_distance = distance
            if 1e-10 < clipped_fraction < 1.0 - 1e-10:
                best_kind, best_index = "side", index
            else:
                best_kind = "corner"
                best_index = (
                    index if clipped_fraction <= 1e-10 else (index + 1) % 6
                )
    return best_kind, best_index


def _normal_fan_direction(
    kind: str,
    index: int,
    radius: int,
    period_um: float,
) -> np.ndarray:
    vertices = _ideal_bulk_hex_vertices(radius, period_um)

    def side_normal(side_index: int) -> np.ndarray:
        edge = vertices[(side_index + 1) % 6] - vertices[side_index]
        normal = np.array([-edge[1], edge[0]], dtype=float)
        return normal / np.linalg.norm(normal)

    if kind == "side":
        return side_normal(index)
    direction = side_normal((index - 1) % 6) + side_normal(index)
    return direction / np.linalg.norm(direction)


def _ellipse_inward_shift(
    point: LatticePoint,
    period_um: float,
    x_factor: float,
    y_factor: float,
    envelope: float,
) -> np.ndarray:
    radius = math.hypot(point.x, point.y)
    if radius == 0.0 or envelope == 0.0:
        return np.zeros(2, dtype=float)
    weight = (
        x_factor * point.x * point.x + y_factor * point.y * point.y
    ) / (radius * radius)
    magnitude = period_um * envelope * weight
    return -magnitude * np.array([point.x, point.y], dtype=float) / radius


def _cladding_shift(
    point: LatticePoint,
    spec: HexLayoutSpec,
) -> tuple[int, float, np.ndarray]:
    layer = point.shell - spec.cavity_layers
    envelope = spec.shift_profile.envelope(layer)
    if spec.shift_kind == ELLIPSE_SHIFT_KIND:
        return (
            layer,
            envelope,
            _ellipse_inward_shift(
                point,
                spec.period_um,
                spec.x_factor,
                spec.y_factor,
                envelope,
            ),
        )
    kind, index = _normal_fan_feature(
        point, spec.cavity_layers, spec.period_um
    )
    factor = (
        spec.x_factor
        if _cladding_shift_group(kind, index) == "x"
        else spec.y_factor
    )
    magnitude = envelope * factor * spec.period_um
    if kind == "corner":
        magnitude *= 2.0 / math.sqrt(3.0)
    return (
        layer,
        envelope,
        magnitude
        * _normal_fan_direction(
            kind, index, spec.cavity_layers, spec.period_um
        ),
    )


def _rotation_matrix(angle_deg: float) -> np.ndarray:
    angle = math.radians(angle_deg)
    return np.array(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]],
        dtype=float,
    )


def _transform_points(
    points: np.ndarray,
    rotation: np.ndarray,
    origin: np.ndarray,
) -> np.ndarray:
    return np.asarray(points, dtype=float) @ rotation.T + origin


def _hex_boundary_size(
    points: Sequence[LatticePoint],
    period_um: float,
    padding_um: float,
) -> float:
    corners = unit_cell_boundary(period_um)
    vertices = np.vstack(
        [corners + np.array([point.x, point.y], dtype=float) for point in points]
    )
    root3 = math.sqrt(3.0)
    x_coordinates = vertices[:, 0]
    y_coordinates = vertices[:, 1]
    minimum = max(
        float(4.0 * np.max(np.abs(y_coordinates)) / root3),
        float(
            2.0
            * np.max(np.abs(root3 * x_coordinates + y_coordinates))
            / root3
        ),
        float(
            2.0
            * np.max(np.abs(root3 * x_coordinates - y_coordinates))
            / root3
        ),
    )
    return minimum + 2.0 * padding_um


def _footprint_boundary(size_um: float) -> np.ndarray:
    root3 = math.sqrt(3.0)
    return np.array(
        [
            [size_um / 2.0, 0.0],
            [size_um / 4.0, root3 * size_um / 4.0],
            [-size_um / 4.0, root3 * size_um / 4.0],
            [-size_um / 2.0, 0.0],
            [-size_um / 4.0, -root3 * size_um / 4.0],
            [size_um / 4.0, -root3 * size_um / 4.0],
        ],
        dtype=float,
    )


def _cell_metadata(cell: SixTriangleCell) -> dict[str, object]:
    return {
        **cell.metadata,
        "hole_parameters": cell.hole_parameters.tolist(),
    }


def build_hex_layout(geometry: Mapping[str, object]) -> LayoutPlan:
    """Build a full, tagged nominal hex layout from one explicit mapping."""
    spec = HexLayoutSpec.from_mapping(geometry)
    cavity_cell = build_six_triangle_cell(
        period_um=spec.period_um,
        radial_reference_fraction=spec.radial_reference_fraction,
        edge_reference_nm=spec.edge_reference_nm,
        parameters=spec.cavity_cell,
        parameter_path="geometry.unit_cell.cavity",
    )
    cladding_cell = build_six_triangle_cell(
        period_um=spec.period_um,
        radial_reference_fraction=spec.radial_reference_fraction,
        edge_reference_nm=spec.edge_reference_nm,
        parameters=spec.cladding_cell,
        parameter_path="geometry.unit_cell.cladding",
    )
    cavity_points = lattice_points(spec.cavity_layers, spec.period_um)
    cladding_points = lattice_points(
        spec.cavity_layers + spec.cladding_layers,
        spec.period_um,
        spec.cavity_layers + 1,
    )
    rotation = _rotation_matrix(spec.orientation_deg)
    origin = np.asarray(spec.origin_um, dtype=float)

    features: list[LayoutFeature] = []
    nominal_vertices: list[np.ndarray] = []
    for region, points, cell in (
        ("cavity", cavity_points, cavity_cell),
        ("cladding", cladding_points, cladding_cell),
    ):
        for point in points:
            if region == "cavity":
                layer = 0
                envelope = 0.0
                canonical_shift = np.zeros(2, dtype=float)
            else:
                layer, envelope, canonical_shift = _cladding_shift(point, spec)
            canonical_parent = np.array([point.x, point.y], dtype=float)
            canonical_center = canonical_parent + canonical_shift
            parent_center = _transform_points(
                canonical_parent[None, :], rotation, origin
            )[0]
            shift = canonical_shift @ rotation.T
            for local_index, template in enumerate(cell.polygons):
                polygon = _transform_points(
                    template + canonical_center,
                    rotation,
                    origin,
                )
                nominal_vertices.append(polygon)
                features.append(
                    LayoutFeature(
                        feature_id=(
                            f"{region}/{point.i}/{point.j}/0/{local_index}"
                        ),
                        region=region,
                        parent_i=point.i,
                        parent_j=point.j,
                        group_id=0,
                        local_index=local_index,
                        layer=layer,
                        nominal_polygon=polygon,
                        polygon=np.array(polygon, copy=True),
                        shift_um=shift,
                        dxf_layer="ETCH",
                        metadata={
                            "parent_shell": point.shell,
                            "canonical_parent_center_um": canonical_parent.tolist(),
                            "parent_center_um": parent_center.tolist(),
                            "shift_envelope": envelope,
                            "shift_formula": (
                                "hex_radial_ellipse_v1"
                                if spec.shift_kind == ELLIPSE_SHIFT_KIND
                                else "hex_normal_fan_v1"
                            ),
                        },
                    )
                )

    all_points = (*cavity_points, *cladding_points)
    footprint_size = _hex_boundary_size(
        all_points,
        spec.period_um,
        spec.empty_buffer_periods * spec.period_um,
    )
    boundary = _transform_points(
        _footprint_boundary(footprint_size), rotation, origin
    )
    all_vertices = np.vstack(nominal_vertices)

    return LayoutPlan(
        geometry_kind=HEX_LATTICE_KIND,
        features=tuple(features),
        boundary=boundary,
        metadata={
            "schema_version": 1,
            "length_unit": "um",
            "lattice": {
                "kind": HEX_LATTICE_KIND,
                "period_um": spec.period_um,
                "origin_um": list(spec.origin_um),
                "orientation_deg": spec.orientation_deg,
            },
            "unit_cell": {
                "kind": SIX_TRIANGLE_CELL_KIND,
                "radial_reference_fraction": spec.radial_reference_fraction,
                "edge_reference_nm": spec.edge_reference_nm,
                "cavity": _cell_metadata(cavity_cell),
                "cladding": _cell_metadata(cladding_cell),
            },
            "finite": {
                "kind": HEX_FINITE_KIND,
                "cavity_layers": spec.cavity_layers,
                "cladding_layers": spec.cladding_layers,
                "empty_buffer_periods": spec.empty_buffer_periods,
                "footprint_size_um": footprint_size,
            },
            "cladding_shift": {
                "geometry": {"kind": spec.shift_kind},
                "profile": spec.shift_profile.to_dict(),
                "x_factor": spec.x_factor,
                "y_factor": spec.y_factor,
            },
            "counts": {
                "cavity_cells": len(cavity_points),
                "cladding_cells": len(cladding_points),
                "cavity_features": len(cavity_points) * len(cavity_cell.polygons),
                "cladding_features": len(cladding_points)
                * len(cladding_cell.polygons),
                "total_features": len(features),
            },
            "nominal_bbox_um": [
                float(np.min(all_vertices[:, 0])),
                float(np.min(all_vertices[:, 1])),
                float(np.max(all_vertices[:, 0])),
                float(np.max(all_vertices[:, 1])),
            ],
        },
    )


@dataclass(frozen=True)
class HexGeometrySource:
    """Concrete source object for callers that prefer the generic protocol."""

    kind: str = HEX_LATTICE_KIND

    def build(self, geometry: Mapping[str, object]) -> LayoutPlan:
        return build_hex_layout(geometry)
