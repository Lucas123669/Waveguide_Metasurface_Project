"""COMSOL mode analysis for the 600 nm x 220 nm SOI ridge waveguide."""

import json
import os
import shutil

import numpy as np

try:
    import mph
except Exception as exc:  # pragma: no cover
    mph = None
    _MPH_ERROR = exc
else:
    _MPH_ERROR = None

try:
    from jpype.types import JArray, JString
except Exception as exc:  # pragma: no cover
    JArray = JString = None
    _JPYPE_ERROR = exc
else:
    _JPYPE_ERROR = None


def _strings(values):
    return JArray(JString, 1)([str(value) for value in values])


def _rectangle(geom, tag, label, pos, size):
    geom.create(tag, "Rectangle")
    feature = geom.feature(tag)
    feature.label(label)
    feature.set("base", "corner")
    feature.set("pos", _strings(pos))
    feature.set("size", _strings(size))
    feature.set("selresult", True)


def _box_boundary(component, tag, bounds):
    component.selection().create(tag, "Box")
    selection = component.selection(tag)
    selection.geom("geom1", 1)
    selection.set("condition", "inside")
    for name, value in bounds.items():
        selection.set(name, str(value))


def _index_material(component, tag, label, selection, index):
    component.material().create(tag, "Common")
    material = component.material(tag)
    material.label(label)
    if selection:
        material.selection().named(selection)
    material.propertyGroup().create("RefractiveIndex", "RefractiveIndex", "Refractive index")
    material.propertyGroup("RefractiveIndex").set(
        "n", _strings([index, "0", "0", "0", index, "0", "0", "0", index])
    )
    material.propertyGroup("RefractiveIndex").set(
        "ki", _strings(["0", "0", "0", "0", "0", "0", "0", "0", "0"])
    )


def ensure_runtime():
    if _MPH_ERROR is not None:
        raise RuntimeError("MPh is required") from _MPH_ERROR
    if _JPYPE_ERROR is not None:
        raise RuntimeError("JPype is required") from _JPYPE_ERROR
    if not any(shutil.which(name) for name in ["comsol", "comsolmphserver", "comsolbatch"]):
        raise RuntimeError("COMSOL executables are not on PATH")


def build_mode_model(jmodel, config):
    design = config["design"]
    materials = config["materials"]

    jmodel.label("soi_waveguide_mode.mph")
    parameters = {
        "lambda0": f'{design["wavelength_um"]}[um]',
        "freq0": "c_const/lambda0",
        "wg_w": f'{design["waveguide_width_um"]}[um]',
        "wg_h": f'{design["waveguide_height_um"]}[um]',
        "box_h": f'{design["box_thickness_um"]}[um]',
        "air_h": "2[um]",
        "side_pad": "1.5[um]",
        "n_air": str(materials["air"]["n"]),
        "n_si": str(materials["silicon"]["n"]),
        "n_sio2": str(materials["silica"]["n"]),
        "xmin": "-wg_w/2-side_pad",
        "xmax": "wg_w/2+side_pad",
        "ymin": "-box_h",
        "ymax": "wg_h+air_h",
        "mesh_core": "0.035[um]",
        "mesh_clad": "0.15[um]",
        "tol": "1[nm]",
    }
    for key, value in parameters.items():
        jmodel.param().set(key, value)

    jmodel.component().create("comp1", True)
    component = jmodel.component("comp1")
    component.label("SOI waveguide cross section")
    component.geom().create("geom1", 2)
    geom = component.geom("geom1")
    geom.lengthUnit("um")
    _rectangle(geom, "air_window", "air computational window", ["xmin", "ymin"], ["xmax-xmin", "ymax-ymin"])
    _rectangle(geom, "box", "3 um buried oxide", ["xmin", "ymin"], ["xmax-xmin", "box_h"])
    _rectangle(geom, "core", "600 nm x 220 nm silicon ridge", ["-wg_w/2", "0"], ["wg_w", "wg_h"])
    geom.feature("fin").set("action", "union")
    geom.run()

    common = {"xmin": "xmin", "xmax": "xmax", "ymin": "ymin", "ymax": "ymax"}
    _box_boundary(component, "sel_left", dict(common, xmax="xmin+tol"))
    _box_boundary(component, "sel_right", dict(common, xmin="xmax-tol"))
    _box_boundary(component, "sel_bottom", dict(common, ymax="ymin+tol"))
    _box_boundary(component, "sel_top", dict(common, ymin="ymax-tol"))
    component.selection().create("sel_outer", "Union")
    component.selection("sel_outer").geom("geom1", 1)
    component.selection("sel_outer").set("input", _strings(["sel_left", "sel_right", "sel_bottom", "sel_top"]))

    _index_material(component, "mat_air", "Air", None, "n_air")
    _index_material(component, "mat_sio2", "Silicon dioxide", "geom1_box_dom", "n_sio2")
    _index_material(component, "mat_si", "Silicon", "geom1_core_dom", "n_si")

    component.physics().create("ewfd", "ElectromagneticWavesFrequencyDomain", "geom1")
    physics = component.physics("ewfd")
    physics.create("sctr1", "Scattering", 1)
    physics.feature("sctr1").selection().named("sel_outer")

    component.mesh().create("mesh1")
    mesh = component.mesh("mesh1")
    mesh.automatic(False)
    mesh.feature("size").set("custom", "on")
    mesh.feature("size").set("hmax", "mesh_clad")
    mesh.feature("size").set("hmin", "mesh_core/5")
    mesh.create("size_core", "Size")
    mesh.feature("size_core").selection().named("geom1_core_dom")
    mesh.feature("size_core").set("custom", "on")
    mesh.feature("size_core").set("hmax", "mesh_core")
    mesh.feature("size_core").set("hmin", "mesh_core/5")

    jmodel.study().create("std1")
    jmodel.study("std1").create("mode", "ModeAnalysis")
    study = jmodel.study("std1").feature("mode")
    study.label("1550 nm guided-mode analysis")
    study.set("modeFreq", "freq0")
    study.set("neigs", "6")
    study.set("shift", "2.5")


