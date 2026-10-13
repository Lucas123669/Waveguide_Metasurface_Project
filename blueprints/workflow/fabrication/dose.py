"""Dose-field, process-response, and encoding extension points.

Version 1 deliberately does not invent a dose-to-CD relationship.  A scalar
dose can be carried through the pipeline and identity while the
``pass_through`` response contributes zero geometry correction.  The protocols
below keep the calibrated spatial/response implementations replaceable later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping, Protocol, runtime_checkable

from ..models import Coordinate, LayoutFeature


class DoseConfigurationError(ValueError):
    """Raised when a dose contract is incomplete or internally inconsistent."""


@dataclass(frozen=True, slots=True)
class DoseSample:
    """Dose evaluated at one layout position."""

    value: float | None
    unit: str | None
    field_kind: str
    assigned: bool
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.field_kind,
            "assigned": self.assigned,
            "value": self.value,
            "unit": self.unit,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class GeometryCorrectionContribution:
    """Geometry deltas returned by a calibrated process response.

    Scale fields are deltas: ``0`` means no contribution and ``0.01`` means a
    one-percent multiplicative increase when combined by the correction stage.
    """

    edge_offset_um: float = 0.0
    isotropic_scale_delta: float = 0.0
    scale_x_delta: float = 0.0
    scale_y_delta: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        values = (
            self.edge_offset_um,
            self.isotropic_scale_delta,
            self.scale_x_delta,
            self.scale_y_delta,
        )
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("process-response geometry contributions must be finite")

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_offset_um": float(self.edge_offset_um),
            "isotropic_scale_delta": float(self.isotropic_scale_delta),
            "scale_x_delta": float(self.scale_x_delta),
            "scale_y_delta": float(self.scale_y_delta),
            "metadata": dict(self.metadata),
        }


@runtime_checkable
class DoseField(Protocol):
    """A scalar or spatial exposure-dose field."""

    kind: str

    def evaluate(
        self, position_um: Coordinate, feature: LayoutFeature | None = None
    ) -> DoseSample:
        """Evaluate dose at *position_um*."""

    def identity(self) -> Mapping[str, Any]:
        """Return stable, JSON-serializable identity fields."""


@runtime_checkable
class ProcessResponse(Protocol):
    """Convert a dose sample into an additive geometry contribution."""

    kind: str

    def evaluate(
        self,
        sample: DoseSample,
        position_um: Coordinate,
        feature: LayoutFeature,
        profile: Mapping[str, Any] | None = None,
    ) -> GeometryCorrectionContribution:
        """Return the calibrated correction contribution."""


@runtime_checkable
class DoseEncoder(Protocol):
    """Map dose to a downstream exposure representation."""

    kind: str

    def encode_layer(
        self, base_layer: str, sample: DoseSample, feature: LayoutFeature
    ) -> str:
        """Return the physical output layer for this dose sample."""

    def identity(self) -> Mapping[str, Any]:
        """Return stable, JSON-serializable encoder identity fields."""


@dataclass(frozen=True, slots=True)
class ScalarDoseField:
    """One explicitly assigned dose over the complete layout."""

    value: float
    unit: str
    kind: str = field(default="scalar", init=False)

    def __post_init__(self) -> None:
        if isinstance(self.value, bool):
            raise DoseConfigurationError("scalar dose value must be numeric, not boolean")
        value = float(self.value)
        if not math.isfinite(value) or value < 0.0:
            raise DoseConfigurationError("scalar dose value must be finite and non-negative")
        if not isinstance(self.unit, str) or not self.unit.strip():
            raise DoseConfigurationError("scalar dose unit must be a non-empty string")
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "unit", self.unit.strip())

    def evaluate(
        self, position_um: Coordinate, feature: LayoutFeature | None = None
    ) -> DoseSample:
        del position_um, feature
        return DoseSample(
            value=self.value,
            unit=self.unit,
            field_kind=self.kind,
            assigned=True,
        )

    def identity(self) -> Mapping[str, Any]:
        return {"kind": self.kind, "value": self.value, "unit": self.unit}


@dataclass(frozen=True, slots=True)
class UnassignedDoseField:
    """An explicit marker that dose has not yet been assigned."""

    kind: str = field(default="unassigned", init=False)

    def evaluate(
        self, position_um: Coordinate, feature: LayoutFeature | None = None
    ) -> DoseSample:
        del position_um, feature
        return DoseSample(
            value=None,
            unit=None,
            field_kind=self.kind,
            assigned=False,
        )

    def identity(self) -> Mapping[str, Any]:
        return {"kind": self.kind, "assigned": False}


@dataclass(frozen=True, slots=True)
class PassThroughProcessResponse:
    """A no-op response used until calibration data exists."""

    kind: str = field(default="pass_through", init=False)

    def evaluate(
        self,
        sample: DoseSample,
        position_um: Coordinate,
        feature: LayoutFeature,
        profile: Mapping[str, Any] | None = None,
    ) -> GeometryCorrectionContribution:
        del position_um, feature, profile
        return GeometryCorrectionContribution(
            metadata={
                "response_kind": self.kind,
                "dose_assigned": sample.assigned,
            }
        )


@dataclass(frozen=True, slots=True)
class ExternalRecipeDoseEncoder:
    """Keep DXF layers unchanged; dose is supplied by the writer job recipe."""

    kind: str = field(default="external_recipe", init=False)

    def encode_layer(
        self, base_layer: str, sample: DoseSample, feature: LayoutFeature
    ) -> str:
        del sample, feature
        return base_layer

    def identity(self) -> Mapping[str, Any]:
        return {"kind": self.kind, "encodes_dose_in_dxf": False}


@dataclass(frozen=True, slots=True)
class UnassignedDoseEncoder:
    """Explicitly reject any attempt to encode assigned dose into DXF."""

    kind: str = field(default="unassigned", init=False)

    def encode_layer(
        self, base_layer: str, sample: DoseSample, feature: LayoutFeature
    ) -> str:
        del feature
        if sample.assigned:
            raise DoseConfigurationError(
                "dose encoder is unassigned; select external_recipe or a calibrated encoder"
            )
        return base_layer

    def identity(self) -> Mapping[str, Any]:
        return {"kind": self.kind, "encodes_dose_in_dxf": False}


def _kind_from(value: Mapping[str, Any] | str | None, *, default: str) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    kind = value.get("kind", default)
    if not isinstance(kind, str):
        raise DoseConfigurationError("dose component kind must be a string")
    return kind


def create_dose_field(config: Mapping[str, Any] | None) -> DoseField:
    """Build the configured dose field.

    Empty input maps to the explicit ``unassigned`` state; production config
    validation can still require the caller to spell that state out.
    """

    config = {} if config is None else dict(config)
    kind = _kind_from(config, default="unassigned")
    if kind == "unassigned":
        unexpected = {
            key for key in ("value", "unit") if key in config and config[key] is not None
        }
        if unexpected:
            raise DoseConfigurationError(
                "unassigned dose requires value and unit to be null or omitted"
            )
        return UnassignedDoseField()
    if kind == "scalar":
        if "value" not in config or "unit" not in config:
            raise DoseConfigurationError("scalar dose requires explicit value and unit")
        return ScalarDoseField(value=config["value"], unit=config["unit"])
    raise DoseConfigurationError(f"unsupported dose field kind: {kind!r}")


def create_process_response(
    config: Mapping[str, Any] | str | None,
) -> ProcessResponse:
    """Build a process-response model without inferring calibration."""

    kind = _kind_from(config, default="pass_through")
    if kind == "pass_through":
        return PassThroughProcessResponse()
    raise DoseConfigurationError(f"unsupported process response kind: {kind!r}")


def create_dose_encoder(config: Mapping[str, Any] | str | None) -> DoseEncoder:
    """Build the downstream dose encoder."""

    kind = _kind_from(config, default="unassigned")
    if kind == "unassigned":
        return UnassignedDoseEncoder()
    if kind == "external_recipe":
        return ExternalRecipeDoseEncoder()
    raise DoseConfigurationError(f"unsupported dose encoder kind: {kind!r}")


def resolve_dose_components(
    config: Mapping[str, Any] | None,
) -> tuple[DoseField, ProcessResponse, DoseEncoder]:
    """Resolve the three dose interfaces from one configuration block."""

    config = {} if config is None else dict(config)
    field_config = config.get("field")
    if field_config is None:
        # Keep response/encoder keys out of field parsing.  This also preserves
        # the strict self-contained schema where unassigned dose explicitly
        # carries ``value: null`` and ``unit: null``.
        field_config = {
            key: config[key]
            for key in ("kind", "value", "unit")
            if key in config
        }
    if not isinstance(field_config, Mapping):
        raise DoseConfigurationError("dose.field must be an object")
    response_config = config.get("response", config.get("response_model"))
    encoder_config = config.get("encoder")
    return (
        create_dose_field(field_config),
        create_process_response(response_config),
        create_dose_encoder(encoder_config),
    )


# Readable compatibility aliases for callers that prefer shorter names.
ScalarDose = ScalarDoseField
UnassignedDose = UnassignedDoseField
PassThroughResponse = PassThroughProcessResponse


__all__ = [
    "DoseConfigurationError",
    "DoseEncoder",
    "DoseField",
    "DoseSample",
    "ExternalRecipeDoseEncoder",
    "GeometryCorrectionContribution",
    "PassThroughProcessResponse",
    "PassThroughResponse",
    "ProcessResponse",
    "ScalarDose",
    "ScalarDoseField",
    "UnassignedDose",
    "UnassignedDoseEncoder",
    "UnassignedDoseField",
    "create_dose_encoder",
    "create_dose_field",
    "create_process_response",
    "resolve_dose_components",
]
