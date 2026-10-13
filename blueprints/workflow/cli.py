"""Command-line orchestration for the standalone blueprint pipeline."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as package_version
import os
from pathlib import Path
import shutil
import sys
import tempfile
from time import perf_counter
from typing import Any, Mapping, Sequence
from uuid import uuid4

from .geometry.auxiliary import add_auxiliary_geometry
from .config import BlueprintConfig, load_blueprint_config
from .fabrication.corrections import apply_corrections
from .quality.drc import DrcReport, run_drc
from .output.dxf import write_dxf
from .geometry import build_hex_layout
from .models import LayoutPlan
from .output.reporting import (
    blueprint_source_provenance,
    case_name,
    dxf_artifact_name,
    file_sha256,
    write_json,
)


REPORT_SCHEMA_VERSION = 1
BLUEPRINT_PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class GenerationResult:
    case_name: str
    case_dir: Path | None
    feature_count: int
    drc: DrcReport
    output_files: tuple[str, ...]
    preflight_only: bool


def _package_versions() -> dict[str, str]:
    result = {"python": sys.version.split()[0]}
    for package in ("microfab-blueprints", "numpy", "shapely", "ezdxf", "matplotlib"):
        try:
            result[package] = package_version(package)
        except PackageNotFoundError:
            result[package] = "unknown"
    return result


def _source_trace_status(config: BlueprintConfig) -> dict[str, Any] | None:
    trace = config.data.get("source_trace")
    if trace is None:
        return None
    source_path = (config.path.parent / str(trace["path"])).resolve()
    result: dict[str, Any] = {
        "kind": trace["kind"],
        "configured_path": trace["path"],
        "expected_sha256": trace["sha256"],
        "exists_at_generation": source_path.is_file(),
    }
    if source_path.is_file():
        actual = file_sha256(source_path)
        result["actual_sha256"] = actual
        result["hash_matches"] = actual.lower() == str(trace["sha256"]).lower()
    else:
        result["hash_matches"] = None
    return result


def _drc_config(config: BlueprintConfig) -> dict[str, Any]:
    resolved = {
        key: value
        for key, value in config.data["drc"].items()
        if value is not None
    }
    resolved["grid_nm"] = config.data["fabrication"]["grid_nm"]
    resolved["allowed_dxf_layers"] = [config.data["layout"]["etch_layer"]]
    return resolved


def _layout_summary(layout: LayoutPlan) -> dict[str, Any]:
    region_counts: dict[str, int] = {}
    for feature in layout.features:
        region_counts[feature.region] = region_counts.get(feature.region, 0) + 1
    summary = {
        "geometry_kind": layout.geometry_kind,
        "feature_count": layout.feature_count,
        "region_counts": region_counts,
        "bounds_um": list(layout.bounds) if layout.bounds is not None else None,
        "boundary_bounds_um": (
            list(layout.boundary.bounds) if layout.boundary is not None else None
        ),
    }
    auxiliary = layout.metadata.get("auxiliary_geometry")
    if isinstance(auxiliary, Mapping):
        summary["auxiliary_geometry"] = dict(auxiliary)
    return summary


def _correction_summary(layout: LayoutPlan) -> dict[str, Any]:
    edge_offsets: list[float] = []
    scale_factors: list[float] = []
    envelope_values: list[float] = []
    snap_values: list[float] = []
    dose_assigned: set[bool] = set()
    dose_values: set[tuple[object, object]] = set()
    for feature in layout.features:
        item = feature.metadata.get("correction")
        if not isinstance(item, Mapping):
            continue
        effective = item.get("effective", {})
        envelope = item.get("envelope", {})
        dose = item.get("dose", {})
        if isinstance(effective, Mapping):
            if "edge_offset_um" in effective:
                edge_offsets.append(float(effective["edge_offset_um"]))
            if "isotropic_scale" in effective:
                scale_factors.append(float(effective["isotropic_scale"]))
        if isinstance(envelope, Mapping) and "value" in envelope:
            envelope_values.append(float(envelope["value"]))
        if isinstance(dose, Mapping):
            dose_assigned.add(bool(dose.get("assigned", False)))
            dose_values.add((dose.get("value"), dose.get("unit")))
        snap_values.append(float(item.get("grid_snap_max_displacement_um", 0.0)))

    def value_range(values: Sequence[float]) -> list[float] | None:
        return [min(values), max(values)] if values else None

    pipeline = layout.metadata.get("correction_pipeline", {})
    return {
        "pipeline": pipeline,
        "effective_edge_offset_range_um": value_range(edge_offsets),
        "effective_isotropic_scale_range": value_range(scale_factors),
        "envelope_value_range": value_range(envelope_values),
        "grid_snap_max_displacement_um": max(snap_values, default=0.0),
        "dose_assigned_states": sorted(dose_assigned),
        "dose_values": [
            {"value": value, "unit": unit}
            for value, unit in sorted(dose_values, key=lambda item: str(item))
        ],
    }


def _preview_summary(
    correction: Mapping[str, Any],
    fabrication: Mapping[str, Any],
    dose: Mapping[str, Any],
    drc: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        'triangle_side_correction': dict(
            fabrication['triangle_side_correction']
        ),
        "spatial_envelope": dict(fabrication["spatial_envelope"]),
        "fabrication": {
            "local_correction": dict(fabrication["local_correction"]),
            "corner_strategy": dict(fabrication["corner_strategy"]),
        },
        "correction": {
            "edge_offset_range_um": correction["effective_edge_offset_range_um"],
            "isotropic_scale_range": correction["effective_isotropic_scale_range"],
            "envelope_value_range": correction["envelope_value_range"],
            "max_grid_snap_um": correction["grid_snap_max_displacement_um"],
        },
        "dose": {
            "kind": dose["kind"],
            "value": dose["value"],
            "unit": dose["unit"],
            "response": dose["response"]["kind"],
            "encoder": dose["encoder"]["kind"],
        },
        "drc": {
            "passed": drc["passed"],
            "errors": drc["error_count"],
            "warnings": drc["warning_count"],
            "metrics": drc["metrics"],
        },
    }


def _clean_staging(path: Path, output_root: Path) -> None:
    if not path.exists():
        return
    resolved = path.resolve()
    root = output_root.resolve()
    if resolved.parent != root or not resolved.name.startswith(".staging-"):
        raise RuntimeError(f"refusing to clean unexpected staging path: {resolved}")
    shutil.rmtree(resolved)


def _path_exists(path: Path) -> bool:
    """Treat broken symlinks as existing output targets."""

    return path.exists() or path.is_symlink()


def _validate_staging_contents(staging: Path, expected_names: set[str]) -> None:
    entries = list(staging.iterdir())
    actual_names = {entry.name for entry in entries}
    non_regular = sorted(
        entry.name
        for entry in entries
        if not entry.is_file() or entry.is_symlink()
    )
    if (
        len(entries) != len(expected_names)
        or actual_names != expected_names
        or non_regular
    ):
        raise RuntimeError(
            "staging output contract mismatch: "
            f"expected regular files {sorted(expected_names)}, "
            f"found entries {sorted(actual_names)}, "
            f"non-regular entries {non_regular}"
        )


def _finalize_staging(
    staging: Path,
    target: Path,
    expected_names: set[str],
) -> None:
    _validate_staging_contents(staging, expected_names)
    if _path_exists(target):
        raise FileExistsError(f"blueprint output already exists: {target}")
    staging.rename(target)


def _config_report(config: BlueprintConfig) -> dict[str, Any]:
    return {
        "path": config.path.name,
        "source_sha256": config.source_sha256,
        "identity_sha256": config.identity_sha256,
        "resolved": config.to_dict(),
        "source_trace_status": _source_trace_status(config),
    }


def generate_blueprint(
    config: BlueprintConfig,
    *,
    preflight_only: bool = False,
) -> GenerationResult:
    """Build, correct, validate, and optionally serialize one layout case."""

    timings: dict[str, float] = {}
    started = perf_counter()
    nominal = build_hex_layout(config.data["geometry"])
    timings["build_nominal_s"] = perf_counter() - started

    started = perf_counter()
    nominal = add_auxiliary_geometry(
        nominal,
        geometry=config.data["geometry"],
        outer_etch_windows=config.data["outer_etch_windows"],
        markers=config.data["markers"],
    )
    timings["build_auxiliary_geometry_s"] = perf_counter() - started

    started = perf_counter()
    corrected = apply_corrections(
        nominal,
        config.data["fabrication"],
        config.data["dose"],
        config.data["layout"],
    )
    timings["apply_corrections_s"] = perf_counter() - started

    started = perf_counter()
    drc = run_drc(corrected, _drc_config(config))
    timings["drc_s"] = perf_counter() - started

    resolved_case_name = case_name(config.data, config.identity_sha256)
    if preflight_only:
        return GenerationResult(
            case_name=resolved_case_name,
            case_dir=None,
            feature_count=corrected.feature_count,
            drc=drc,
            output_files=(),
            preflight_only=True,
        )

    output_root = config.output_root
    output_root.mkdir(parents=True, exist_ok=True)
    target = output_root / resolved_case_name
    if _path_exists(target):
        raise FileExistsError(f"blueprint output already exists: {target}")
    if config.data["export"]["overwrite"]:
        raise ValueError("export.overwrite=true is not supported in v1; use a new revision")
    staging = output_root / (
        f".s-{config.identity_sha256[:8]}-{uuid4().hex[:8]}"
    )
    staging.mkdir(parents=False, exist_ok=False)

    dxf_name = dxf_artifact_name(config.data, config.identity_sha256)
    preview_name = "preview.png"
    report_name = "layout_report.json"
    dxf_report: dict[str, Any] | None = None
    try:
        correction_report = _correction_summary(corrected)
        drc_report = drc.to_dict()
        if drc.passed:
            started = perf_counter()
            dxf_report = write_dxf(
                corrected,
                staging / dxf_name,
                version=str(config.data["export"]["dxf_version"]),
            )
            timings["write_and_readback_dxf_s"] = perf_counter() - started

        started = perf_counter()
        with tempfile.TemporaryDirectory(prefix="blueprints-mpl-") as mpl_dir:
            previous = os.environ.get("MPLCONFIGDIR")
            os.environ["MPLCONFIGDIR"] = mpl_dir
            try:
                from .output.preview import save_preview

                save_preview(
                    nominal,
                    corrected,
                    _preview_summary(
                        correction_report,
                        config.data["fabrication"],
                        config.data["dose"],
                        drc_report,
                    ),
                    staging / preview_name,
                    dpi=int(config.data["export"]["dpi"]),
                )
            finally:
                if previous is None:
                    os.environ.pop("MPLCONFIGDIR", None)
                else:
                    os.environ["MPLCONFIGDIR"] = previous
        timings["write_preview_s"] = perf_counter() - started

        output_hashes: dict[str, str] = {
            preview_name: file_sha256(staging / preview_name),
        }
        if dxf_report is not None:
            output_hashes[dxf_name] = file_sha256(staging / dxf_name)

        artifact_names = {preview_name, report_name}
        if dxf_report is not None:
            artifact_names.add(dxf_name)

        report = {
            "report_schema_version": REPORT_SCHEMA_VERSION,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "case_name": resolved_case_name,
            "release_status": config.release_status,
            "config": _config_report(config),
            "software": {
                "packages": _package_versions(),
                "blueprint_source": blueprint_source_provenance(
                    BLUEPRINT_PROJECT_ROOT
                ),
            },
            "nominal_layout": _layout_summary(nominal),
            "corrected_layout": _layout_summary(corrected),
            "correction": correction_report,
            "dose": config.data["dose"],
            "drc": drc_report,
            "dxf": dxf_report,
            "outputs": {
                "artifact_count": len(artifact_names),
                "artifact_names": sorted(artifact_names),
                "sha256": output_hashes,
                "sha256_exclusions": {
                    report_name: "self-referential artifact",
                },
            },
            "timings_seconds": timings,
        }
        write_json(staging / report_name, report)

        _finalize_staging(staging, target, artifact_names)
    except BaseException:
        _clean_staging(staging, output_root)
        raise

    return GenerationResult(
        case_name=resolved_case_name,
        case_dir=target,
        feature_count=corrected.feature_count,
        drc=drc,
        output_files=tuple(sorted(artifact_names)),
        preflight_only=False,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a corrected microfabrication DXF blueprint without COMSOL."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=BLUEPRINT_PROJECT_ROOT / "main" / "parameter.json",
        help="Path to the self-contained blueprint parameter.json.",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Build, correct, and run DRC without writing output files.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_blueprint_config(args.config)
    result = generate_blueprint(config, preflight_only=args.preflight_only)
    print(f"case: {result.case_name}")
    print(f"features: {result.feature_count}")
    print(
        "DRC: "
        f"passed={result.drc.passed}, errors={result.drc.error_count}, "
        f"warnings={result.drc.warning_count}"
    )
    if result.preflight_only:
        print("output: preflight only; no files written")
    else:
        print(f"output: {result.case_dir}")
        print("files: " + ", ".join(result.output_files))
    return 0 if result.drc.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
