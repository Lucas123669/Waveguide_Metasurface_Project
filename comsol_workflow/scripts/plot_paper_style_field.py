"""Render a paper-style real(Ey) field map from the solved COMSOL model."""

import argparse
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from jpype.types import JArray, JDouble, JString


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _strings(values):
    return JArray(JString, 1)([str(value) for value in values])


def _coordinates(rows):
    return JArray(JDouble, 2)([[float(value) for value in row] for row in rows])


def sample_comsol(mph_path, cache_path, x, z):
    import mph

    if os.name == "nt":
        mph.option("session", os.environ.get("GWM_WORKFLOW_MPH_SESSION", "client-server"))
    print("Loading solved COMSOL model...", flush=True)
    client = mph.start(version=os.environ.get("COMSOL_VERSION"))
    model = client.load(os.path.abspath(mph_path))
    try:
        xx, zz = np.meshgrid(x, z)
        jmodel = model.java
        tag = "interp_paper_ey"
        numerical = jmodel.result().numerical()
        if tag in list(numerical.tags()):
            numerical.remove(tag)
        numerical.create(tag, "Interp")
        feature = jmodel.result().numerical(tag)
        feature.set("expr", _strings(["real(ewfd.Ey)", "imag(ewfd.Ey)"]))
        feature.set(
            "coord",
            _coordinates([xx.reshape(-1), np.zeros(xx.size), zz.reshape(-1)]),
        )
        feature.run()
        raw = np.asarray(feature.getData(), dtype=float)
        if raw.ndim == 3:
            raw = raw[:, -1, :]
        ey = (raw[0] + 1j * raw[1]).reshape(z.size, x.size)
        np.savez_compressed(cache_path, x_um=x, z_um=z, ey=ey)
        print(f"Saved field cache: {cache_path}", flush=True)
        return ey
    finally:
        client.remove(model)


def paper_colormap():
    # Blue-cyan-green-yellow-red, close to the field map used in the paper.
    return LinearSegmentedColormap.from_list(
        "paper_field",
        [
            (0.00, "#0017a8"),
            (0.22, "#0068ff"),
            (0.42, "#00d7df"),
            (0.50, "#72ef8b"),
            (0.63, "#f4f43a"),
            (0.82, "#ff7a00"),
            (1.00, "#a30000"),
        ],
    )


def add_structure(axis, design, cells, period):
    x_left, x_right = axis.get_xlim()
    # BOX and 220-nm silicon waveguide.
    axis.add_patch(patches.Rectangle((x_left, -0.16), x_right - x_left, 0.16, facecolor="#5d2431", edgecolor="none", zorder=7))
    axis.add_patch(patches.Rectangle((x_left, 0.00), x_right - x_left, 0.22, facecolor="#153a83", edgecolor="#08225c", linewidth=0.7, zorder=8))

    library = design["phase_library"]
    array_x0 = -cells * period / 2.0
    atom_pitch = period / 3.0
    for index in range(3 * cells):
        atom = library[index % 3]
        width = float(atom["lx_um"])
        center = array_x0 + (index + 0.5) * atom_pitch
        left = center - width / 2.0
        axis.add_patch(patches.Rectangle((left, 0.22), width, 0.03, facecolor="#b51d22", edgecolor="#6f0e12", linewidth=0.25, zorder=9))
        axis.add_patch(patches.Rectangle((left, 0.25), width, 0.03, facecolor="#79cbe8", edgecolor="none", zorder=9))
        axis.add_patch(patches.Rectangle((left, 0.28), width, 0.03, facecolor="#e3291f", edgecolor="#7c110d", linewidth=0.25, zorder=9))


def add_annotations(axis, peak_angle):
    x_left, x_right = axis.get_xlim()
    z_top = axis.get_ylim()[1]
    # Guided-wave arrow.
    axis.annotate("", xy=(x_right - 0.35, 0.11), xytext=(x_left + 0.65, 0.11), arrowprops=dict(arrowstyle="-|>", color="#f04b3e", lw=2.0), zorder=15)

    origin = (0.35, 0.31)
    length = min(2.65, 0.78 * z_top)
    angle_rad = np.deg2rad(abs(peak_angle))
    dx = -np.sin(angle_rad) * length if peak_angle < 0 else np.sin(angle_rad) * length
    dz = np.cos(angle_rad) * length
    end = (origin[0] + dx, origin[1] + dz)
    axis.plot([origin[0], origin[0]], [origin[1], min(z_top - 0.08, origin[1] + length)], color="white", lw=1.2, ls=(0, (3, 2)), zorder=14)
    axis.annotate("", xy=end, xytext=origin, arrowprops=dict(arrowstyle="-|>", color="white", lw=2.2), zorder=15)

    direction = 1.0 if peak_angle >= 0 else -1.0
    if direction > 0:
        arc_start, arc_end = 90 - abs(peak_angle), 90
        theta_text_x = origin[0] + 0.12
    else:
        arc_start, arc_end = 90, 90 + abs(peak_angle)
        theta_text_x = origin[0] - 0.34
    arc = patches.Arc(origin, 0.52, 0.52, theta1=arc_start, theta2=arc_end, color="white", lw=1.4, zorder=15)
    axis.add_patch(arc)
    axis.text(theta_text_x, origin[1] + 0.43, rf"$\theta={abs(peak_angle):.1f}^\circ$", color="white", fontsize=11, zorder=15)
    kx_end = origin[0] + direction * 0.63
    axis.annotate("", xy=(kx_end, origin[1] + 0.02), xytext=origin, arrowprops=dict(arrowstyle="-|>", color="white", lw=1.6), zorder=15)
    axis.text(origin[0] + direction * 0.38, origin[1] + 0.07, r"$k_x$", color="white", fontsize=11, zorder=15)

    # 500-nm scale bar.
    x0, z0 = x_left + 0.55, z_top - 0.18
    axis.plot([x0, x0 + 0.50], [z0, z0], color="black", lw=2.2, solid_capstyle="butt", zorder=16)
    axis.text(x0 + 0.25, z0 + 0.07, "500 nm", ha="center", va="bottom", fontsize=10, color="black", zorder=16)

    # Coordinate triad.
    triad_x, triad_z = x_left + 0.06, -0.10
    axis.annotate("", xy=(triad_x + 0.40, triad_z), xytext=(triad_x, triad_z), arrowprops=dict(arrowstyle="-|>", color="#ef3326", lw=1.5), zorder=16)
    axis.annotate("", xy=(triad_x, triad_z + 0.35), xytext=(triad_x, triad_z), arrowprops=dict(arrowstyle="-|>", color="#1575b8", lw=1.5), zorder=16)
    axis.text(triad_x + 0.43, triad_z - 0.03, "$x$", fontsize=10)
    axis.text(triad_x - 0.06, triad_z + 0.38, "$z$", fontsize=10)

    axis.text(0.50, -0.095, r"$k_x=\beta-2\pi/\Lambda$", transform=axis.transAxes, ha="center", va="top", fontsize=12)


