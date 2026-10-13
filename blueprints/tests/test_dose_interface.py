from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from blueprint_core.fabrication.dose import (
    DoseConfigurationError,
    ExternalRecipeDoseEncoder,
    PassThroughProcessResponse,
    ScalarDoseField,
    UnassignedDoseEncoder,
    UnassignedDoseField,
    create_dose_encoder,
    create_dose_field,
    create_process_response,
    resolve_dose_components,
)
from blueprint_core.models import LayoutFeature


def _feature() -> LayoutFeature:
    polygon = Polygon([(0, 0), (1, 0), (0, 1)])
    return LayoutFeature(
        "cavity/0/0/0/0",
        "cavity",
        0,
        0,
        0,
        0,
        0,
        polygon,
        polygon,
        (0.0, 0.0),
    )


def test_explicit_unassigned_dose_accepts_null_value_and_unit() -> None:
    field, response, encoder = resolve_dose_components(
        {
            "kind": "unassigned",
            "value": None,
            "unit": None,
            "response": {"kind": "pass_through"},
            "encoder": {"kind": "external_recipe"},
        }
    )
    assert isinstance(field, UnassignedDoseField)
    assert isinstance(response, PassThroughProcessResponse)
    assert isinstance(encoder, ExternalRecipeDoseEncoder)
    sample = field.evaluate((0.0, 0.0), _feature())
    assert sample.to_dict()["assigned"] is False
    assert sample.value is None


def test_scalar_dose_is_identity_bearing_but_pass_through_changes_no_geometry() -> None:
    field = ScalarDoseField(275.0, "uC/cm^2")
    sample = field.evaluate((2.0, 3.0), _feature())
    contribution = PassThroughProcessResponse().evaluate(
        sample, (2.0, 3.0), _feature(), {"profile_id": "test"}
    )
    assert field.identity() == {"kind": "scalar", "value": 275.0, "unit": "uC/cm^2"}
    assert sample.assigned is True
    assert contribution.edge_offset_um == 0.0
    assert contribution.isotropic_scale_delta == 0.0


@pytest.mark.parametrize(
    "config",
    [
        {"kind": "scalar", "value": 100.0},
        {"kind": "scalar", "value": -1.0, "unit": "uC/cm^2"},
        {"kind": "unassigned", "value": 100.0, "unit": None},
    ],
)
def test_invalid_dose_contracts_are_rejected(config: dict[str, object]) -> None:
    with pytest.raises(DoseConfigurationError):
        create_dose_field(config)


def test_unsupported_response_and_encoder_are_not_guessed() -> None:
    with pytest.raises(DoseConfigurationError, match="unsupported process response"):
        create_process_response({"kind": "linear_unvalidated"})
    with pytest.raises(DoseConfigurationError, match="unsupported dose encoder"):
        create_dose_encoder({"kind": "layer_bucket_unvalidated"})


def test_external_recipe_encoder_preserves_layer() -> None:
    feature = _feature()
    sample = ScalarDoseField(250.0, "uC/cm^2").evaluate((0.0, 0.0), feature)
    assert ExternalRecipeDoseEncoder().encode_layer("ETCH", sample, feature) == "ETCH"
    with pytest.raises(DoseConfigurationError, match="encoder is unassigned"):
        UnassignedDoseEncoder().encode_layer("ETCH", sample, feature)
