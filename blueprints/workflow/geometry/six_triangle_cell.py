"""Standalone six-triangular-hole unit-cell parameterization.

The formulas in this module are migrated from the current COMSOL workflow's
``basis_utils.py`` and ``geometry_utils.py``.  They deliberately live here so
that the manufacturing-layout package has no runtime dependency on that
project.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math

import numpy as np

from ._validation import (
    require_exact_keys,
    require_mapping,
    require_number,
)


SIX_TRIANGLE_CELL_KIND = "six_triangular_holes_fourier_v1"
_HOLE_COUNT = 6


@dataclass(frozen=True)
class CompactCellParameters:
    """The three compact parameters used by the active photonic-crystal cell."""

    b0_nm: float
    eta: float
    zeta: float

    @classmethod
    def from_mapping(
        cls,
        value: object,
        path: str = "unit_cell.parameters",
    ) -> "CompactCellParameters":
        mapping = require_mapping(value, path)
        require_exact_keys(mapping, path, {"b0_nm", "eta", "zeta"})
        return cls(
            b0_nm=require_number(mapping["b0_nm"], f"{path}.b0_nm", positive=True),
            eta=require_number(mapping["eta"], f"{path}.eta", positive=True),
            zeta=require_number(mapping["zeta"], f"{path}.zeta"),
        )

    def to_dict(self) -> dict[str, float]:
        return {"b0_nm": self.b0_nm, "eta": self.eta, "zeta": self.zeta}


@dataclass(frozen=True)
class SixTriangleCell:
    """Resolved local polygons and the six ``(r, theta, b, phi)`` rows."""

    polygons: tuple[np.ndarray, ...]
    hole_parameters: np.ndarray
    boundary: np.ndarray
    metadata: dict[str, object]


def rotate_points(
    points: np.ndarray,
    angle_deg: float,
    origin: tuple[float, float] = (0.0, 0.0),
) -> np.ndarray:
    """Rotate an ``N x 2`` coordinate table counter-clockwise in degrees."""
    coordinates = np.asarray(points, dtype=float)
    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("points must have shape (N, 2)")
    angle = math.radians(require_number(angle_deg, "angle_deg"))
    anchor = np.asarray(origin, dtype=float)
    rotation = np.array(
        [[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]],
        dtype=float,
    )
    return (coordinates - anchor) @ rotation.T + anchor


def _fourier_basis_matrix(count: int) -> np.ndarray:
    matrix = np.zeros((count, count), dtype=float)
    matrix[:, 0] = 1.0 / math.sqrt(count)
    samples = np.arange(count, dtype=float)
    column = 1
    for frequency in range(1, (count - 1) // 2 + 1):
        angle = 2.0 * math.pi * frequency * samples / count
        matrix[:, column] = math.sqrt(2.0 / count) * np.cos(angle)
        matrix[:, column + 1] = math.sqrt(2.0 / count) * np.sin(angle)
        column += 2
    if count % 2 == 0:
        matrix[:, column] = ((-1.0) ** samples) / math.sqrt(count)
    return matrix


def _fourier_basis_min_nonzero_values(count: int) -> np.ndarray:
    values = np.zeros(count, dtype=float)
    values[0] = 1.0 / math.sqrt(count)
    index = 1
    for frequency in range(1, (count - 1) // 2 + 1):
        reduced_count = count // math.gcd(frequency, count)
        if reduced_count % 4 == 0:
            cosine_value = math.sin(2.0 * math.pi / reduced_count)
        elif reduced_count % 2 == 0:
            cosine_value = math.sin(math.pi / reduced_count)
        else:
            cosine_value = math.sin(math.pi / (2.0 * reduced_count))
        values[index] = cosine_value * math.sqrt(2.0 / count)
        index += 1

        if reduced_count % 2 == 0:
            sine_value = math.sin(2.0 * math.pi / reduced_count)
        else:
            sine_value = math.sin(math.pi / reduced_count)
        values[index] = sine_value * math.sqrt(2.0 / count)
        index += 1
    if count % 2 == 0:
        values[index] = 1.0 / math.sqrt(count)
    return values


def resolve_hole_parameters(
    *,
    period_um: float,
    radial_reference_fraction: float,
    edge_reference_nm: float,
    parameters: CompactCellParameters,
) -> np.ndarray:
    """Resolve compact cell inputs to six ``r/theta/b/phi`` rows.

    ``radial_reference_fraction`` and ``edge_reference_nm`` are explicit even
    though the latter algebraically cancels for the current ``b0_nm`` compact
    input.  Keeping both values in the schema preserves the exact versioned
    Fourier parameterization without a hidden ``R_0`` or ``B_0`` constant.
    """
    lattice_period = require_number(period_um, "period_um", positive=True)
    radial_fraction = require_number(
        radial_reference_fraction,
        "radial_reference_fraction",
        positive=True,
    )
    edge_reference = require_number(
        edge_reference_nm,
        "edge_reference_nm",
        positive=True,
    )
    if not isinstance(parameters, CompactCellParameters):
        raise TypeError("parameters must be CompactCellParameters")

    radial_reference_um = lattice_period * radial_fraction
    edge_reference_um = edge_reference / 1000.0
    edge_dc_scale = (parameters.b0_nm / edge_reference) ** 2

    radial_fourier = np.zeros(_HOLE_COUNT, dtype=float)
    theta_fourier = np.zeros(_HOLE_COUNT, dtype=float)
    edge_square_fourier = np.zeros(_HOLE_COUNT, dtype=float)
    phi_fourier = np.zeros(_HOLE_COUNT, dtype=float)
    radial_fourier[0] = radial_reference_um * parameters.eta
    edge_square_fourier[0] = edge_reference_um**2 * edge_dc_scale
    edge_square_fourier[3] = (
        edge_reference_um**2
        * edge_dc_scale
        * (parameters.zeta**2 - 1.0)
        / 2.0
    )

    normalizers = _fourier_basis_min_nonzero_values(_HOLE_COUNT)
    basis = _fourier_basis_matrix(_HOLE_COUNT)
    radius = basis @ (radial_fourier / normalizers)
    theta_deg = basis @ (theta_fourier / normalizers)
    edge_square = basis @ (edge_square_fourier / normalizers)
    phi_deg = basis @ (phi_fourier / normalizers)

    if not np.all(np.isfinite(edge_square)) or np.any(edge_square <= 0.0):
        raise ValueError(
            "compact cell parameters produce a zero or imaginary triangle edge"
        )
    edge_um = np.sqrt(edge_square)
    return np.column_stack([radius, theta_deg, edge_um, phi_deg])


def _inner_triangle(
    edge_um: float,
    center: tuple[float, float],
    rotation_deg: float,
) -> np.ndarray:
    height = edge_um * math.sqrt(3.0) / 2.0
    triangle = np.array(
        [
            [-2.0 * height / 3.0, 0.0],
            [height / 3.0, -edge_um / 2.0],
            [height / 3.0, edge_um / 2.0],
        ],
        dtype=float,
    )
    return rotate_points(triangle, rotation_deg) + np.asarray(center, dtype=float)


def unit_cell_boundary(period_um: float) -> np.ndarray:
    """Return the current regular hexagonal Wigner-Seitz cell boundary."""
    period = require_number(period_um, "period_um", positive=True)
    height = period / 2.0
    edge = period / math.sqrt(3.0)
    first_corner = np.array([[height, edge / 2.0]], dtype=float)
    return np.vstack(
        [rotate_points(first_corner, 60.0 * index)[0] for index in range(6)]
    )


def build_six_triangle_cell(
    *,
    period_um: float,
    radial_reference_fraction: float,
    edge_reference_nm: float,
    parameters: CompactCellParameters | Mapping[str, object],
    parameter_path: str = "unit_cell.parameters",
) -> SixTriangleCell:
    """Build the six local triangular-hole polygons for one cell."""
    compact = (
        parameters
        if isinstance(parameters, CompactCellParameters)
        else CompactCellParameters.from_mapping(parameters, parameter_path)
    )
    rows = resolve_hole_parameters(
        period_um=period_um,
        radial_reference_fraction=radial_reference_fraction,
        edge_reference_nm=edge_reference_nm,
        parameters=compact,
    )

    polygons: list[np.ndarray] = []
    for index, (radius, theta_deg, edge_um, phi_deg) in enumerate(rows):
        theta = math.radians(float(theta_deg))
        local = _inner_triangle(
            float(edge_um),
            (float(radius), float(radius) * math.tan(theta)),
            float(phi_deg),
        )
        polygons.append(rotate_points(local, 60.0 * index))

    return SixTriangleCell(
        polygons=tuple(polygons),
        hole_parameters=rows,
        boundary=unit_cell_boundary(period_um),
        metadata={
            "kind": SIX_TRIANGLE_CELL_KIND,
            "radial_reference_fraction": float(radial_reference_fraction),
            "edge_reference_nm": float(edge_reference_nm),
            "compact_parameters": compact.to_dict(),
        },
    )