def render(cache_path, config_path, result_path, output_png, output_pdf):
    cached = np.load(cache_path)
    x = cached["x_um"]
    z = cached["z_um"]
    ey = cached["ey"]
    with open(config_path, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    with open(result_path, "r", encoding="utf-8") as handle:
        result = json.load(handle)

    # Select a reproducible global phase referenced to the strongest point in
    # the radiating air region, then normalize only against that region.
    air_mask = z[:, None] >= 0.34
    masked_amplitude = np.where(air_mask, np.abs(ey), 0.0)
    ref_index = np.unravel_index(int(np.argmax(masked_amplitude)), ey.shape)
    phase = np.angle(ey[ref_index])
    field = np.real(ey * np.exp(-1j * phase))
    scale = np.percentile(np.abs(field[air_mask.repeat(x.size, axis=1)]), 99.5)
    normalized = np.clip(field / max(scale, np.finfo(float).tiny), -1.0, 1.0)

    figure = plt.figure(figsize=(9.2, 4.0), dpi=220)
    axis = figure.add_axes([0.055, 0.16, 0.82, 0.77])
    image = axis.pcolormesh(x, z, normalized, shading="auto", cmap=paper_colormap(), vmin=-1, vmax=1, rasterized=True)
    axis.set_xlim(float(x.min()), float(x.max()))
    axis.set_ylim(-0.16, float(z.max()))
    add_structure(axis, config["design"], int(result["supercell_count"]), float(result["supercell_period_um"]))
    peak_angle = float(result["comsol_fft_physical_peak_angle_deg"])
    add_annotations(axis, peak_angle)
    axis.set_xticks([])
    axis.set_yticks([])
    for spine in axis.spines.values():
        spine.set_visible(False)

    color_axis = figure.add_axes([0.895, 0.34, 0.018, 0.54])
    colorbar = figure.colorbar(image, cax=color_axis, ticks=[-1, 0, 1])
    colorbar.ax.tick_params(labelsize=9, length=2)
    figure.text(0.885, 0.92, r"$\mathrm{Re}(E_y)$ (a.u.)", ha="center", va="bottom", fontsize=12)
    figure.savefig(output_png, dpi=300, facecolor="white")
    figure.savefig(output_pdf, dpi=300, facecolor="white")
    plt.close(figure)
    print(json.dumps({"png": output_png, "pdf": output_pdf, "peak_angle_deg": peak_angle}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default=os.path.join(PROJECT_ROOT, "comsol_models", "beam_deflector_45deg"))
    initial, _ = parser.parse_known_args()
    directory = os.path.abspath(initial.directory)
    parser.add_argument("--mph", default=os.path.join(directory, "guided_wave_metasurface_45deg_solved.mph"))
    parser.add_argument("--cache", default=os.path.join(directory, "field_xz_Ey_complex.npz"))
    parser.add_argument("--config", default=os.path.join(directory, "resolved_config.json"))
    parser.add_argument("--result", default=os.path.join(directory, "simulation_result.json"))
    parser.add_argument("--png", default=os.path.join(directory, "field_xz_Ey_paper_style.png"))
    parser.add_argument("--pdf", default=os.path.join(directory, "field_xz_Ey_paper_style.pdf"))
    parser.add_argument("--resample", action="store_true")
    args = parser.parse_args()

    with open(args.result, "r", encoding="utf-8") as handle:
        result = json.load(handle)
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    half_width = max(2.40, float(result["array_length_um"]) / 2.0 + 0.80)
    sample_count = max(720, int(np.ceil(half_width * 2.0 / 0.0095)))
    x = np.linspace(-half_width, half_width, sample_count)
    z_top = float(config["design"]["air_height_um"]) - 0.18
    z_count = max(300, int(np.ceil((z_top - 0.22) / 0.0095)))
    z = np.linspace(0.22, z_top, z_count)
    if args.resample or not os.path.isfile(args.cache):
        sample_comsol(args.mph, args.cache, x, z)
    render(args.cache, args.config, args.result, args.png, args.pdf)


if __name__ == "__main__":
    main()
