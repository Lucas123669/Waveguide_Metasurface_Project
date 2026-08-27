"""Build, solve, and post-process the finite 45-degree COMSOL deflector."""

import argparse
import copy
import csv
import json
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from jpype.types import JArray, JDouble, JString


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

import mph

from gwm_workflow.comsol_structure import build_structure, ensure_comsol_runtime


def _strings(values):
    return JArray(JString, 1)([str(value) for value in values])


def _coordinates(rows):
    return JArray(JDouble, 2)([[float(value) for value in row] for row in rows])


def interpolate(jmodel, tag, expressions, x, y, z):
    numerical = jmodel.result().numerical()
    if tag in list(numerical.tags()):
        numerical.remove(tag)
    numerical.create(tag, "Interp")
    feature = jmodel.result().numerical(tag)
    feature.set("expr", _strings(expressions))
    feature.set("coord", _coordinates([x, y, z]))
    feature.run()
    raw = np.asarray(feature.getData(), dtype=float)
    # COMSOL returns (expression, solution, coordinate). A single-frequency
    # solution therefore has a singleton middle axis.
    if raw.ndim == 3:
        raw = raw[:, -1, :]
    elif raw.ndim == 1:
        raw = raw.reshape(1, -1)
    return raw


def evaluate_scalar(model, expression):
    value = np.asarray(model.evaluate(expression)).reshape(-1)
    if not value.size:
        raise RuntimeError(f"Empty evaluation for {expression}")
    return float(np.real(value[-1]))


def angular_spectrum(x_um, fields, wavelength_um, nfft=65536):
    dx = float(x_um[1] - x_um[0])
    window = np.hanning(x_um.size)
    spectrum = np.zeros(nfft, dtype=float)
    for field in fields:
        spectrum += np.abs(np.fft.fftshift(np.fft.fft(field * window, n=nfft))) ** 2
    kx = 2.0 * np.pi * np.fft.fftshift(np.fft.fftfreq(nfft, d=dx))
    k0 = 2.0 * np.pi / wavelength_um
    propagating = np.abs(kx) <= k0
    theta_internal = np.rad2deg(np.arcsin(np.clip(kx[propagating] / k0, -1.0, 1.0)))
    power = spectrum[propagating]
    power /= max(float(power.max()), np.finfo(float).tiny)
    # The paper defines the plotted angle with the opposite x sign to the
    # internal grating-wavevector coordinate used in the workflow.
    theta_reported = -theta_internal
    useful = np.abs(theta_reported) >= 8.0
    peak_local = int(np.argmax(np.where(useful, power, -1.0)))
    peak_angle = float(theta_reported[peak_local])
    peak_power = float(power[peak_local])
    return theta_reported, power, peak_angle, peak_power


