"""Manufacturing corrections for geometry-neutral blueprint layouts."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from typing import Any, Mapping, Protocol, Sequence

from shapely import affinity
from shapely.geometry import Polygon

from .dose import GeometryCorrectionContribution, resolve_dose_components
from .sem_calibration import SIDE_TO_EDGE_OFFSET
from ..models import Coordinate, LayoutFeature, LayoutPlan


class CorrectionError(ValueError):
    """Raised when a requested correction cannot produce a usable polygon."""


_JOIN_STYLE_CODES = {"round": 1, "mitre": 2, "miter": 2, "bevel": 3}
_KNOWN_OPERATORS = {
    "edge_offset",
    "edge_offset_um",
    "centroid_scale",
    "isotropic_scale",
    "anisotropic_scale_xy",
    "corner_strategy",
}


def _as_finite(value: Any, *, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise CorrectionError(f"{name} must be a finite number") from exc
    if not math.isfinite(result):
        raise CorrectionError(f"{name} must be a finite number")
    return result


def _pair(value: Sequence[float], *, name: str) -> Coordinate:
    try:
        x, y = value
    except (TypeError, ValueError) as exc:
        raise CorrectionError(f"{name} must contain exactly two values") from exc
    return (_as_finite(x, name=f"{name}[0]"), _as_finite(y, name=f"{name}[1]"))


def _exclusive_length_um(
    config: Mapping[str, Any],
    *,
    um_keys: Sequence[str],
    nm_keys: Sequence[str],
    default: float = 0.0,
) -> float:
    present = [key for key in (*um_keys, *nm_keys) if key in config]
    if len(present) > 1:
        raise CorrectionError(
            "conflicting length fields: " + ", ".join(sorted(present))
        )
    if not present:
        return default
    key = present[0]
    value = _as_finite(config[key], name=key)
    return value / 1000.0 if key in nm_keys else value


@dataclass(frozen=True, slots=True)
class FeatureCorrection:
    """Effective correction applied once in a feature-local frame."""

    edge_offset_um: float = 0.0
    isotropic_scale: float = 1.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    scale_axes: str = "global"
    axis_angle_deg: float = 0.0
    join_style: str = "mitre"
    miter_limit: float = 5.0
    corner_strategy: str = "sharp"
    corner_radius_um: float = 0.0
    operator_order: tuple[str, ...] = (
        "edge_offset",
        "isotropic_scale",
        "anisotropic_scale_xy",
        "corner_strategy",
    )

    def __post_init__(self) -> None:
        finite_fields = (
            "edge_offset_um",
            "isotropic_scale",
            "scale_x",
            "scale_y",
            "axis_angle_deg",
            "miter_limit",
            "corner_radius_um",
        )
        for name in finite_fields:
            value = _as_finite(getattr(self, name), name=name)
            object.__setattr__(self, name, value)
        if self.isotropic_scale <= 0.0 or self.scale_x <= 0.0 or self.scale_y <= 0.0:
            raise CorrectionError("all centroid scale factors must be greater than zero")
        if self.scale_axes not in {"global", "local"}:
            raise CorrectionError("scale_axes must be global or local")
        if self.join_style not in _JOIN_STYLE_CODES:
            raise CorrectionError(
                f"join_style must be one of {sorted(_JOIN_STYLE_CODES)}, got {self.join_style!r}"
            )
        if self.miter_limit <= 0.0:
            raise CorrectionError("miter_limit must be greater than zero")
        if self.corner_strategy not in {"sharp", "rounded"}:
            raise CorrectionError("corner_strategy must be 'sharp' or 'rounded'")
        if self.corner_radius_um < 0.0:
            raise CorrectionError("corner_radius_um must be non-negative")
        if self.corner_strategy == "rounded" and self.corner_radius_um <= 0.0:
            raise CorrectionError("rounded corners require corner_radius_um > 0")
        normalized_order = tuple(self.operator_order)
        unknown = set(normalized_order).difference(_KNOWN_OPERATORS)
        if unknown:
            raise CorrectionError(f"unknown correction operators: {sorted(unknown)}")
        object.__setattr__(self, "operator_order", normalized_order)

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_offset_um": self.edge_offset_um,
            "isotropic_scale": self.isotropic_scale,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "scale_axes": self.scale_axes,
            "axis_angle_deg": self.axis_angle_deg,
            "join_style": self.join_style,
            "miter_limit": self.miter_limit,
            "corner_strategy": self.corner_strategy,
            "corner_radius_um": self.corner_radius_um,
            "operator_order": list(self.operator_order),
        }


FeatureCorrectionConfig = FeatureCorrection
LocalCorrectionConfig = FeatureCorrection


@dataclass(frozen=True, slots=True)
class TriangleSideCorrection:
    '''User-facing single-side correction for equilateral triangular holes.'''

    kind: str = 'none'
    global_delta_nm: float = 0.0
    envelope_modulation_strength: float = 1.0
    regions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.kind not in {'none', 'equilateral_parallel_edge_v1'}:
            raise CorrectionError(
                'triangle_side_correction.kind must be '
                'equilateral_parallel_edge_v1'
            )
        object.__setattr__(
            self,
            'global_delta_nm',
            _as_finite(
                self.global_delta_nm,
                name='triangle_side_correction.global_delta_nm',
            ),
        )
        strength = _as_finite(
            self.envelope_modulation_strength,
            name='triangle_side_correction.envelope_modulation_strength',
        )
        if strength < 0.0:
            raise CorrectionError(
                'triangle_side_correction.envelope_modulation_strength '
                'must be non-negative'
            )
        object.__setattr__(self, 'envelope_modulation_strength', strength)
        normalized_regions: list[str] = []
        for index, raw_region in enumerate(self.regions):
            if not isinstance(raw_region, str) or not raw_region.strip():
                raise CorrectionError(
                    f'triangle_side_correction.regions[{index}] '
                    'must be a non-empty string'
                )
            region = raw_region.strip()
            if region in normalized_regions:
                raise CorrectionError(
                    'triangle_side_correction.regions must not contain duplicates'
                )
            normalized_regions.append(region)
        if self.kind != 'none' and not normalized_regions:
            raise CorrectionError(
                'triangle_side_correction.regions must be a non-empty sequence'
            )
        object.__setattr__(self, 'regions', tuple(normalized_regions))

    @property
    def global_edge_offset_um(self) -> float:
        return self.global_delta_nm / SIDE_TO_EDGE_OFFSET / 1000.0

    def applies_to(self, region: str) -> bool:
        return self.kind != 'none' and region in self.regions

    def to_dict(self) -> dict[str, Any]:
        return {
            'kind': self.kind,
            'global_delta_nm': self.global_delta_nm,
            'global_edge_offset_um': self.global_edge_offset_um,
            'envelope_modulation_strength': self.envelope_modulation_strength,
            'regions': list(self.regions),
        }


def triangle_side_correction_from_mapping(
    config: Mapping[str, Any] | None,
) -> TriangleSideCorrection:
    '''Parse the explicit triangle side-length correction interface.

    Missing configuration is a compatibility path for direct low-level callers:
    it leaves the global correction disabled and preserves the legacy envelope
    amplitude.
    '''

    if config is None:
        return TriangleSideCorrection()
    if not isinstance(config, Mapping):
        raise CorrectionError(
            'fabrication.triangle_side_correction must be an object'
        )
    raw = dict(config)
    regions = raw.get('regions', ())
    if isinstance(regions, (str, bytes)) or not isinstance(regions, Sequence):
        raise CorrectionError(
            'triangle_side_correction.regions must be a non-empty sequence'
        )
    return TriangleSideCorrection(
        kind=str(raw.get('kind', 'equilateral_parallel_edge_v1')),
        global_delta_nm=raw.get('global_delta_nm', 0.0),
        envelope_modulation_strength=raw.get(
            'envelope_modulation_strength', 1.0
        ),
        regions=tuple(regions),
    )


def feature_correction_from_mapping(config: Mapping[str, Any] | None) -> FeatureCorrection:
    """Parse one local-correction block with explicit length-unit suffixes."""

    config = {} if config is None else dict(config)
    edge_offset_um = _exclusive_length_um(
        config,
        um_keys=("edge_offset_um", "edge_bias_um"),
        nm_keys=("edge_offset_nm", "edge_bias_nm"),
    )

    isotropic = config.get("isotropic_scale", 1.0)
    centroid_scale = config.get("centroid_scale")
    if centroid_scale is not None:
        if isinstance(centroid_scale, Mapping):
            isotropic = centroid_scale.get("isotropic", centroid_scale.get("scale", isotropic))
        else:
            isotropic = centroid_scale

    scale_x = config.get("scale_x", 1.0)
    scale_y = config.get("scale_y", 1.0)
    anisotropic = config.get("anisotropic_scale_xy")
    if anisotropic is not None:
        if isinstance(anisotropic, Mapping):
            scale_x = anisotropic.get("x", anisotropic.get("scale_x", scale_x))
            scale_y = anisotropic.get("y", anisotropic.get("scale_y", scale_y))
        else:
            scale_x, scale_y = _pair(anisotropic, name="anisotropic_scale_xy")

    corner = config.get("corner_strategy", "sharp")
    corner_radius_um = _exclusive_length_um(
        config,
        um_keys=("corner_radius_um",),
        nm_keys=("corner_radius_nm",),
    )
    if isinstance(corner, Mapping):
        corner_mapping = dict(corner)
        corner = corner_mapping.get("kind", "sharp")
        corner_radius_um = _exclusive_length_um(
            corner_mapping,
            um_keys=("radius_um", "corner_radius_um"),
            nm_keys=("radius_nm", "corner_radius_nm"),
            default=corner_radius_um,
        )

    join_style = str(config.get("join_style", "mitre"))
    miter_limit = config.get("miter_limit", config.get("mitre_limit", 5.0))
    axis_angle_deg = config.get("axis_angle_deg", 0.0)
    scale_axes = str(config.get("scale_axes", "global"))
    operators = config.get("operators")
    if operators is None:
        operator_order = FeatureCorrection().operator_order
    else:
        if not isinstance(operators, Sequence) or isinstance(operators, (str, bytes)):
            raise CorrectionError("local correction operators must be an ordered list")
        parsed: list[str] = []
        for item in operators:
            if isinstance(item, str):
                parsed.append(item)
            elif isinstance(item, Mapping) and isinstance(item.get("kind"), str):
                kind = item["kind"]
                parsed.append(kind)
                if kind in {"edge_offset", "edge_offset_um"}:
                    if any(
                        key in config
                        for key in ("edge_offset_um", "edge_bias_um", "edge_offset_nm", "edge_bias_nm")
                    ):
                        raise CorrectionError(
                            "edge offset must be configured either as an operator or a top-level field, not both"
                        )
                    edge_offset_um = _exclusive_length_um(
                        item,
                        um_keys=("value_um", "edge_offset_um", "edge_bias_um"),
                        nm_keys=("value_nm", "edge_offset_nm", "edge_bias_nm"),
                    )
                    join_style = str(item.get("join_style", join_style))
                    miter_limit = item.get(
                        "miter_limit", item.get("mitre_limit", miter_limit)
                    )
                elif kind == "isotropic_scale":
                    isotropic = item.get("factor", item.get("scale", isotropic))
                elif kind == "anisotropic_scale_xy":
                    scale_x = item.get("x_factor", item.get("scale_x", scale_x))
                    scale_y = item.get("y_factor", item.get("scale_y", scale_y))
                    # ``global`` axes need no rotation.  A future geometry
                    # source may resolve a feature-specific local angle before
                    # constructing the effective correction.
                    axes = item.get("axes", "global")
                    if axes not in {"global", "local"}:
                        raise CorrectionError("anisotropic scale axes must be global or local")
                    scale_axes = str(axes)
                elif kind == "corner_strategy":
                    corner = item.get("strategy", item.get("value", corner))
                    corner_radius_um = _exclusive_length_um(
                        item,
                        um_keys=("radius_um", "corner_radius_um"),
                        nm_keys=("radius_nm", "corner_radius_nm"),
                        default=corner_radius_um,
                    )
            else:
                raise CorrectionError("every correction operator needs a string kind")
        operator_order = tuple(parsed)

    return FeatureCorrection(
        edge_offset_um=edge_offset_um,
        isotropic_scale=isotropic,
        scale_x=scale_x,
        scale_y=scale_y,
        scale_axes=scale_axes,
        axis_angle_deg=axis_angle_deg,
        join_style=join_style,
        miter_limit=miter_limit,
        corner_strategy=str(corner),
        corner_radius_um=corner_radius_um,
        operator_order=operator_order,
    )


def _ensure_polygon_result(polygon: Polygon, *, operation: str) -> Polygon:
    if polygon.is_empty:
        raise CorrectionError(f"{operation} collapsed the feature to empty geometry")
    if not isinstance(polygon, Polygon):
        raise CorrectionError(
            f"{operation} produced {polygon.geom_type}; a feature must remain one Polygon"
        )
    if polygon.area <= 0.0:
        raise CorrectionError(f"{operation} produced a zero-area feature")
    if not polygon.is_valid:
        raise CorrectionError(f"{operation} produced an invalid polygon")
    return polygon


def _scale_about_centroid(
    polygon: Polygon,
    *,
    scale_x: float,
    scale_y: float,
    axis_angle_deg: float,
) -> Polygon:
    origin = (polygon.centroid.x, polygon.centroid.y)
    working = polygon
    if axis_angle_deg:
        working = affinity.rotate(working, -axis_angle_deg, origin=origin, use_radians=False)
    working = affinity.scale(working, xfact=scale_x, yfact=scale_y, origin=origin)
    if axis_angle_deg:
        working = affinity.rotate(working, axis_angle_deg, origin=origin, use_radians=False)
    return working


def apply_feature_correction(
    polygon: Polygon,
    correction: FeatureCorrection | Mapping[str, Any],
) -> Polygon:
    """Apply local operators in their declared order.

    Positive edge offset expands an air hole/etch opening along its outward
    normal.  No implicit topology repair or feature deletion is performed.
    """

    if not isinstance(correction, FeatureCorrection):
        correction = feature_correction_from_mapping(correction)
    result = polygon
    for operator in correction.operator_order:
        if operator in {"edge_offset", "edge_offset_um"}:
            if correction.edge_offset_um:
                result = result.buffer(
                    correction.edge_offset_um,
                    join_style=_JOIN_STYLE_CODES[correction.join_style],
                    mitre_limit=correction.miter_limit,
                )
                result = _ensure_polygon_result(result, operation="edge offset")
        elif operator in {"centroid_scale", "isotropic_scale"}:
            if correction.isotropic_scale != 1.0:
                result = _scale_about_centroid(
                    result,
                    scale_x=correction.isotropic_scale,
                    scale_y=correction.isotropic_scale,
                    axis_angle_deg=correction.axis_angle_deg,
                )
                result = _ensure_polygon_result(result, operation="isotropic centroid scale")
        elif operator == "anisotropic_scale_xy":
            if correction.scale_x != 1.0 or correction.scale_y != 1.0:
                result = _scale_about_centroid(
                    result,
                    scale_x=correction.scale_x,
                    scale_y=correction.scale_y,
                    axis_angle_deg=correction.axis_angle_deg,
                )
                result = _ensure_polygon_result(result, operation="anisotropic centroid scale")
        elif operator == "corner_strategy":
            if correction.corner_strategy == "rounded":
                radius = correction.corner_radius_um
                result = result.buffer(-radius, join_style=1).buffer(radius, join_style=1)
                result = _ensure_polygon_result(result, operation="rounded corner strategy")
    return _ensure_polygon_result(result, operation="local correction")


apply_local_correction = apply_feature_correction


@dataclass(frozen=True, slots=True)
class EnvelopeEvaluation:
    kind: str
    target: str
    value: float
    normalized_x: float
    normalized_y: float
    applied: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "target": self.target,
            "value": self.value,
            "normalized_x": self.normalized_x,
            "normalized_y": self.normalized_y,
            "applied": self.applied,
        }


class SpatialEnvelope(Protocol):
    kind: str
    target: str

    def evaluate(self, position_um: Coordinate) -> EnvelopeEvaluation:
        """Evaluate a correction contribution at one nominal feature center."""


@dataclass(frozen=True, slots=True)
class ConstantEnvelope:
    value: float = 0.0
    target: str = "edge_offset_um"
    center_um: Coordinate = (0.0, 0.0)
    half_size_um: Coordinate | None = None
    outside_policy: str = "error"
    kind: str = field(default="constant", init=False)

    def evaluate(self, position_um: Coordinate) -> EnvelopeEvaluation:
        if self.half_size_um is None:
            nx = ny = 0.0
        else:
            nx, ny = _normalized_envelope_position(
                position_um,
                self.center_um,
                self.half_size_um,
                self.outside_policy,
            )
        return EnvelopeEvaluation(self.kind, self.target, self.value, nx, ny)


@dataclass(frozen=True, slots=True)
class RadialEvenPolynomialEnvelope:
    """``sum(c[k] * rho**(2*k))`` on an elliptical normalized radius."""

    coefficients: tuple[float, ...]
    center_um: Coordinate
    radius_x_um: float
    radius_y_um: float
    target: str = "edge_offset_um"
    outside_policy: str = "error"
    kind: str = field(default="radial_even_polynomial", init=False)

    def __post_init__(self) -> None:
        if not self.coefficients:
            raise CorrectionError("radial envelope requires at least one coefficient")
        if not all(math.isfinite(float(value)) for value in self.coefficients):
            raise CorrectionError("radial envelope coefficients must be finite")
        if self.radius_x_um <= 0.0 or self.radius_y_um <= 0.0:
            raise CorrectionError("radial envelope radii must be greater than zero")

    def evaluate(self, position_um: Coordinate) -> EnvelopeEvaluation:
        nx, ny = _normalized_envelope_position(
            position_um,
            self.center_um,
            (self.radius_x_um, self.radius_y_um),
            self.outside_policy,
        )
        rho_squared = nx * nx + ny * ny
        if rho_squared > 1.0 + 1e-12:
            if self.outside_policy == "error":
                raise CorrectionError(
                    f"feature center {position_um!r} lies outside the "
                    "radial spatial-envelope field"
                )
            radial_scale = 1.0 / math.sqrt(rho_squared)
            nx *= radial_scale
            ny *= radial_scale
            rho_squared = 1.0
        value = sum(
            coefficient * rho_squared**order
            for order, coefficient in enumerate(self.coefficients)
        )
        return EnvelopeEvaluation(self.kind, self.target, value, nx, ny)


@dataclass(frozen=True, slots=True)
class SeparableEvenPolynomialXYEnvelope:
    """``c0 + sum(cx[k]*x**(2k+2)) + sum(cy[k]*y**(2k+2))``."""

    constant: float
    x_coefficients: tuple[float, ...]
    y_coefficients: tuple[float, ...]
    center_um: Coordinate
    half_width_um: float
    half_height_um: float
    target: str = "edge_offset_um"
    outside_policy: str = "error"
    kind: str = field(default="separable_even_polynomial_xy", init=False)

    def __post_init__(self) -> None:
        values = (self.constant, *self.x_coefficients, *self.y_coefficients)
        if not all(math.isfinite(float(value)) for value in values):
            raise CorrectionError("separable envelope coefficients must be finite")
        if self.half_width_um <= 0.0 or self.half_height_um <= 0.0:
            raise CorrectionError("separable envelope half-ranges must be greater than zero")

    def evaluate(self, position_um: Coordinate) -> EnvelopeEvaluation:
        nx, ny = _normalized_envelope_position(
            position_um,
            self.center_um,
            (self.half_width_um, self.half_height_um),
            self.outside_policy,
        )
        x_value = sum(value * nx ** (2 * (order + 1)) for order, value in enumerate(self.x_coefficients))
        y_value = sum(value * ny ** (2 * (order + 1)) for order, value in enumerate(self.y_coefficients))
        return EnvelopeEvaluation(
            self.kind,
            self.target,
            self.constant + x_value + y_value,
            nx,
            ny,
        )


def _coefficient_values(
    config: Mapping[str, Any],
    *,
    base_name: str,
    target: str,
    default: Sequence[float] | None = None,
    implicit_nm: bool = False,
) -> tuple[float, ...]:
    keys = (f"{base_name}_um", f"{base_name}_nm", base_name)
    present = [key for key in keys if key in config]
    if len(present) > 1:
        raise CorrectionError("conflicting envelope coefficient fields: " + ", ".join(present))
    if not present:
        values = () if default is None else tuple(default)
    else:
        raw = config[present[0]]
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
            raise CorrectionError(f"{present[0]} must be a list")
        values = tuple(_as_finite(value, name=present[0]) for value in raw)
        if present[0].endswith("_nm") or (
            present[0] == base_name and target == "edge_offset_um" and implicit_nm
        ):
            values = tuple(value / 1000.0 for value in values)
    if (
        target == "edge_offset_um"
        and present
        and present[0] == base_name
        and not implicit_nm
    ):
        raise CorrectionError(
            f"{base_name} needs an explicit _um or _nm suffix for edge-offset envelopes"
        )
    return values


def _normalized_envelope_position(
    position_um: Coordinate,
    center_um: Coordinate,
    half_size_um: Coordinate,
    outside_policy: str,
) -> Coordinate:
    if half_size_um[0] <= 0.0 or half_size_um[1] <= 0.0:
        raise CorrectionError("spatial envelope half_size_um values must be positive")
    nx = (position_um[0] - center_um[0]) / half_size_um[0]
    ny = (position_um[1] - center_um[1]) / half_size_um[1]
    outside = abs(nx) > 1.0 + 1e-12 or abs(ny) > 1.0 + 1e-12
    if outside:
        if outside_policy == "error":
            raise CorrectionError(
                f"feature center {position_um!r} lies outside the spatial-envelope field"
            )
        if outside_policy == "clip":
            nx = max(-1.0, min(1.0, nx))
            ny = max(-1.0, min(1.0, ny))
        else:
            raise CorrectionError("spatial envelope outside_policy must be error or clip")
    elif outside_policy not in {"error", "clip"}:
        raise CorrectionError("spatial envelope outside_policy must be error or clip")
    return (nx, ny)


def _normalize_envelope_target(value: Any) -> str:
    aliases = {
        "edge_offset": "edge_offset_um",
        "edge_bias": "edge_offset_um",
        "edge_offset_um": "edge_offset_um",
        "edge_offset_nm": "edge_offset_um",
        "isotropic_scale": "isotropic_scale_delta",
        "isotropic_scale_delta": "isotropic_scale_delta",
    }
    if value not in aliases:
        raise CorrectionError(
            "spatial envelope target must be edge_offset_um or isotropic_scale_delta"
        )
    return aliases[value]


def _spatial_envelope_regions(
    config: Mapping[str, Any] | None,
) -> tuple[str, ...] | None:
    if config is None or "regions" not in config:
        return None
    raw_regions = config["regions"]
    if isinstance(raw_regions, (str, bytes)) or not isinstance(raw_regions, Sequence):
        raise CorrectionError("spatial_envelope.regions must be a non-empty sequence")
    regions: list[str] = []
    for index, raw_region in enumerate(raw_regions):
        if not isinstance(raw_region, str) or not raw_region.strip():
            raise CorrectionError(
                f"spatial_envelope.regions[{index}] must be a non-empty string"
            )
        region = raw_region.strip()
        if region in regions:
            raise CorrectionError("spatial_envelope.regions must not contain duplicates")
        regions.append(region)
    if not regions:
        raise CorrectionError("spatial_envelope.regions must be a non-empty sequence")
    return tuple(regions)


def spatial_envelope_from_mapping(config: Mapping[str, Any] | None) -> SpatialEnvelope:
    config = {} if config is None else dict(config)
    if config.get("enabled") is False:
        return ConstantEnvelope()
    kind = str(config.get("kind", "constant"))
    raw_target = config.get("target", "edge_offset_um")
    target = _normalize_envelope_target(raw_target)
    implicit_nm = raw_target == "edge_offset_nm"
    center_raw = config.get("center_um", config.get("write_field_center_um", (0.0, 0.0)))
    center = _pair(center_raw, name="spatial_envelope.center_um")
    half_size_raw = config.get("half_size_um")
    half_size = (
        _pair(half_size_raw, name="spatial_envelope.half_size_um")
        if half_size_raw is not None
        else None
    )
    outside_policy = str(config.get("outside_policy", "error"))

    if kind == "constant":
        if "coefficients" in config:
            coefficients = _coefficient_values(
                config,
                base_name="coefficients",
                target=target,
                implicit_nm=implicit_nm,
            )
            if len(coefficients) != 1:
                raise CorrectionError("constant envelope requires exactly one coefficient")
            value = coefficients[0]
        elif target == "edge_offset_um":
            value = _exclusive_length_um(
                config,
                um_keys=("value_um", "edge_offset_um", "edge_bias_um"),
                nm_keys=("value_nm", "edge_offset_nm", "edge_bias_nm"),
            )
        else:
            value = _as_finite(
                config.get("value", config.get("scale_delta", 0.0)),
                name="spatial_envelope.value",
            )
        return ConstantEnvelope(
            value=value,
            target=target,
            center_um=center,
            half_size_um=half_size,
            outside_policy=outside_policy,
        )

    if kind == "radial_even_polynomial":
        common_radius = config.get("radius_um")
        radius_x = config.get(
            "radius_x_um", common_radius if common_radius is not None else (half_size[0] if half_size else None)
        )
        radius_y = config.get(
            "radius_y_um", common_radius if common_radius is not None else (half_size[1] if half_size else None)
        )
        if radius_x is None or radius_y is None:
            raise CorrectionError("radial envelope requires radius_um or both radius_x_um/radius_y_um")
        coefficients = _coefficient_values(
            config,
            base_name="coefficients",
            target=target,
            implicit_nm=implicit_nm,
        )
        return RadialEvenPolynomialEnvelope(
            coefficients=coefficients,
            center_um=center,
            radius_x_um=_as_finite(radius_x, name="radius_x_um"),
            radius_y_um=_as_finite(radius_y, name="radius_y_um"),
            target=target,
            outside_policy=outside_policy,
        )
    if kind == "separable_even_polynomial_xy":
        half_width = config.get(
            "half_width_um",
            config.get("radius_x_um", half_size[0] if half_size else None),
        )
        half_height = config.get(
            "half_height_um",
            config.get("radius_y_um", half_size[1] if half_size else None),
        )
        if half_width is None or half_height is None:
            raise CorrectionError(
                "separable envelope requires half_width_um and half_height_um"
            )
        if "coefficients" in config and not any(
            key in config
            for key in ("x_coefficients", "x_coefficients_um", "x_coefficients_nm")
        ):
            raw_coefficients = config["coefficients"]
            if (
                isinstance(raw_coefficients, Sequence)
                and len(raw_coefficients) == 3
                and not isinstance(raw_coefficients[0], Sequence)
                and isinstance(raw_coefficients[1], Sequence)
                and isinstance(raw_coefficients[2], Sequence)
            ):
                constant_raw = _as_finite(raw_coefficients[0], name="coefficients[0]")
                x_raw = raw_coefficients[1]
                y_raw = raw_coefficients[2]
            elif (
                isinstance(raw_coefficients, Sequence)
                and len(raw_coefficients) == 2
                and all(isinstance(value, Sequence) for value in raw_coefficients)
            ):
                constant_raw = 0.0
                x_raw, y_raw = raw_coefficients
            elif isinstance(raw_coefficients, Sequence) and not isinstance(
                raw_coefficients, (str, bytes)
            ):
                constant_raw = 0.0
                x_raw = y_raw = raw_coefficients
            else:
                raise CorrectionError("invalid separable envelope coefficients")
            factor = 0.001 if implicit_nm else 1.0
            constant = constant_raw * factor
            x_coefficients = tuple(
                _as_finite(value, name="x coefficients") * factor for value in x_raw
            )
            y_coefficients = tuple(
                _as_finite(value, name="y coefficients") * factor for value in y_raw
            )
        else:
            x_coefficients = _coefficient_values(
                config,
                base_name="x_coefficients",
                target=target,
                implicit_nm=implicit_nm,
            )
            y_coefficients = _coefficient_values(
                config,
                base_name="y_coefficients",
                target=target,
                implicit_nm=implicit_nm,
            )
            if target == "edge_offset_um":
                constant = _exclusive_length_um(
                    config,
                    um_keys=("constant_um",),
                    nm_keys=("constant_nm",),
                )
            else:
                constant = _as_finite(config.get("constant", 0.0), name="constant")
        return SeparableEvenPolynomialXYEnvelope(
            constant=constant,
            x_coefficients=x_coefficients,
            y_coefficients=y_coefficients,
            center_um=center,
            half_width_um=_as_finite(half_width, name="half_width_um"),
            half_height_um=_as_finite(half_height, name="half_height_um"),
            target=target,
            outside_policy=outside_policy,
        )
    raise CorrectionError(f"unsupported spatial envelope kind: {kind!r}")


def evaluate_spatial_envelope(
    config: SpatialEnvelope | Mapping[str, Any] | None,
    position_um: Coordinate,
) -> EnvelopeEvaluation:
    envelope = (
        spatial_envelope_from_mapping(config)
        if config is None or isinstance(config, Mapping)
        else config
    )
    return envelope.evaluate(position_um)


@dataclass(frozen=True, slots=True)
class LayoutTransform:
    origin_um: Coordinate = (0.0, 0.0)
    mirror_x: bool = False
    mirror_y: bool = False
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation_deg: float = 0.0
    translation_um: Coordinate = (0.0, 0.0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin_um", _pair(self.origin_um, name="origin_um"))
        object.__setattr__(
            self, "translation_um", _pair(self.translation_um, name="translation_um")
        )
        scale_x = _as_finite(self.scale_x, name="scale_x")
        scale_y = _as_finite(self.scale_y, name="scale_y")
        if scale_x <= 0.0 or scale_y <= 0.0:
            raise CorrectionError("layout scale factors must be greater than zero")
        object.__setattr__(self, "scale_x", scale_x)
        object.__setattr__(self, "scale_y", scale_y)
        object.__setattr__(
            self, "rotation_deg", _as_finite(self.rotation_deg, name="rotation_deg")
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "origin_um": list(self.origin_um),
            "mirror_x": self.mirror_x,
            "mirror_y": self.mirror_y,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "rotation_deg": self.rotation_deg,
            "translation_um": list(self.translation_um),
        }


def layout_transform_from_mapping(config: Mapping[str, Any] | None) -> LayoutTransform:
    config = {} if config is None else dict(config)
    origin = config.get("origin_um", (0.0, 0.0))
    translation = config.get("translation_um")
    if translation is None:
        translation = (
            config.get("translation_x_um", 0.0),
            config.get("translation_y_um", 0.0),
        )
    magnification = config.get("magnification", {})
    if magnification is None:
        magnification = {}
    if not isinstance(magnification, Mapping):
        raise CorrectionError("layout magnification must be an object")
    return LayoutTransform(
        origin_um=origin,
        mirror_x=bool(config.get("mirror_x", False)),
        mirror_y=bool(config.get("mirror_y", False)),
        scale_x=config.get("scale_x", magnification.get("x", 1.0)),
        scale_y=config.get("scale_y", magnification.get("y", 1.0)),
        rotation_deg=config.get("rotation_deg", 0.0),
        translation_um=translation,
    )


def transform_polygon(polygon: Polygon, transform: LayoutTransform) -> Polygon:
    x_factor = -transform.scale_x if transform.mirror_x else transform.scale_x
    y_factor = -transform.scale_y if transform.mirror_y else transform.scale_y
    result = affinity.scale(
        polygon,
        xfact=x_factor,
        yfact=y_factor,
        origin=transform.origin_um,
    )
    if transform.rotation_deg:
        result = affinity.rotate(
            result,
            transform.rotation_deg,
            origin=transform.origin_um,
            use_radians=False,
        )
    if transform.translation_um != (0.0, 0.0):
        result = affinity.translate(
            result,
            xoff=transform.translation_um[0],
            yoff=transform.translation_um[1],
        )
    return _ensure_polygon_result(result, operation="layout coordinate transform")


def _round_grid_quotient(value: float) -> int:
    return math.floor(value + 0.5) if value >= 0.0 else math.ceil(value - 0.5)


def snap_coordinate_to_grid(value: float, grid_um: float, origin_um: float = 0.0) -> float:
    grid = _as_finite(grid_um, name="grid_um")
    if grid <= 0.0:
        raise CorrectionError("grid_um must be greater than zero")
    quotient = (value - origin_um) / grid
    return origin_um + _round_grid_quotient(quotient) * grid


def _snap_ring(
    coordinates: Sequence[Sequence[float]], grid_um: float, origin_um: Coordinate
) -> list[Coordinate]:
    snapped: list[Coordinate] = []
    for coordinate in coordinates:
        point = (
            snap_coordinate_to_grid(float(coordinate[0]), grid_um, origin_um[0]),
            snap_coordinate_to_grid(float(coordinate[1]), grid_um, origin_um[1]),
        )
        if not snapped or point != snapped[-1]:
            snapped.append(point)
    if len(snapped) > 1 and snapped[0] == snapped[-1]:
        snapped.pop()
    if len(snapped) < 3 or len(set(snapped)) < 3:
        raise CorrectionError("grid snapping collapsed a polygon ring below three vertices")
    return snapped


def snap_polygon_to_grid(
    polygon: Polygon,
    grid_um: float,
    origin_um: Coordinate = (0.0, 0.0),
) -> Polygon:
    """Quantize all vertices and reject any collapsed or invalid feature."""

    origin = _pair(origin_um, name="grid_origin_um")
    exterior = _snap_ring(list(polygon.exterior.coords), grid_um, origin)
    interiors = [
        _snap_ring(list(interior.coords), grid_um, origin)
        for interior in polygon.interiors
    ]
    result = Polygon(exterior, interiors)
    return _ensure_polygon_result(result, operation="grid snap")


def _grid_contract(fabrication: Mapping[str, Any]) -> tuple[float | None, Coordinate]:
    grid_config = fabrication.get("grid")
    if grid_config is None:
        grid_config = {}
    if isinstance(grid_config, (int, float)):
        grid_config = {"step_um": grid_config}
    if not isinstance(grid_config, Mapping):
        raise CorrectionError("fabrication.grid must be an object or a numeric um step")
    if grid_config.get("enabled") is False:
        return None, (0.0, 0.0)
    merged = dict(grid_config)
    for key in ("grid_um", "address_grid_um", "writer_grid_um", "grid_nm", "address_grid_nm"):
        if key in fabrication and key not in merged:
            merged[key] = fabrication[key]
    step = _exclusive_length_um(
        merged,
        um_keys=("step_um", "grid_um", "address_grid_um", "writer_grid_um"),
        nm_keys=("step_nm", "grid_nm", "address_grid_nm"),
        default=0.0,
    )
    if step == 0.0:
        return None, (0.0, 0.0)
    if step < 0.0:
        raise CorrectionError("writer grid step must be positive")
    origin = _pair(merged.get("origin_um", (0.0, 0.0)), name="grid.origin_um")
    return step, origin


def local_correction_for_region(
    fabrication: Mapping[str, Any], region: str
) -> FeatureCorrection:
    raw = fabrication.get("local_correction", fabrication.get("feature_correction", {}))
    if raw is None:
        raw = {}
    if not isinstance(raw, Mapping):
        raise CorrectionError("fabrication.local_correction must be an object")
    raw = dict(raw)
    base: dict[str, Any]
    if "default" in raw:
        if not isinstance(raw["default"], Mapping):
            raise CorrectionError("local_correction.default must be an object")
        base = dict(raw["default"])
    else:
        base = {
            key: value
            for key, value in raw.items()
            if key not in {"by_region", "regions", "default"}
        }
    region_map = raw.get("by_region", raw.get("regions", {}))
    if region_map:
        if not isinstance(region_map, Mapping):
            raise CorrectionError("local correction region overrides must be an object")
        override = region_map.get(region)
        if override is not None:
            if not isinstance(override, Mapping):
                raise CorrectionError(f"local correction override for {region!r} must be an object")
            base.update(override)
    if "corner_strategy" not in base and "corner_strategy" in fabrication:
        base["corner_strategy"] = fabrication["corner_strategy"]
    return feature_correction_from_mapping(base)


def _combine_effective_correction(
    base: FeatureCorrection,
    envelope: EnvelopeEvaluation,
    response: GeometryCorrectionContribution,
    *,
    triangle_edge_offset_um: float = 0.0,
) -> FeatureCorrection:
    edge_offset = (
        base.edge_offset_um + triangle_edge_offset_um + response.edge_offset_um
    )
    isotropic = base.isotropic_scale * (1.0 + response.isotropic_scale_delta)
    if envelope.target == "edge_offset_um":
        edge_offset += envelope.value
    elif envelope.target == "isotropic_scale_delta":
        isotropic *= 1.0 + envelope.value
    return replace(
        base,
        edge_offset_um=edge_offset,
        isotropic_scale=isotropic,
        scale_x=base.scale_x * (1.0 + response.scale_x_delta),
        scale_y=base.scale_y * (1.0 + response.scale_y_delta),
    )


def apply_corrections(
    layout: LayoutPlan,
    fabrication: Mapping[str, Any],
    dose: Mapping[str, Any],
    layout_transform: Mapping[str, Any],
) -> LayoutPlan:
    """CLI-facing correction pipeline.

    The order is nominal-center envelope/dose evaluation, feature-local
    correction, layout transform, then address-grid quantization.  DRC is a
    separate mandatory stage after this function.
    """

    fabrication = dict(fabrication)
    dose = dict(dose)
    layout_transform = dict(layout_transform)
    transform = layout_transform_from_mapping(layout_transform)
    ppm = fabrication.get("scale_correction_ppm", {})
    if ppm:
        if not isinstance(ppm, Mapping):
            raise CorrectionError("fabrication.scale_correction_ppm must be an object")
        ppm_x = _as_finite(ppm.get("x", 0.0), name="scale_correction_ppm.x")
        ppm_y = _as_finite(ppm.get("y", 0.0), name="scale_correction_ppm.y")
        transform = replace(
            transform,
            scale_x=transform.scale_x * (1.0 + ppm_x * 1e-6),
            scale_y=transform.scale_y * (1.0 + ppm_y * 1e-6),
        )
    envelope_config = fabrication.get(
        "spatial_envelope", fabrication.get("envelope", {"kind": "constant", "value_um": 0.0})
    )
    envelope = spatial_envelope_from_mapping(envelope_config)
    envelope_regions = _spatial_envelope_regions(
        envelope_config if isinstance(envelope_config, Mapping) else None
    )
    triangle_side = triangle_side_correction_from_mapping(
        fabrication.get('triangle_side_correction')
    )
    dose_field, process_response, dose_encoder = resolve_dose_components(dose)
    encoder_is_explicit = "encoder" in dose
    placement = fabrication.get("placement_distortion", {"kind": "none"})
    if not isinstance(placement, Mapping) or placement.get("kind", "none") != "none":
        raise CorrectionError(
            "v1 supports only placement_distortion.kind='none'; calibrated vector fields are not yet implemented"
        )
    grid_um, grid_origin = _grid_contract(fabrication)
    configured_etch_layer = layout_transform.get("etch_layer")
    if configured_etch_layer is not None and (
        not isinstance(configured_etch_layer, str) or not configured_etch_layer.strip()
    ):
        raise CorrectionError("layout etch_layer must be a non-empty string")

    corrected_features: list[LayoutFeature] = []
    for feature in layout.features:
        nominal_design = feature.nominal_polygon
        nominal_center = feature.nominal_centroid_um
        if envelope_regions is None or feature.region in envelope_regions:
            raw_envelope_value = envelope.evaluate(nominal_center)
        else:
            raw_envelope_value = EnvelopeEvaluation(
                kind=envelope.kind,
                target=envelope.target,
                value=0.0,
                normalized_x=0.0,
                normalized_y=0.0,
                applied=False,
            )
        triangle_applied = triangle_side.applies_to(feature.region)
        envelope_strength = (
            triangle_side.envelope_modulation_strength if triangle_applied else 1.0
        )
        envelope_value = replace(
            raw_envelope_value,
            value=raw_envelope_value.value * envelope_strength,
        )
        triangle_edge_offset_um = (
            triangle_side.global_edge_offset_um if triangle_applied else 0.0
        )
        dose_sample = dose_field.evaluate(nominal_center, feature)
        response_value = process_response.evaluate(
            dose_sample,
            nominal_center,
            feature,
            fabrication,
        )
        base = local_correction_for_region(fabrication, feature.region)
        effective = _combine_effective_correction(
            base,
            envelope_value,
            response_value,
            triangle_edge_offset_um=triangle_edge_offset_um,
        )
        if effective.scale_axes == "local":
            local_angle = feature.metadata.get("local_axis_angle_deg")
            if local_angle is None:
                raise CorrectionError(
                    f"feature {feature.feature_id!r} requests local anisotropic axes "
                    "but metadata.local_axis_angle_deg is missing"
                )
            effective = replace(
                effective,
                axis_angle_deg=effective.axis_angle_deg
                + _as_finite(local_angle, name="local_axis_angle_deg"),
            )
        corrected_design = apply_feature_correction(nominal_design, effective)

        nominal_final = transform_polygon(nominal_design, transform)
        corrected_final = transform_polygon(corrected_design, transform)
        max_snap_displacement = 0.0
        if grid_um is not None:
            before = list(corrected_final.exterior.coords)
            corrected_final = snap_polygon_to_grid(corrected_final, grid_um, grid_origin)
            after = list(corrected_final.exterior.coords)
            # Vertex removal can change list lengths; Hausdorff distance is the
            # stable bound relevant to final geometry.
            max_snap_displacement = float(
                Polygon(before).hausdorff_distance(corrected_final)
            ) if len(before) >= 4 else 0.0

        dxf_layer = (
            feature.dxf_layer
            if configured_etch_layer is None
            else configured_etch_layer.strip()
        )
        if encoder_is_explicit:
            dxf_layer = dose_encoder.encode_layer(dxf_layer, dose_sample, feature)
        metadata = dict(feature.metadata)
        triangle_metadata = {
            'applied': triangle_applied,
            'kind': triangle_side.kind,
            'global_delta_nm': (
                triangle_side.global_delta_nm if triangle_applied else 0.0
            ),
            'global_edge_offset_um': triangle_edge_offset_um,
            'envelope_modulation_strength': envelope_strength,
            'raw_envelope': raw_envelope_value.to_dict(),
            'modulated_envelope': envelope_value.to_dict(),
            'applied_side_delta_nm': (
                SIDE_TO_EDGE_OFFSET
                * 1000.0
                * (triangle_edge_offset_um + envelope_value.value)
                if envelope.target == 'edge_offset_um'
                else None
            ),
            'effective_side_delta_nm': (
                SIDE_TO_EDGE_OFFSET * 1000.0 * effective.edge_offset_um
            ),
        }
        metadata["correction"] = {
            "base": base.to_dict(),
            "envelope": envelope_value.to_dict(),
            "dose": dose_sample.to_dict(),
            "process_response": response_value.to_dict(),
            "effective": effective.to_dict(),
            "grid_snap_max_displacement_um": max_snap_displacement,
        }
        metadata['correction']['triangle_side_correction'] = triangle_metadata
        corrected_features.append(
            replace(
                feature,
                nominal_polygon=nominal_final,
                polygon=corrected_final,
                dxf_layer=dxf_layer,
                metadata=metadata,
            )
        )

    boundary = None
    if layout.boundary is not None:
        boundary = transform_polygon(layout.boundary, transform)
        if grid_um is not None:
            boundary = snap_polygon_to_grid(boundary, grid_um, grid_origin)

    metadata = dict(layout.metadata)
    metadata["correction_pipeline"] = {
        "order": [
            "spatial_envelope_and_dose",
            "feature_local_correction",
            "layout_transform",
            "grid_snap",
        ],
        "layout_transform": transform.to_dict(),
        "grid_um": grid_um,
        "grid_origin_um": list(grid_origin),
        "dose_field": dict(dose_field.identity()),
        "dose_encoder": dict(dose_encoder.identity()),
        "spatial_envelope_kind": envelope.kind,
        "spatial_envelope_target": envelope.target,
        "spatial_envelope_regions": (
            list(envelope_regions) if envelope_regions is not None else None
        ),
    }
    metadata['correction_pipeline'][
        'triangle_side_correction'
    ] = triangle_side.to_dict()
    return LayoutPlan(
        geometry_kind=layout.geometry_kind,
        features=corrected_features,
        boundary=boundary,
        metadata=metadata,
    )


__all__ = [
    'TriangleSideCorrection',
    'triangle_side_correction_from_mapping',
    "ConstantEnvelope",
    "CorrectionError",
    "EnvelopeEvaluation",
    "FeatureCorrection",
    "FeatureCorrectionConfig",
    "LayoutTransform",
    "LocalCorrectionConfig",
    "RadialEvenPolynomialEnvelope",
    "SeparableEvenPolynomialXYEnvelope",
    "SpatialEnvelope",
    "apply_corrections",
    "apply_feature_correction",
    "apply_local_correction",
    "evaluate_spatial_envelope",
    "feature_correction_from_mapping",
    "local_correction_for_region",
    "layout_transform_from_mapping",
    "snap_coordinate_to_grid",
    "snap_polygon_to_grid",
    "spatial_envelope_from_mapping",
    "transform_polygon",
]