def solve_mode(config, output_directory):
    ensure_runtime()
    os.makedirs(output_directory, exist_ok=True)
    if os.name == "nt":
        mph.option("session", os.environ.get("GWM_WORKFLOW_MPH_SESSION", "client-server"))
    client = mph.start(version=os.environ.get("COMSOL_VERSION"))
    model = client.create("soi_waveguide_mode")
    try:
        build_mode_model(model.java, config)
        model.java.component("comp1").mesh("mesh1").run()
        model.java.study("std1").run()

        real_neff = np.asarray(model.evaluate("real(ewfd.neff)"), dtype=float).reshape(-1)
        imag_neff = np.asarray(model.evaluate("imag(ewfd.neff)"), dtype=float).reshape(-1)
        order = np.argsort(real_neff)[::-1]
        real_neff = real_neff[order]
        imag_neff = imag_neff[order]
        guided = np.where((real_neff > float(config["materials"]["silica"]["n"])) & (real_neff < float(config["materials"]["silicon"]["n"])))[0]
        if guided.size == 0:
            raise RuntimeError(f"No guided mode found; neff={real_neff.tolist()}")
        te00_index = int(guided[0])
        neff = float(real_neff[te00_index])

        wavelength = float(config["design"]["wavelength_um"])
        target_angle = 45.0
        period = wavelength / (neff + np.sin(np.deg2rad(target_angle)))
        predicted_internal = np.rad2deg(np.arcsin(neff - wavelength / period))
        reported_angle = -predicted_internal

        result = {
            "wavelength_um": wavelength,
            "waveguide_width_um": float(config["design"]["waveguide_width_um"]),
            "waveguide_height_um": float(config["design"]["waveguide_height_um"]),
            "real_neff_sorted": real_neff.tolist(),
            "imag_neff_sorted": imag_neff.tolist(),
            "selected_te00_neff": neff,
            "target_reported_angle_deg": target_angle,
            "phase_matching_period_um": float(period),
            "phase_matching_internal_angle_deg": float(predicted_internal),
            "phase_matching_reported_angle_deg": float(reported_angle),
            "equation": "sin(theta_internal)=neff-lambda0/Lambda; theta_reported=-theta_internal",
        }
        mph_path = os.path.abspath(os.path.join(output_directory, "soi_waveguide_mode.mph"))
        java_path = os.path.abspath(os.path.join(output_directory, "SOIWaveguideMode.java"))
        json_path = os.path.abspath(os.path.join(output_directory, "mode_result.json"))
        model.save(mph_path)
        model.save(java_path)
        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
        result.update({"mph_path": mph_path, "java_path": java_path, "json_path": json_path})
        return result
    finally:
        client.remove(model)
