"""Derive a radial triangular-hole layout correction from SEM measurements."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import median
from typing import Sequence
from uuid import uuid4

import numpy as np


LAYER_COLUMN = "层数_外向内"
MEAN_COLUMN = "平均值_nm"
TRIMMED_MEAN_COLUMN = "去极值平均_nm"
TRIANGLE_COLUMNS = tuple(f"三角形{index}_nm" for index in range(1, 7))
REQUIRED_COLUMNS = (LAYER_COLUMN, *TRIANGLE_COLUMNS, MEAN_COLUMN, TRIMMED_MEAN_COLUMN)
FIT_KIND = "radial_even_polynomial"
SIDE_TO_EDGE_OFFSET = 2.0 * math.sqrt(3.0)


@dataclass(frozen=True, slots=True)
class SemLayerMeasurement:
    """Validated SEM samples for one outside-to-inside layer."""

    layer_outside_in: int
    samples_nm: tuple[float, ...]
    mean_nm: float
    trimmed_mean_nm: float


@dataclass(frozen=True, slots=True)
class SemCorrectionProfile:
    """Complete shell profile plus a smooth radial-even-polynomial fit."""

    rows: tuple[dict[str, object], ...]
    reference_sem_nm: float
    target_cd_nm: float
    coefficients_nm: tuple[float, ...]
    fit_rmse_edge_offset_nm: float
    fit_max_abs_edge_offset_nm: float
    source_sha256: str
    total_shells: int
    period_um: float
    reference_min_layer: int
    process_gain: float


def _finite_float(value: str, *, field: str, row_number: int) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {row_number}: {field} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"row {row_number}: {field} must be finite")
    return result


def _recalculate_trimmed_mean(samples_nm: Sequence[float]) -> float:
    ordered = sorted(float(value) for value in samples_nm)
    if len(ordered) >= 4:
        return float(sum(ordered[1:-1]) / (len(ordered) - 2))
    if len(ordered) == 3:
        return float(ordered[1])
    return float(sum(ordered) / len(ordered))


def read_sem_measurements(path: str | Path) -> tuple[SemLayerMeasurement, ...]:
    """Read and validate the Chinese-column SEM CSV contract."""

    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("SEM CSV must contain a header row")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"SEM CSV is missing required columns: {missing}")

        measurements: list[SemLayerMeasurement] = []
        seen_layers: set[int] = set()
        for row_number, raw in enumerate(reader, start=2):
            layer_value = _finite_float(
                raw[LAYER_COLUMN], field=LAYER_COLUMN, row_number=row_number
            )
            layer = int(layer_value)
            if layer_value != layer or layer <= 0:
                raise ValueError(
                    f"row {row_number}: {LAYER_COLUMN} must be a positive integer"
                )
            if layer in seen_layers:
                raise ValueError(f"row {row_number}: duplicate layer {layer}")
            seen_layers.add(layer)

            samples = tuple(
                _finite_float(raw[name], field=name, row_number=row_number)
                for name in TRIANGLE_COLUMNS
                if raw.get(name, "").strip()
            )
            if len(samples) < 3 or any(value <= 0.0 for value in samples):
                raise ValueError(
                    f"row {row_number}: at least three positive triangle samples are required"
                )
            calculated_mean = float(sum(samples) / len(samples))
            calculated_trimmed = _recalculate_trimmed_mean(samples)
            supplied_mean = _finite_float(
                raw[MEAN_COLUMN], field=MEAN_COLUMN, row_number=row_number
            )
            supplied_trimmed = _finite_float(
                raw[TRIMMED_MEAN_COLUMN],
                field=TRIMMED_MEAN_COLUMN,
                row_number=row_number,
            )
            if not math.isclose(supplied_mean, calculated_mean, abs_tol=0.11):
                raise ValueError(
                    f"row {row_number}: supplied mean differs from raw samples"
                )
            if not math.isclose(supplied_trimmed, calculated_trimmed, abs_tol=1e-6):
                raise ValueError(
                    f"row {row_number}: supplied trimmed mean differs from raw samples"
                )
            measurements.append(
                SemLayerMeasurement(
                    layer_outside_in=layer,
                    samples_nm=samples,
                    mean_nm=supplied_mean,
                    trimmed_mean_nm=supplied_trimmed,
                )
            )

    measurements.sort(key=lambda item: item.layer_outside_in)
    if not measurements or measurements[0].layer_outside_in != 1:
        raise ValueError("SEM profile must include the outermost layer 1")
    return tuple(measurements)


def evaluate_radial_even_polynomial(
    normalized_radius: float | np.ndarray,
    coefficients_nm: Sequence[float],
) -> float | np.ndarray:
    """Evaluate ``sum(c[k] * rho**(2*k))`` in nanometres."""

    radius = np.asarray(normalized_radius, dtype=float)
    result = np.zeros_like(radius)
    for order, coefficient in enumerate(coefficients_nm):
        result += float(coefficient) * radius ** (2 * order)
    if result.ndim == 0:
        return float(result)
    return result


def derive_sem_correction_profile(
    measurements: Sequence[SemLayerMeasurement],
    *,
    total_shells: int,
    period_um: float,
    target_cd_nm: float,
    reference_min_layer: int,
    fit_order: int,
    process_gain: float,
    source_sha256: str,
) -> SemCorrectionProfile:
    """Build the complete relative correction table and smooth fit."""

    if type(total_shells) is not int or total_shells <= 0:
        raise ValueError("total_shells must be a positive integer")
    if not math.isfinite(period_um) or period_um <= 0.0:
        raise ValueError("period_um must be finite and positive")
    if not math.isfinite(target_cd_nm) or target_cd_nm <= 0.0:
        raise ValueError("target_cd_nm must be finite and positive")
    if type(reference_min_layer) is not int or not 1 <= reference_min_layer <= total_shells:
        raise ValueError("reference_min_layer must lie within the finite layout")
    if type(fit_order) is not int or fit_order < 1:
        raise ValueError("fit_order must be a positive integer")
    if not math.isfinite(process_gain) or process_gain <= 0.0:
        raise ValueError("process_gain must be finite and positive")
    if not measurements:
        raise ValueError("measurements must not be empty")

    by_layer = {item.layer_outside_in: item for item in measurements}
    measured_layers = np.asarray(sorted(by_layer), dtype=int)
    if measured_layers[-1] > total_shells:
        raise ValueError("SEM layer index exceeds configured total_shells")
    reference_values = [
        item.trimmed_mean_nm
        for item in measurements
        if item.layer_outside_in >= reference_min_layer
    ]
    if len(reference_values) < 3:
        raise ValueError("reference region must contain at least three measured layers")
    reference_sem_nm = float(median(reference_values))

    measured_profile = np.asarray(
        [by_layer[int(layer)].trimmed_mean_nm for layer in measured_layers],
        dtype=float,
    )
    measured_parent_shell = total_shells + 1 - measured_layers
    measured_radius = measured_parent_shell / float(total_shells)
    measured_side_compensation = (target_cd_nm - measured_profile) / process_gain
    measured_edge_offset = measured_side_compensation / SIDE_TO_EDGE_OFFSET
    center_offset_nm = (
        (target_cd_nm - reference_sem_nm)
        / process_gain
        / SIDE_TO_EDGE_OFFSET
    )

    design_matrix = np.column_stack(
        [measured_radius ** (2 * order) for order in range(1, fit_order + 1)]
    )
    fitted_nonconstant, *_ = np.linalg.lstsq(
        design_matrix, measured_edge_offset - center_offset_nm, rcond=None
    )
    coefficients_nm = (
        center_offset_nm,
        *(float(value) for value in fitted_nonconstant),
    )
    measured_fitted = np.asarray(
        evaluate_radial_even_polynomial(measured_radius, coefficients_nm), dtype=float
    )
    fit_residual = measured_fitted - measured_edge_offset
    fit_rmse = float(np.sqrt(np.mean(fit_residual**2)))
    fit_max_abs = float(np.max(np.abs(fit_residual)))

    maximum_measured_layer = int(measured_layers[-1])
    rows: list[dict[str, object]] = []
    for layer in range(1, total_shells + 1):
        parent_shell = total_shells + 1 - layer
        normalized_radius = parent_shell / float(total_shells)
        measurement = by_layer.get(layer)
        if measurement is not None:
            status = "measured"
            sample_count = len(measurement.samples_nm)
            raw_mean: float | None = measurement.mean_nm
            raw_trimmed: float | None = measurement.trimmed_mean_nm
            profile_sem_nm = measurement.trimmed_mean_nm
        elif layer <= maximum_measured_layer:
            status = "interpolated"
            sample_count = 0
            raw_mean = None
            raw_trimmed = None
            profile_sem_nm = float(
                np.interp(layer, measured_layers, measured_profile)
            )
        else:
            status = "inner_reference_hold"
            sample_count = 0
            raw_mean = None
            raw_trimmed = None
            profile_sem_nm = reference_sem_nm

        tabulated_side = (target_cd_nm - profile_sem_nm) / process_gain
        tabulated_edge = tabulated_side / SIDE_TO_EDGE_OFFSET
        fitted_edge = float(
            evaluate_radial_even_polynomial(normalized_radius, coefficients_nm)
        )
        fitted_side = fitted_edge * SIDE_TO_EDGE_OFFSET
        predicted_corrected = profile_sem_nm + process_gain * fitted_side
        rows.append(
            {
                "layer_outside_in": layer,
                "parent_shell": parent_shell,
                "normalized_shell_radius": normalized_radius,
                "data_status": status,
                "sample_count": sample_count,
                "sem_mean_nm": raw_mean,
                "sem_trimmed_mean_nm": raw_trimmed,
                "sem_profile_nm": profile_sem_nm,
                "reference_sem_nm": reference_sem_nm,
                "target_cd_nm": target_cd_nm,
                "relative_sem_bias_nm": profile_sem_nm - target_cd_nm,
                "tabulated_side_compensation_nm": tabulated_side,
                "tabulated_edge_offset_nm": tabulated_edge,
                "recommended_edge_offset_nm": fitted_edge,
                "recommended_side_compensation_nm": fitted_side,
                "predicted_corrected_sem_nm": predicted_corrected,
                "fit_residual_edge_offset_nm": fitted_edge - tabulated_edge,
            }
        )

    return SemCorrectionProfile(
        rows=tuple(rows),
        reference_sem_nm=reference_sem_nm,
        target_cd_nm=target_cd_nm,
        coefficients_nm=coefficients_nm,
        fit_rmse_edge_offset_nm=fit_rmse,
        fit_max_abs_edge_offset_nm=fit_max_abs,
        source_sha256=source_sha256,
        total_shells=total_shells,
        period_um=period_um,
        reference_min_layer=reference_min_layer,
        process_gain=process_gain,
    )


def _format_csv_value(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.9f}"
    return value


def write_correction_csv(path: str | Path, profile: SemCorrectionProfile) -> None:
    """Write one self-describing, standard tabular correction artifact."""

    destination = Path(path)
    coefficient_fields = [
        f"fit_c{index}_edge_offset_nm"
        for index in range(len(profile.coefficients_nm))
    ]
    fieldnames = [
        *profile.rows[0].keys(),
        "total_shells",
        "period_um",
        "envelope_radius_um",
        "reference_min_layer",
        "process_gain",
        "fit_kind",
        "fit_order",
        *coefficient_fields,
        "fit_rmse_edge_offset_nm",
        "fit_max_abs_edge_offset_nm",
        "source_sha256",
    ]
    with destination.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in profile.rows:
            enriched = {
                **row,
                "total_shells": profile.total_shells,
                "period_um": profile.period_um,
                "envelope_radius_um": profile.total_shells * profile.period_um,
                "reference_min_layer": profile.reference_min_layer,
                "process_gain": profile.process_gain,
                "fit_kind": FIT_KIND,
                "fit_order": len(profile.coefficients_nm) - 1,
                "fit_rmse_edge_offset_nm": profile.fit_rmse_edge_offset_nm,
                "fit_max_abs_edge_offset_nm": profile.fit_max_abs_edge_offset_nm,
                "source_sha256": profile.source_sha256,
            }
            for index, coefficient in enumerate(profile.coefficients_nm):
                enriched[f"fit_c{index}_edge_offset_nm"] = coefficient
            writer.writerow(
                {key: _format_csv_value(enriched.get(key)) for key in fieldnames}
            )


def write_correction_figure(
    path: str | Path,
    measurements: Sequence[SemLayerMeasurement],
    profile: SemCorrectionProfile,
    *,
    dpi: int,
) -> None:
    """Render the SEM evidence, derived correction, and expected corrected CD."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(1, 3, figsize=(14.4, 4.2), constrained_layout=True)
    axis_sem, axis_correction, axis_expected = axes

    first_raw_label = True
    measured_layers = np.asarray(
        [item.layer_outside_in for item in measurements], dtype=float
    )
    measured_trimmed = np.asarray(
        [item.trimmed_mean_nm for item in measurements], dtype=float
    )
    for item in measurements:
        axis_sem.scatter(
            [item.layer_outside_in] * len(item.samples_nm),
            item.samples_nm,
            s=12,
            color="#9a9a9a",
            alpha=0.7,
            linewidths=0,
            label="SEM samples" if first_raw_label else None,
        )
        first_raw_label = False
    axis_sem.plot(
        measured_layers,
        measured_trimmed,
        color="#1764ab",
        linewidth=1.8,
        marker="o",
        markersize=3.0,
        label="Trimmed mean",
    )
    axis_sem.axhline(
        profile.reference_sem_nm,
        color="#222222",
        linewidth=1.0,
        label="Inner reference",
    )
    axis_sem.set(
        title="SEM measurements",
        xlabel="Layer (outside → inside)",
        ylabel="Triangle edge length (nm)",
        xlim=(0.5, profile.total_shells + 0.5),
    )
    axis_sem.legend(frameon=False, fontsize=8)

    rows_by_shell = sorted(profile.rows, key=lambda row: int(row["parent_shell"]))
    shells = np.asarray([row["parent_shell"] for row in rows_by_shell], dtype=float)
    tabulated = np.asarray(
        [row["tabulated_edge_offset_nm"] for row in rows_by_shell], dtype=float
    )
    recommended = np.asarray(
        [row["recommended_edge_offset_nm"] for row in rows_by_shell], dtype=float
    )
    measured_shells = profile.total_shells + 1 - measured_layers
    measured_edge = (
        (profile.target_cd_nm - measured_trimmed)
        / profile.process_gain
        / SIDE_TO_EDGE_OFFSET
    )
    axis_correction.plot(
        shells,
        tabulated,
        color="#a7a7a7",
        linewidth=1.2,
        label="Tabulated profile",
    )
    axis_correction.scatter(
        measured_shells,
        measured_edge,
        s=18,
        color="#1764ab",
        linewidths=0,
        label="Measured layers",
        zorder=3,
    )
    axis_correction.plot(
        shells,
        recommended,
        color="#c33c54",
        linewidth=2.0,
        label="Recommended fit",
    )
    axis_correction.axhline(0.0, color="#222222", linewidth=0.8)
    axis_correction.set(
        title="Derived layout correction",
        xlabel="Parent shell (center → edge)",
        ylabel="Polygon edge offset (nm)",
        xlim=(0.0, profile.total_shells + 0.5),
    )
    axis_correction.legend(frameon=False, fontsize=8)

    layers = np.asarray([row["layer_outside_in"] for row in profile.rows], dtype=float)
    sem_profile = np.asarray([row["sem_profile_nm"] for row in profile.rows], dtype=float)
    expected = np.asarray(
        [row["predicted_corrected_sem_nm"] for row in profile.rows], dtype=float
    )
    axis_expected.plot(
        layers,
        sem_profile,
        color="#a7a7a7",
        linewidth=1.4,
        label="Uncorrected profile",
    )
    axis_expected.plot(
        layers,
        expected,
        color="#1764ab",
        linewidth=2.0,
        label="Predicted after correction",
    )
    axis_expected.axhline(
        profile.target_cd_nm,
        color="#222222",
        linewidth=1.0,
        label="Target CD",
    )
    axis_expected.set(
        title="Predicted corrected CD",
        xlabel="Layer (outside → inside)",
        ylabel="Triangle edge length (nm)",
        xlim=(0.5, profile.total_shells + 0.5),
    )
    axis_expected.legend(frameon=False, fontsize=8)

    for label, axis in zip(("a", "b", "c"), axes):
        axis.text(
            -0.12,
            1.05,
            label,
            transform=axis.transAxes,
            fontsize=12,
            fontweight="bold",
            va="top",
        )
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.tick_params(direction="out", length=3, width=0.8)

    figure.savefig(path, dpi=dpi, facecolor="white")
    plt.close(figure)


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_project_path(project_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (project_root / path).resolve()


def _geometry_contract(parameter_path: Path) -> tuple[int, float]:
    with parameter_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    geometry = data["geometry"]
    finite = geometry["finite"]
    total_shells = int(finite["cavity_layers"]) + int(finite["cladding_layers"])
    period_um = float(geometry["lattice"]["period_um"])
    return total_shells, period_um


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an engineering radial layout-correction profile from SEM triangle data."
    )
    parser.add_argument("--source", default="data/SEM_air_hole_size.csv")
    parser.add_argument("--parameter", default="main/parameter.json")
    parser.add_argument("--output-csv", default="data/SEM_air_hole_correction.csv")
    parser.add_argument("--output-png", default="data/SEM_air_hole_correction.png")
    parser.add_argument("--reference-min-layer", type=int, default=22)
    parser.add_argument("--fit-order", type=int, default=2)
    parser.add_argument("--target-cd-nm", type=float, default=220.0)
    parser.add_argument("--process-gain", type=float, default=1.0)
    parser.add_argument("--dpi", type=int, default=220)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    project_root = Path(__file__).resolve().parents[2]
    args = build_argument_parser().parse_args(argv)
    source = _resolve_project_path(project_root, args.source)
    parameter = _resolve_project_path(project_root, args.parameter)
    output_csv = _resolve_project_path(project_root, args.output_csv)
    output_png = _resolve_project_path(project_root, args.output_png)
    if output_csv == output_png:
        raise ValueError("CSV and PNG outputs must be different paths")
    for destination in (output_csv, output_png):
        if destination.exists() and not args.overwrite:
            raise FileExistsError(f"output already exists: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)

    measurements = read_sem_measurements(source)
    total_shells, period_um = _geometry_contract(parameter)
    profile = derive_sem_correction_profile(
        measurements,
        total_shells=total_shells,
        period_um=period_um,
        target_cd_nm=args.target_cd_nm,
        reference_min_layer=args.reference_min_layer,
        fit_order=args.fit_order,
        process_gain=args.process_gain,
        source_sha256=_file_sha256(source),
    )

    token = uuid4().hex
    temporary_csv = output_csv.with_name(f".{output_csv.name}.{token}.tmp")
    temporary_png = output_png.with_name(f".{output_png.name}.{token}.tmp.png")
    try:
        write_correction_csv(temporary_csv, profile)
        write_correction_figure(
            temporary_png,
            measurements,
            profile,
            dpi=args.dpi,
        )
        temporary_csv.replace(output_csv)
        temporary_png.replace(output_png)
    finally:
        temporary_csv.unlink(missing_ok=True)
        temporary_png.unlink(missing_ok=True)

    coefficients = ", ".join(f"{value:.6f}" for value in profile.coefficients_nm)
    print(f"SEM rows: {len(measurements)}; correction rows: {len(profile.rows)}")
    print(f"Reference CD: {profile.reference_sem_nm:.6f} nm")
    print(f"Target CD: {profile.target_cd_nm:.6f} nm")
    print(f"{FIT_KIND} coefficients_nm: [{coefficients}]")
    print(f"Fit RMSE: {profile.fit_rmse_edge_offset_nm:.6f} nm edge offset")
    print(f"Wrote: {output_csv}")
    print(f"Wrote: {output_png}")
    return 0


__all__ = [
    "FIT_KIND",
    "SIDE_TO_EDGE_OFFSET",
    "SemCorrectionProfile",
    "SemLayerMeasurement",
    "derive_sem_correction_profile",
    "evaluate_radial_even_polynomial",
    "main",
    "read_sem_measurements",
    "write_correction_csv",
    "write_correction_figure",
]


if __name__ == "__main__":
    raise SystemExit(main())
