"""Recompute a finely sampled angular spectrum from a saved COMSOL monitor line."""

import argparse
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "comsol_models", "beam_deflector_45deg")))
    parser.add_argument("--nfft", type=int, default=65536)
    args = parser.parse_args()

    line_path = os.path.join(args.directory, "monitor_field_complex.csv")
    result_path = os.path.join(args.directory, "simulation_result.json")
    values = np.loadtxt(line_path, delimiter=",", skiprows=1)
    x = values[:, 0]
    fields = [
        values[:, 1] + 1j * values[:, 2],
        values[:, 3] + 1j * values[:, 4],
        values[:, 5] + 1j * values[:, 6],
    ]
    window = np.hanning(x.size)
    spectrum = np.zeros(args.nfft)
    for field in fields:
        spectrum += np.abs(np.fft.fftshift(np.fft.fft(field * window, n=args.nfft))) ** 2
    wavelength_um = 1.55
    k0 = 2.0 * np.pi / wavelength_um
    kx = 2.0 * np.pi * np.fft.fftshift(np.fft.fftfreq(args.nfft, d=x[1] - x[0]))
    propagating = np.abs(kx) <= k0
    # COMSOL uses the exp(+i*omega*t) convention, so physical propagation
    # direction has the opposite sign to NumPy's FFT spatial frequency.
    angle = -np.rad2deg(np.arcsin(np.clip(kx[propagating] / k0, -1.0, 1.0)))
    power = spectrum[propagating]
    power /= power.max()
    useful = np.abs(angle) >= 8.0
    peak_index = int(np.argmax(np.where(useful, power, -1.0)))
    peak_angle = float(angle[peak_index])
    peak_abs = abs(peak_angle)

    spectrum_path = os.path.join(args.directory, "angular_spectrum.csv")
    np.savetxt(spectrum_path, np.column_stack([angle, power]), delimiter=",", header="physical_angle_from_+z_deg,normalized_power", comments="")

    image_path = os.path.join(args.directory, "angular_spectrum.png")
    figure, axis = plt.subplots(figsize=(7.2, 4.4), dpi=160)
    axis.plot(angle, 10.0 * np.log10(np.maximum(power, 1e-8)), color="#1769aa", linewidth=2)
    target_signed = -45.0 if peak_angle < 0 else 45.0
    axis.axvline(target_signed, color="#d32f2f", linestyle="--", label=f"target {target_signed:+.0f} degrees")
    axis.axvline(peak_angle, color="#2e7d32", linestyle=":", label=f"COMSOL peak {peak_angle:+.2f} degrees")
    axis.set(
        xlabel="Physical radiation angle from +z (deg)",
        ylabel="Normalized angular power (dB)",
        xlim=(-90, 90),
        ylim=(-40, 1),
    )
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(image_path)
    plt.close(figure)

    with open(result_path, "r", encoding="utf-8") as handle:
        result = json.load(handle)
    result["comsol_fft_coarse_bin_peak_angle_deg"] = result.get("comsol_fft_reported_peak_angle_deg")
    result["comsol_fft_physical_peak_angle_deg"] = peak_angle
    result["comsol_fft_absolute_peak_angle_deg"] = peak_abs
    result["absolute_angle_error_deg"] = abs(peak_abs - 45.0)
    result["angular_spectrum_zero_padding_nfft"] = args.nfft
    result["angle_sign_definition"] = "theta=0 is +z; negative theta points toward -x; magnitude is the requested upward tilt"
    with open(result_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    print(json.dumps({
        "peak_physical_angle_deg": peak_angle,
        "peak_absolute_angle_deg": peak_abs,
        "absolute_error_deg": abs(peak_abs - 45.0),
        "spectrum": spectrum_path,
        "image": image_path,
        "result": result_path,
    }, indent=2))


if __name__ == "__main__":
    main()
