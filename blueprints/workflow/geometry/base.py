"""Geometry-source interface consumed by the rest of the blueprint pipeline."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from ..models import LayoutPlan


@runtime_checkable
class GeometrySource(Protocol):
    """Build a neutral polygon layout without knowing about DXF or COMSOL."""

    kind: str

    def build(self, geometry: Mapping[str, object]) -> LayoutPlan:
        """Resolve one self-contained geometry mapping into a nominal layout."""
