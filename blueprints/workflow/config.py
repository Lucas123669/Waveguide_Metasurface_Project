"""Strict, self-contained configuration contract for blueprint generation."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = 1
RELEASE_STATES = frozenset({"engineering_preview", "released"})


def _object(
    value: object,
    path: str,
    *,
    required: Sequence[str],
    optional: Sequence[str] = (),
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    required_set = set(required)
    missing = sorted(required_set.difference(value))
    if missing:
        raise ValueError(f"{path} is missing: {', '.join(missing)}")
    unknown = sorted(set(value).difference(required_set.union(optional)))
    if unknown:
        raise ValueError(f"{path} contains unknown fields: {', '.join(unknown)}")
    return value


def _string(value: object, path: str, *, allowed: set[str] | frozenset[str] | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{path} must be a non-empty string")
    resolved = value.strip()
    if allowed is not None and resolved not in allowed:
        raise ValueError(f"{path} must be one of: {', '.join(sorted(allowed))}")
    return resolved


def _number(
    value: object,
    path: str,
    *,
    positive: bool = False,
    non_negative: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} must be a number")
    resolved = float(value)
    if not math.isfinite(resolved):
        raise ValueError(f"{path} must be finite")
    if positive and resolved <= 0.0:
        raise ValueError(f"{path} must be positive")
    if non_negative and resolved < 0.0:
        raise ValueError(f"{path} must be non-negative")
    return resolved


def _integer(value: object, path: str, *, positive: bool = False) -> int:
    if type(value) is not int:
        raise TypeError(f"{path} must be an integer")
    if positive and value <= 0:
        raise ValueError(f"{path} must be positive")
    return value


def _boolean(value: object, path: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{path} must be a boolean")
    return value


def _pair(
    value: object,
    path: str,
    *,
    positive: bool = False,
) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise TypeError(f"{path} must be a two-number array")
    return (
        _number(value[0], f"{path}[0]", positive=positive),
        _number(value[1], f"{path}[1]", positive=positive),
    )


def _nullable_non_negative(value: object, path: str) -> float | None:
    if value is None:
        return None
    return _number(value, path, non_negative=True)


def _validate_cell(value: object, path: str) -> None:
    cell = _object(value, path, required=("b0_nm", "eta", "zeta"))
    _number(cell["b0_nm"], f"{path}.b0_nm", positive=True)
    _number(cell["eta"], f"{path}.eta", positive=True)
    _number(cell["zeta"], f"{path}.zeta", positive=True)


def _validate_geometry(value: object) -> None:
    geometry = _object(
        value,
        "geometry",
        required=(
            "schema_version",
            "length_unit",
            "lattice",
            "unit_cell",
            "finite",
            "cladding_shift",
        ),
    )
    if _integer(geometry["schema_version"], "geometry.schema_version") != 1:
        raise ValueError("geometry.schema_version must be 1")
    _string(geometry["length_unit"], "geometry.length_unit", allowed={"um"})

    lattice = _object(
        geometry["lattice"],
        "geometry.lattice",
        required=("kind", "period_um", "origin_um", "orientation_deg"),
    )
    _string(
        lattice["kind"],
        "geometry.lattice.kind",
        allowed={"triangular_hexagonal_v1"},
    )
    _number(lattice["period_um"], "geometry.lattice.period_um", positive=True)
    _pair(lattice["origin_um"], "geometry.lattice.origin_um")
    _number(lattice["orientation_deg"], "geometry.lattice.orientation_deg")

    unit_cell = _object(
        geometry["unit_cell"],
        "geometry.unit_cell",
        required=(
            "kind",
            "radial_reference_fraction",
            "edge_reference_nm",
            "cavity",
            "cladding",
        ),
    )
    _string(
        unit_cell["kind"],
        "geometry.unit_cell.kind",
        allowed={"six_triangular_holes_fourier_v1"},
    )
    _number(
        unit_cell["radial_reference_fraction"],
        "geometry.unit_cell.radial_reference_fraction",
        positive=True,
    )
    _number(
        unit_cell["edge_reference_nm"],
        "geometry.unit_cell.edge_reference_nm",
        positive=True,
    )
    _validate_cell(unit_cell["cavity"], "geometry.unit_cell.cavity")
    _validate_cell(unit_cell["cladding"], "geometry.unit_cell.cladding")

    finite = _object(
        geometry["finite"],
        "geometry.finite",
        required=("kind", "cavity_layers", "cladding_layers", "empty_buffer_periods"),
    )
    _string(finite["kind"], "geometry.finite.kind", allowed={"hex_shells_v1"})
    _integer(finite["cavity_layers"], "geometry.finite.cavity_layers", positive=True)
    _integer(finite["cladding_layers"], "geometry.finite.cladding_layers", positive=True)
    _number(
        finite["empty_buffer_periods"],
        "geometry.finite.empty_buffer_periods",
        non_negative=True,
    )

    shift = _object(
        geometry["cladding_shift"],
        "geometry.cladding_shift",
        required=("geometry", "profile", "x_factor", "y_factor"),
    )
    shift_geometry = _object(
        shift["geometry"],
        "geometry.cladding_shift.geometry",
        required=("kind",),
    )
    _string(
        shift_geometry["kind"],
        "geometry.cladding_shift.geometry.kind",
        allowed={"groups", "ellipse"},
    )
    profile = _object(
        shift["profile"],
        "geometry.cladding_shift.profile",
        required=("kind",),
        optional=("scale_layers", "power"),
    )
    profile_kind = _string(
        profile["kind"],
        "geometry.cladding_shift.profile.kind",
        allowed={"uniform", "tanh_power"},
    )
    if profile_kind == "uniform" and set(profile) != {"kind"}:
        raise ValueError("uniform cladding shift profile accepts only kind")
    if profile_kind == "tanh_power":
        if set(profile) != {"kind", "scale_layers", "power"}:
            raise ValueError("tanh_power profile requires scale_layers and power")
        _number(profile["scale_layers"], "geometry.cladding_shift.profile.scale_layers", positive=True)
        power = _number(
            profile["power"],
            "geometry.cladding_shift.profile.power",
        )
        if power <= 1.0:
            raise ValueError(
                "geometry.cladding_shift.profile.power must be greater than 1"
            )
    _number(shift["x_factor"], "geometry.cladding_shift.x_factor", non_negative=True)
    _number(shift["y_factor"], "geometry.cladding_shift.y_factor", non_negative=True)


def _validate_local_operator_set(value: object, path: str) -> None:
    local = _object(value, path, required=("operators",))
    operators = local["operators"]
    if not isinstance(operators, list):
        raise TypeError(f"{path}.operators must be an array")
    for index, raw in enumerate(operators):
        operator_path = f"{path}.operators[{index}]"
        if not isinstance(raw, Mapping):
            raise TypeError(f"{operator_path} must be an object")
        kind = _string(raw.get("kind"), f"{operator_path}.kind")
        if kind == "edge_offset":
            operator = _object(
                raw,
                operator_path,
                required=("kind", "value_nm", "join_style", "miter_limit"),
            )
            _number(operator["value_nm"], f"{operator_path}.value_nm")
            _string(operator["join_style"], f"{operator_path}.join_style", allowed={"miter"})
            _number(operator["miter_limit"], f"{operator_path}.miter_limit", positive=True)
        elif kind == "isotropic_scale":
            operator = _object(raw, operator_path, required=("kind", "factor"))
            _number(operator["factor"], f"{operator_path}.factor", positive=True)
        elif kind == "anisotropic_scale_xy":
            operator = _object(raw, operator_path, required=("kind", "x_factor", "y_factor", "axes"))
            _number(operator["x_factor"], f"{operator_path}.x_factor", positive=True)
            _number(operator["y_factor"], f"{operator_path}.y_factor", positive=True)
            _string(operator["axes"], f"{operator_path}.axes", allowed={"global", "local"})
        else:
            raise ValueError(f"{operator_path}.kind is not supported: {kind}")


def _validate_local_correction(value: object) -> None:
    path = "fabrication.local_correction"
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    if "operators" in value:
        local = _object(value, path, required=("operators",), optional=("by_region",))
        _validate_local_operator_set({"operators": local["operators"]}, path)
    else:
        local = _object(value, path, required=("default", "by_region"))
        _validate_local_operator_set(local["default"], f"{path}.default")
    by_region = local.get("by_region", {})
    if not isinstance(by_region, Mapping):
        raise TypeError(f"{path}.by_region must be an object")
    for region, region_value in by_region.items():
        _string(region, f"{path}.by_region key")
        _validate_local_operator_set(region_value, f"{path}.by_region.{region}")


def _validate_fabrication(value: object) -> None:
    fabrication = _object(
        value,
        "fabrication",
        required=(
            "profile_id",
            "revision",
            "provenance",
            "triangle_side_correction",
            "local_correction",
            "spatial_envelope",
            "placement_distortion",
            "grid_nm",
            "corner_strategy",
            "scale_correction_ppm",
        ),
    )
    _string(fabrication["profile_id"], "fabrication.profile_id")
    _string(fabrication["revision"], "fabrication.revision")
    _string(fabrication["provenance"], "fabrication.provenance")
    triangle = _object(
        fabrication["triangle_side_correction"],
        "fabrication.triangle_side_correction",
        required=(
            "kind",
            "global_delta_nm",
            "envelope_modulation_strength",
            "regions",
        ),
    )
    _string(
        triangle["kind"],
        "fabrication.triangle_side_correction.kind",
        allowed={"equilateral_parallel_edge_v1"},
    )
    _number(
        triangle["global_delta_nm"],
        "fabrication.triangle_side_correction.global_delta_nm",
    )
    _number(
        triangle["envelope_modulation_strength"],
        "fabrication.triangle_side_correction.envelope_modulation_strength",
        non_negative=True,
    )
    triangle_regions = triangle["regions"]
    if not isinstance(triangle_regions, list) or not triangle_regions:
        raise ValueError(
            "fabrication.triangle_side_correction.regions must be a non-empty array"
        )
    seen_triangle_regions: set[str] = set()
    for index, region in enumerate(triangle_regions):
        resolved_region = _string(
            region,
            f"fabrication.triangle_side_correction.regions[{index}]",
        )
        if resolved_region in seen_triangle_regions:
            raise ValueError(
                "fabrication.triangle_side_correction.regions must not contain duplicates"
            )
        seen_triangle_regions.add(resolved_region)
    _validate_local_correction(fabrication["local_correction"])

    envelope = _object(
        fabrication["spatial_envelope"],
        "fabrication.spatial_envelope",
        required=("kind", "target", "center_um", "half_size_um", "outside_policy", "coefficients"),
        optional=("regions",),
    )
    _string(
        envelope["kind"],
        "fabrication.spatial_envelope.kind",
        allowed={"constant", "radial_even_polynomial", "separable_even_polynomial_xy"},
    )
    _string(
        envelope["target"],
        "fabrication.spatial_envelope.target",
        allowed={"edge_offset_nm", "isotropic_scale_delta"},
    )
    _pair(envelope["center_um"], "fabrication.spatial_envelope.center_um")
    _pair(envelope["half_size_um"], "fabrication.spatial_envelope.half_size_um", positive=True)
    _string(
        envelope["outside_policy"],
        "fabrication.spatial_envelope.outside_policy",
        allowed={"error", "clip"},
    )
    regions = envelope.get("regions")
    if regions is not None:
        if not isinstance(regions, list) or not regions:
            raise ValueError(
                "fabrication.spatial_envelope.regions must be a non-empty array"
            )
        seen_regions: set[str] = set()
        for index, region in enumerate(regions):
            resolved_region = _string(
                region,
                f"fabrication.spatial_envelope.regions[{index}]",
            )
            if resolved_region in seen_regions:
                raise ValueError(
                    "fabrication.spatial_envelope.regions must not contain duplicates"
                )
            seen_regions.add(resolved_region)
    if envelope["target"] != "edge_offset_nm":
        raise ValueError(
            "fabrication.triangle_side_correction requires "
            "fabrication.spatial_envelope.target='edge_offset_nm'"
        )
    if regions != triangle_regions:
        raise ValueError(
            "fabrication.triangle_side_correction.regions must exactly match "
            "fabrication.spatial_envelope.regions"
        )

    coefficients = envelope["coefficients"]
    if not isinstance(coefficients, list) or not coefficients:
        raise ValueError("fabrication.spatial_envelope.coefficients must be a non-empty array")
    for index, coefficient in enumerate(coefficients):
        if isinstance(coefficient, list):
            if not coefficient:
                raise ValueError(f"fabrication.spatial_envelope.coefficients[{index}] must not be empty")
            for sub_index, sub_value in enumerate(coefficient):
                _number(sub_value, f"fabrication.spatial_envelope.coefficients[{index}][{sub_index}]")
        else:
            _number(coefficient, f"fabrication.spatial_envelope.coefficients[{index}]")

    distortion = _object(
        fabrication["placement_distortion"],
        "fabrication.placement_distortion",
        required=("kind",),
    )
    _string(distortion["kind"], "fabrication.placement_distortion.kind", allowed={"none"})
    _number(fabrication["grid_nm"], "fabrication.grid_nm", positive=True)
    corner = _object(
        fabrication["corner_strategy"],
        "fabrication.corner_strategy",
        required=("kind",),
    )
    _string(corner["kind"], "fabrication.corner_strategy.kind", allowed={"sharp"})
    scale = _object(
        fabrication["scale_correction_ppm"],
        "fabrication.scale_correction_ppm",
        required=("x", "y"),
    )
    _number(scale["x"], "fabrication.scale_correction_ppm.x")
    _number(scale["y"], "fabrication.scale_correction_ppm.y")


def _validate_dose(value: object) -> None:
    dose = _object(value, "dose", required=("kind", "value", "unit", "response", "encoder"))
    kind = _string(dose["kind"], "dose.kind", allowed={"unassigned", "scalar"})
    if kind == "unassigned":
        if dose["value"] is not None or dose["unit"] is not None:
            raise ValueError("unassigned dose requires null value and unit")
    else:
        _number(dose["value"], "dose.value", positive=True)
        _string(dose["unit"], "dose.unit")
    response = _object(dose["response"], "dose.response", required=("kind",))
    _string(response["kind"], "dose.response.kind", allowed={"pass_through"})
    encoder = _object(dose["encoder"], "dose.encoder", required=("kind",))
    _string(encoder["kind"], "dose.encoder.kind", allowed={"external_recipe"})


def _validate_layout(value: object) -> None:
    layout = _object(
        value,
        "layout",
        required=("rotation_deg", "mirror_x", "mirror_y", "translation_um", "polarity", "etch_layer"),
    )
    _number(layout["rotation_deg"], "layout.rotation_deg")
    _boolean(layout["mirror_x"], "layout.mirror_x")
    _boolean(layout["mirror_y"], "layout.mirror_y")
    _pair(layout["translation_um"], "layout.translation_um")
    _string(layout["polarity"], "layout.polarity", allowed={"unspecified", "clear", "dark"})
    _string(layout["etch_layer"], "layout.etch_layer")


def _validate_optional_structures(value: object, path: str) -> None:
    config = _object(value, path, required=("kind",))
    _string(config["kind"], f"{path}.kind", allowed={"none"})


def resolve_outer_window_radial_width_um(
    config: Mapping[str, Any],
    geometry: Mapping[str, Any] | None = None,
) -> float:
    """Resolve the physical window height from a fixed value or layer rule."""

    has_fixed = "radial_width_um" in config
    has_rule = "radial_width" in config
    if has_fixed == has_rule:
        raise ValueError(
            "outer_etch_windows requires exactly one of radial_width_um or radial_width"
        )
    if has_fixed:
        return _number(
            config["radial_width_um"],
            "outer_etch_windows.radial_width_um",
            positive=True,
        )

    rule = _object(
        config["radial_width"],
        "outer_etch_windows.radial_width",
        required=("kind", "slope_um_per_total_layer", "intercept_um"),
    )
    _string(
        rule["kind"],
        "outer_etch_windows.radial_width.kind",
        allowed={"linear_from_total_finite_layers_v1"},
    )
    slope = _number(
        rule["slope_um_per_total_layer"],
        "outer_etch_windows.radial_width.slope_um_per_total_layer",
        positive=True,
    )
    intercept = _number(
        rule["intercept_um"],
        "outer_etch_windows.radial_width.intercept_um",
    )
    if geometry is None:
        raise ValueError(
            "geometry is required to resolve outer_etch_windows.radial_width"
        )
    finite = geometry.get("finite")
    if not isinstance(finite, Mapping):
        raise TypeError("geometry.finite must be an object")
    cavity_layers = _integer(
        finite.get("cavity_layers"),
        "geometry.finite.cavity_layers",
        positive=True,
    )
    cladding_layers = _integer(
        finite.get("cladding_layers"),
        "geometry.finite.cladding_layers",
        positive=True,
    )
    radial_width = slope * (cavity_layers + cladding_layers) + intercept
    if not math.isfinite(radial_width) or radial_width <= 0.0:
        raise ValueError(
            "outer_etch_windows.radial_width resolves to a non-positive height"
        )
    return radial_width


def _validate_outer_etch_windows(
    value: object,
    geometry: Mapping[str, Any],
) -> None:
    path = "outer_etch_windows"
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    kind = _string(value.get("kind"), f"{path}.kind")
    if kind == "none":
        _object(value, path, required=("kind",))
        return

    if kind == "segmented_hex_etch_windows_v1":
        config = _object(
            value,
            path,
            required=(
                "kind",
                "reference",
                "inner_clearance_um",
                "radial_width_um",
                "inner_end_clearance_um",
                "outer_tangential_extension_um",
                "corner_radius_um",
                "arc_segments_per_quadrant",
                "dxf_layer",
            ),
        )
        _string(
            config["kind"],
            f"{path}.kind",
            allowed={"segmented_hex_etch_windows_v1"},
        )
        _string(config["reference"], f"{path}.reference", allowed={"finite_boundary"})
        _number(config["inner_clearance_um"], f"{path}.inner_clearance_um", positive=True)
        _number(config["radial_width_um"], f"{path}.radial_width_um", positive=True)
        _number(
            config["inner_end_clearance_um"],
            f"{path}.inner_end_clearance_um",
            non_negative=True,
        )
        _number(
            config["outer_tangential_extension_um"],
            f"{path}.outer_tangential_extension_um",
            non_negative=True,
        )
        _number(config["corner_radius_um"], f"{path}.corner_radius_um", non_negative=True)
    elif kind == "segmented_hex_ring_windows_v2":
        config = _object(
            value,
            path,
            required=(
                "kind",
                "reference",
                "inner_clearance_um",
                "parallel_side_gap_um",
                "inner_corner_radius_um",
                "arc_segments_per_quadrant",
                "dxf_layer",
            ),
            optional=("radial_width_um", "radial_width"),
        )
        _string(
            config["kind"],
            f"{path}.kind",
            allowed={"segmented_hex_ring_windows_v2"},
        )
        _string(config["reference"], f"{path}.reference", allowed={"finite_boundary"})
        _number(
            config["inner_clearance_um"],
            f"{path}.inner_clearance_um",
            non_negative=True,
        )
        resolve_outer_window_radial_width_um(config, geometry)
        _number(
            config["parallel_side_gap_um"],
            f"{path}.parallel_side_gap_um",
            positive=True,
        )
        _number(
            config["inner_corner_radius_um"],
            f"{path}.inner_corner_radius_um",
            non_negative=True,
        )
    else:
        _string(
            kind,
            f"{path}.kind",
            allowed={
                "segmented_hex_etch_windows_v1",
                "segmented_hex_ring_windows_v2",
            },
        )
        raise AssertionError("unreachable")

    _integer(
        config["arc_segments_per_quadrant"],
        f"{path}.arc_segments_per_quadrant",
        positive=True,
    )
    _string(config["dxf_layer"], f"{path}.dxf_layer")

def _validate_markers(value: object) -> None:
    path = "markers"
    if not isinstance(value, Mapping):
        raise TypeError(f"{path} must be an object")
    kind = _string(value.get("kind"), f"{path}.kind")
    if kind == "none":
        _object(value, path, required=("kind",))
        return
    config = _object(
        value,
        path,
        required=(
            "kind",
            "source",
            "anchor",
            "center_x_um",
            "top_clearance_um",
            "digit_height_um",
            "digit_width_um",
            "segment_thickness_um",
            "segment_gap_um",
            "segment_bevel_um",
            "digit_spacing_um",
            "decimal_size_um",
            "decimal_gap_um",
            "value_spacing_um",
            "group_spacing_um",
            "dash_length_um",
            "dash_thickness_um",
            "b0_decimals",
            "eta_decimals",
            "zeta_max_decimals",
            "trim_zeta_trailing_zeros",
            "dxf_layer",
        ),
    )
    _string(
        config["kind"],
        f"{path}.kind",
        allowed={"seven_segment_parameter_label_v1"},
    )
    _string(
        config["source"],
        f"{path}.source",
        allowed={"geometry.unit_cell.cavity_cladding"},
    )
    _string(
        config["anchor"],
        f"{path}.anchor",
        allowed={"below_outer_etch_windows", "below_finite_boundary"},
    )
    _number(config["center_x_um"], f"{path}.center_x_um")
    for field in (
        "top_clearance_um",
        "digit_height_um",
        "digit_width_um",
        "segment_thickness_um",
        "decimal_size_um",
        "dash_length_um",
        "dash_thickness_um",
    ):
        _number(config[field], f"{path}.{field}", positive=True)
    for field in (
        "segment_gap_um",
        "segment_bevel_um",
        "digit_spacing_um",
        "decimal_gap_um",
        "value_spacing_um",
        "group_spacing_um",
    ):
        _number(config[field], f"{path}.{field}", non_negative=True)
    for field in ("b0_decimals", "eta_decimals", "zeta_max_decimals"):
        decimals = _integer(config[field], f"{path}.{field}")
        if decimals < 0:
            raise ValueError(f"{path}.{field} must be non-negative")
    _boolean(config["trim_zeta_trailing_zeros"], f"{path}.trim_zeta_trailing_zeros")
    _string(config["dxf_layer"], f"{path}.dxf_layer")


def _validate_drc(value: object) -> None:
    drc = _object(
        value,
        "drc",
        required=(
            "min_hole_width_nm",
            "min_edge_nm",
            "min_bridge_nm",
            "boundary_clearance_nm",
            "fail_on_warning",
        ),
    )
    for key in ("min_hole_width_nm", "min_edge_nm", "min_bridge_nm", "boundary_clearance_nm"):
        _nullable_non_negative(drc[key], f"drc.{key}")
    _boolean(drc["fail_on_warning"], "drc.fail_on_warning")


def _validate_export(value: object) -> None:
    export = _object(
        value,
        "export",
        required=(
            "mode",
            "dxf_version",
            "flatten",
            "output_root",
            "overwrite",
            "debug_artifacts",
            "dpi",
            "preview_layout",
        ),
    )
    _string(export["mode"], "export.mode", allowed=RELEASE_STATES)
    _string(export["dxf_version"], "export.dxf_version", allowed={"R2010"})
    if not _boolean(export["flatten"], "export.flatten"):
        raise ValueError("export.flatten must be true in v1")
    _string(export["output_root"], "export.output_root")
    _boolean(export["overwrite"], "export.overwrite")
    if _boolean(export["debug_artifacts"], "export.debug_artifacts"):
        raise ValueError("export.debug_artifacts=true is not supported in v1")
    _integer(export["dpi"], "export.dpi", positive=True)
    _string(
        export["preview_layout"],
        "export.preview_layout",
        allowed={
            "radial_three_position_correction_v2",
            "radial_three_position_correction_compact_v3",
            "radial_three_position_correction_compact_wide_v4",
        },
    )


def _validate_release_gate(data: Mapping[str, Any]) -> None:
    status = data["project"]["release_status"]
    if status != data["export"]["mode"]:
        raise ValueError("project.release_status must equal export.mode")
    if status != "released":
        return
    fabrication = data["fabrication"]
    for key in ("profile_id", "revision", "provenance"):
        normalized = str(fabrication[key]).strip().lower()
        if (
            normalized in {"unassigned", "unknown", "none"}
            or "unassigned" in normalized
        ):
            raise ValueError(f"released configuration requires calibrated fabrication.{key}")
    if data["dose"]["kind"] != "scalar":
        raise ValueError("released configuration requires an assigned scalar dose in v1")
    if data["layout"]["polarity"] == "unspecified":
        raise ValueError("released configuration requires explicit layout.polarity")
    for key, value in data["drc"].items():
        if key != "fail_on_warning" and value is None:
            raise ValueError(f"released configuration requires drc.{key}")


def _validate_source_trace(value: object) -> None:
    if value is None:
        return
    trace = _object(value, "source_trace", required=("kind", "path", "sha256"))
    _string(trace["kind"], "source_trace.kind")
    _string(trace["path"], "source_trace.path")
    digest = _string(trace["sha256"], "source_trace.sha256")
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest.lower()):
        raise ValueError("source_trace.sha256 must be a 64-character hexadecimal digest")


def _validate_root(data: object) -> Mapping[str, Any]:
    root = _object(
        data,
        "parameter.json",
        required=(
            "schema_version",
            "project",
            "geometry",
            "fabrication",
            "dose",
            "layout",
            "die",
            "outer_etch_windows",
            "markers",
            "drc",
            "export",
            "source_trace",
        ),
    )
    if _integer(root["schema_version"], "schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    project = _object(root["project"], "project", required=("name", "release_status"))
    _string(project["name"], "project.name")
    _string(project["release_status"], "project.release_status", allowed=RELEASE_STATES)
    _validate_geometry(root["geometry"])
    _validate_fabrication(root["fabrication"])
    _validate_dose(root["dose"])
    _validate_layout(root["layout"])
    _validate_optional_structures(root["die"], "die")
    _validate_outer_etch_windows(root["outer_etch_windows"], root["geometry"])
    _validate_markers(root["markers"])
    _validate_drc(root["drc"])
    _validate_export(root["export"])
    _validate_source_trace(root["source_trace"])
    _validate_release_gate(root)
    return root


@dataclass(frozen=True)
class BlueprintConfig:
    """Validated blueprint configuration and its immutable source identity."""

    path: Path
    data: Mapping[str, Any]
    source_sha256: str

    @property
    def release_status(self) -> str:
        return str(self.data["project"]["release_status"])

    @property
    def is_released(self) -> bool:
        return self.release_status == "released"

    @property
    def output_root(self) -> Path:
        configured = Path(str(self.data["export"]["output_root"]))
        if configured.is_absolute():
            resolved = configured.resolve()
        else:
            resolved = (self.path.parent / configured).resolve()
        project_root = self.path.parent.resolve()
        if not resolved.is_relative_to(project_root):
            raise ValueError("export.output_root must stay inside the blueprints project")
        return resolved

    @property
    def identity_sha256(self) -> str:
        payload = {
            key: self.data[key]
            for key in (
                "schema_version",
                "geometry",
                "fabrication",
                "dose",
                "layout",
                "die",
                "outer_etch_windows",
                "markers",
                "drc",
            )
        }
        payload["artifact_export"] = {
            key: self.data["export"][key]
            for key in ("mode", "dxf_version", "flatten", "dpi", "preview_layout")
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return sha256(encoded).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.data))


def load_blueprint_config(path: str | Path) -> BlueprintConfig:
    """Load a strict standard-JSON blueprint configuration."""
    resolved = Path(path).resolve()
    raw = resolved.read_bytes()
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"blueprint parameter file must be UTF-8: {resolved}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"blueprint parameter file is not valid JSON: {resolved}: {exc}") from exc
    data = _validate_root(parsed)
    config = BlueprintConfig(
        path=resolved,
        data=dict(data),
        source_sha256=sha256(raw).hexdigest(),
    )
    _ = config.output_root
    return config