def save_line_csv(path, x, data):
    names = [
        "x_um",
        "Ex_real_Vpm", "Ex_imag_Vpm",
        "Ey_real_Vpm", "Ey_imag_Vpm",
        "Ez_real_Vpm", "Ez_imag_Vpm",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(names)
        for index, xpos in enumerate(x):
            writer.writerow([float(xpos)] + [float(data[row, index]) for row in range(data.shape[0])])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=os.path.join(PROJECT_ROOT, "configs", "seeds", "guo2020_beam_deflector_paper_seed.json"))
    parser.add_argument("--mode-result", default=os.path.join(PROJECT_ROOT, "experiments", "l02_guo_2020", "beam_deflector", "waveguide_mode_1550nm", "mode_result.json"))
    parser.add_argument("--output", default=os.path.join(PROJECT_ROOT, "experiments", "l02_guo_2020", "beam_deflector", "right45_15cells_air2x"))
    parser.add_argument("--cells", type=int, default=6)
    parser.add_argument("--period-um", type=float, default=None, help="override the bare-waveguide phase-matching period")
    parser.add_argument("--phase-index", type=float, default=None, help="effective/Bloch index used to report the theoretical angle")
    parser.add_argument("--air-height-um", type=float, default=None, help="air-domain height above the BOX top")
    parser.add_argument("--monitor-height-um", type=float, default=None, help="absolute z position of the angular-spectrum monitor")
    parser.add_argument("--export-clean-java-only", action="store_true")
    args = parser.parse_args()

    if args.export_clean_java_only:
        ensure_comsol_runtime()
        if os.name == "nt":
            mph.option("session", os.environ.get("GWM_WORKFLOW_MPH_SESSION", "client-server"))
        client = mph.start(version=os.environ.get("COMSOL_VERSION"))
        source = os.path.abspath(os.path.join(args.output, "guided_wave_metasurface_45deg_unsolved.mph"))
        destination = os.path.abspath(os.path.join(args.output, "GuidedWaveMetasurface45deg.java"))
        model = client.load(source)
        try:
            model.save(destination)
            print(json.dumps({"source": source, "clean_java": destination}, indent=2))
        finally:
            client.remove(model)
        return

    with open(args.config, "r", encoding="utf-8") as handle:
        base_config = json.load(handle)
    with open(args.mode_result, "r", encoding="utf-8") as handle:
        mode_result = json.load(handle)

    config = copy.deepcopy(base_config)
    design = config["design"]
    period = float(args.period_um) if args.period_um is not None else float(mode_result["phase_matching_period_um"])
    phase_index = float(args.phase_index) if args.phase_index is not None else float(mode_result["selected_te00_neff"])
    design.update(
        {
            "supercell_period_um": period,
            "atom_pitch_um": period / 3.0,
            "supercell_count": args.cells,
            "port_buffer_um": 1.5,
            "computational_width_um": 2.0,
            "air_height_um": float(args.air_height_um) if args.air_height_um is not None else 1.8,
            "monitor_height_um": float(args.monitor_height_um) if args.monitor_height_um is not None else 1.25,
            "substrate_thickness_um": 0.4,
            "include_substrate": False,
            "bulk_mesh_max_um": 0.25,
            "dielectric_mesh_max_um": 0.15,
            "silicon_mesh_max_um": 0.055,
            "metal_mesh_max_um": 0.020,
        }
    )
    os.makedirs(args.output, exist_ok=True)
    with open(os.path.join(args.output, "resolved_config.json"), "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)

    ensure_comsol_runtime()
    if os.name == "nt":
        mph.option("session", os.environ.get("GWM_WORKFLOW_MPH_SESSION", "client-server"))
    print("Starting COMSOL...", flush=True)
    client = mph.start(version=os.environ.get("COMSOL_VERSION"))
    model = client.create("guided_wave_metasurface_45deg")
    start = time.perf_counter()
    try:
        print(f"Building {args.cells} supercells at Lambda={period * 1e3:.3f} nm...", flush=True)
        summary = build_structure(model.java, config, supercell_count=args.cells, add_physics=True, build_mesh=False)
        pre_path = os.path.abspath(os.path.join(args.output, "guided_wave_metasurface_45deg_unsolved.mph"))
        model.save(pre_path)
        print("Meshing 3D model...", flush=True)
        mesh_start = time.perf_counter()
        model.java.component("comp1").mesh("mesh1").run()
        mesh_seconds = time.perf_counter() - mesh_start
        model.save(pre_path)
        print(f"Mesh complete in {mesh_seconds:.1f} s; solving frequency-domain model...", flush=True)
        solve_start = time.perf_counter()
        # Numeric ports need COMSOL's generated port-mode solver sequence.
        # Running the raw study node can omit those auxiliary mode solves and
        # leaves the port fields E10/E20 undefined.
        model.java.study("std1").createAutoSequences("all")
        model.java.sol("sol1").runAll()
        solve_seconds = time.perf_counter() - solve_start
        mph_path = os.path.abspath(os.path.join(args.output, "guided_wave_metasurface_45deg_solved.mph"))
        model.save(mph_path)
        print(f"Solve complete in {solve_seconds:.1f} s; sampling monitor fields...", flush=True)

        array_length = args.cells * period
        device_length = array_length + 2.0 * float(design["port_buffer_um"])
        x = np.linspace(-device_length / 2.0 + 0.02, device_length / 2.0 - 0.02, 1024)
        y = np.zeros_like(x)
        z = np.full_like(x, float(design["monitor_height_um"]))
        expressions = [
            "real(ewfd.Ex)", "imag(ewfd.Ex)",
            "real(ewfd.Ey)", "imag(ewfd.Ey)",
            "real(ewfd.Ez)", "imag(ewfd.Ez)",
        ]
        line_data = interpolate(model.java, "interp_line", expressions, x, y, z)
        fields = [line_data[0] + 1j * line_data[1], line_data[2] + 1j * line_data[3], line_data[4] + 1j * line_data[5]]
        theta, angular_power, fft_peak, fft_peak_power = angular_spectrum(x, fields, float(design["wavelength_um"]))

        nx, nz = 360, 180
        x_grid = np.linspace(-device_length / 2.0 + 0.02, device_length / 2.0 - 0.02, nx)
        z_grid = np.linspace(0.0, float(design["air_height_um"]) - 0.02, nz)
        xx, zz = np.meshgrid(x_grid, z_grid)
        plane_data = interpolate(
            model.java,
            "interp_plane",
            ["ewfd.normE"],
            xx.reshape(-1),
            np.zeros(xx.size),
            zz.reshape(-1),
        )[0].reshape(nz, nx)

        sparams = {}
        for key, expression in {
            "reflectance_S11_sq": "abs(ewfd.S11)^2",
            "transmittance_S21_sq": "abs(ewfd.S21)^2",
        }.items():
            try:
                sparams[key] = evaluate_scalar(model, expression)
            except Exception as exc:
                sparams[key] = None
                sparams[f"{key}_error"] = str(exc)

        java_path = os.path.abspath(os.path.join(args.output, "GuidedWaveMetasurface45deg.java"))
        model.save(java_path)

        line_csv = os.path.abspath(os.path.join(args.output, "monitor_field_complex.csv"))
        save_line_csv(line_csv, x, line_data)
        angle_csv = os.path.abspath(os.path.join(args.output, "angular_spectrum.csv"))
        np.savetxt(angle_csv, np.column_stack([theta, angular_power]), delimiter=",", header="reported_angle_deg,normalized_power", comments="")

        angle_png = os.path.abspath(os.path.join(args.output, "angular_spectrum.png"))
        fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=160)
        ax.plot(theta, 10.0 * np.log10(np.maximum(angular_power, 1e-8)), color="#1769aa", lw=2)
        target_signed = -45.0 if fft_peak < 0 else 45.0
        ax.axvline(target_signed, color="#d32f2f", ls="--", label=f"target {target_signed:+.0f} degrees")
        ax.axvline(fft_peak, color="#2e7d32", ls=":", label=f"COMSOL peak {fft_peak:.2f} degrees")
        ax.set(xlabel="Reported radiation angle (deg)", ylabel="Normalized angular power (dB)", xlim=(-90, 90), ylim=(-60, 1))
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(angle_png)
        plt.close(fig)

        field_png = os.path.abspath(os.path.join(args.output, "field_xz_normE.png"))
        fig, ax = plt.subplots(figsize=(8.2, 4.4), dpi=160)
        image = ax.pcolormesh(x_grid, z_grid, np.log10(np.maximum(plane_data, np.nanmax(plane_data) * 1e-6)), shading="auto", cmap="inferno")
        ax.set(xlabel="x (um)", ylabel="z (um)", title="COMSOL |E| in y=0 plane (log10 scale)")
        fig.colorbar(image, ax=ax, label="log10(|E| / V m-1)")
        fig.tight_layout()
        fig.savefig(field_png)
        plt.close(fig)

        theoretical_internal = np.rad2deg(np.arcsin(phase_index - float(design["wavelength_um"]) / period))
        result = {
            **summary,
            "selected_te00_neff": float(mode_result["selected_te00_neff"]),
            "phase_matching_index_used": phase_index,
            "supercell_period_um": period,
            "atom_pitch_um": period / 3.0,
            "theoretical_reported_angle_deg": float(-theoretical_internal),
            "theoretical_physical_angle_deg": float(theoretical_internal),
            "comsol_fft_reported_peak_angle_deg": fft_peak,
            "comsol_fft_peak_normalized_power": fft_peak_power,
            "monitor_z_um": float(design["monitor_height_um"]),
            "monitor_samples": int(x.size),
            "mesh_seconds": mesh_seconds,
            "solve_seconds": solve_seconds,
            "total_seconds": time.perf_counter() - start,
            **sparams,
            "mph_path": mph_path,
            "java_path": java_path,
            "monitor_csv": line_csv,
            "angular_spectrum_csv": angle_csv,
            "angular_spectrum_png": angle_png,
            "field_xz_png": field_png,
            "model_scope": f"finite {args.cells}-supercell validation; figure-read antenna dimensions; scattering boundaries; no PML",
        }
        result_path = os.path.abspath(os.path.join(args.output, "simulation_result.json"))
        with open(result_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
        print(json.dumps(result, indent=2), flush=True)
    finally:
        client.remove(model)


if __name__ == "__main__":
    main()
