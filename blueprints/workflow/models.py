"""Geometry-neutral layout models used by the blueprint pipeline.

The models in this module deliberately know nothing about COMSOL, a lattice
type, or a particular hole parameterization.  Geometry sources hand Shapely
polygons (or plain ``Nx2`` coordinate sequences) to :class:`LayoutFeature`;
correction, DRC, preview, and writer stages consume the same model.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from typing import Any, Iterable, Mapping, Sequence

from shapely.geometry import Polygon


Coordinate = tuple[float, float]
CoordinateSequence = Sequence[Sequence[float]]


def _coerce_polygon(value: Polygon | CoordinateSequence, *, field_name: str) -> Polygon:
    """Return *value* as a polygon without repairing invalid geometry.

    Invalid and degenerate polygons must remain observable by DRC, so this
    helper intentionally does not call ``buffer(0)`` or otherwise alter input
    topology.
    """

    if isinstance(value, Polygon):
        return value
    try:
        return Polygon(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field_name} must be a Polygon or an Nx2 coordinate sequence") from exc


def _coerce_shift(value: Sequence[float]) -> Coordinate:
    try:
        x, y = value
    except (TypeError, ValueError) as exc:
        raise TypeError("shift_um must contain exactly two coordinates") from exc
    x_value = float(x)
    y_value = float(y)
    if not (math.isfinite(x_value) and math.isfinite(y_value)):
        raise ValueError("shift_um coordinates must be finite")
    return (x_value, y_value)


@dataclass(slots=True)
class LayoutFeature:
    """One closed fabrication feature and its stable design identity.

    ``nominal_polygon`` records the uncorrected design shape while ``polygon``
    is the shape consumed by the next pipeline stage.  Geometry builders
    normally initialize both from the same coordinates.  Corrections return a
    new feature and never mutate either input polygon.
    """

    feature_id: str
    region: str
    parent_i: int
    parent_j: int
    group_id: int
    local_index: int
    layer: int
    nominal_polygon: Polygon | CoordinateSequence
    polygon: Polygon | CoordinateSequence
    shift_um: Coordinate
    dxf_layer: str = "ETCH"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.feature_id, str) or not self.feature_id.strip():
            raise ValueError("feature_id must be a non-empty string")
        if not isinstance(self.region, str) or not self.region.strip():
            raise ValueError("region must be a non-empty string")
        if not isinstance(self.dxf_layer, str) or not self.dxf_layer.strip():
            raise ValueError("dxf_layer must be a non-empty string")
        self.parent_i = int(self.parent_i)
        self.parent_j = int(self.parent_j)
        self.group_id = int(self.group_id)
        self.local_index = int(self.local_index)
        self.layer = int(self.layer)
        self.nominal_polygon = _coerce_polygon(
            self.nominal_polygon, field_name="nominal_polygon"
        )
        self.polygon = _coerce_polygon(self.polygon, field_name="polygon")
        self.shift_um = _coerce_shift(self.shift_um)
        self.metadata = dict(self.metadata)

    @property
    def nominal_centroid_um(self) -> Coordinate:
        centroid = self.nominal_polygon.centroid
        return (float(centroid.x), float(centroid.y))

    @property
    def centroid_um(self) -> Coordinate:
        centroid = self.polygon.centroid
        return (float(centroid.x), float(centroid.y))

    def with_geometry(
        self,
        polygon: Polygon | CoordinateSequence,
        *,
        nominal_polygon: Polygon | CoordinateSequence | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "LayoutFeature":
        """Return a copy with updated geometry and optionally metadata."""

        return replace(
            self,
            polygon=polygon,
            nominal_polygon=(
                self.nominal_polygon if nominal_polygon is None else nominal_polygon
            ),
            metadata=self.metadata if metadata is None else dict(metadata),
        )


@dataclass(slots=True)
class LayoutPlan:
    """A complete 2-D layout in one coordinate and length-unit contract."""

    geometry_kind: str
    features: list[LayoutFeature] | tuple[LayoutFeature, ...]
    boundary: Polygon | CoordinateSequence | None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.geometry_kind, str) or not self.geometry_kind.strip():
            raise ValueError("geometry_kind must be a non-empty string")
        self.features = list(self.features)
        if not all(isinstance(item, LayoutFeature) for item in self.features):
            raise TypeError("features must contain only LayoutFeature objects")
        if self.boundary is not None:
            self.boundary = _coerce_polygon(self.boundary, field_name="boundary")
        self.metadata = dict(self.metadata)

    @property
    def feature_count(self) -> int:
        return len(self.features)

    @property
    def bounds(self) -> tuple[float, float, float, float] | None:
        if not self.features:
            return None
        min_x = min(feature.polygon.bounds[0] for feature in self.features)
        min_y = min(feature.polygon.bounds[1] for feature in self.features)
        max_x = max(feature.polygon.bounds[2] for feature in self.features)
        max_y = max(feature.polygon.bounds[3] for feature in self.features)
        return (float(min_x), float(min_y), float(max_x), float(max_y))

    def with_features(
        self,
        features: Iterable[LayoutFeature],
        *,
        boundary: Polygon | CoordinateSequence | None = None,
        metadata: Mapping[str, Any] | None = None,
        preserve_boundary: bool = True,
    ) -> "LayoutPlan":
        """Return a copy after a pure pipeline transformation."""

        next_boundary = self.boundary if preserve_boundary and boundary is None else boundary
        return LayoutPlan(
            geometry_kind=self.geometry_kind,
            features=list(features),
            boundary=next_boundary,
            metadata=self.metadata if metadata is None else dict(metadata),
        )


# ``NominalLayout`` is a semantic alias useful to geometry source protocols.
# It remains the same neutral runtime type, so the standalone writer and DRC
# never need source-specific adapters.
NominalLayout = LayoutPlan


__all__ = [
    "Coordinate",
    "CoordinateSequence",
    "LayoutFeature",
    "LayoutPlan",
    "NominalLayout",
]
