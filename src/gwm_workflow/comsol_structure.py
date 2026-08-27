"""Create the 3D COMSOL structure for the paper's straight-waveguide deflector.

This module uses MPh only as the process/session bridge. The actual model tree
is created through COMSOL's Java API, so the resulting MPH can be inspected in
the GUI and exported as ordinary COMSOL Java source.
"""

import json
import math
import os
import shutil


try:
    import mph
except Exception as exc:  # pragma: no cover - exercised only without COMSOL
    mph = None
    _MPH_ERROR = exc
else:
    _MPH_ERROR = None

try:
    from jpype.types import JArray, JString
except Exception as exc:  # pragma: no cover - exercised only without JPype
    JArray = JString = None
    _JPYPE_ERROR = exc
else:
    _JPYPE_ERROR = None


def _strings(values):
    return JArray(JString, 1)([str(value) for value in values])


def _set_parameter(jmodel, name, value, unit=None, description=None):
    text = f"{value}[{unit}]" if unit else str(value)
    if description:
        jmodel.param().set(name, text, description)
    else:
        jmodel.param().set(name, text)


def _block(geom, tag, label, pos, size):
    geom.create(tag, "Block")
    feature = geom.feature(tag)
    feature.label(label)
    feature.set("base", "corner")
    feature.set("pos", _strings(pos))
    feature.set("size", _strings(size))
    feature.set("selresult", True)


def _union_selection(component, tag, label, inputs, entity_dim=3):
    component.selection().create(tag, "Union")
    selection = component.selection(tag)
    selection.label(label)
    selection.geom("geom1", entity_dim)
    selection.set("input", _strings(inputs))


def _difference_selection(component, tag, label, add, subtract, entity_dim=3):
    component.selection().create(tag, "Difference")
    selection = component.selection(tag)
    selection.label(label)
    selection.geom("geom1", entity_dim)
    selection.set("add", _strings(add))
    selection.set("subtract", _strings(subtract))


def _box_selection(component, tag, label, entity_dim, bounds):
    component.selection().create(tag, "Box")
    selection = component.selection(tag)
    selection.label(label)
    selection.geom("geom1", entity_dim)
    selection.set("condition", "inside")
    for name, value in bounds.items():
        selection.set(name, str(value))


def _refractive_index_material(component, tag, label, selection, n_value, k_value="0"):
    component.material().create(tag, "Common")
    material = component.material(tag)
    material.label(label)
    material.selection().named(selection)
    material.propertyGroup().create("RefractiveIndex", "RefractiveIndex", "Refractive index")
    n_tensor = [n_value, "0", "0", "0", n_value, "0", "0", "0", n_value]
    k_tensor = [k_value, "0", "0", "0", k_value, "0", "0", "0", k_value]
    material.propertyGroup("RefractiveIndex").set("n", _strings(n_tensor))
    material.propertyGroup("RefractiveIndex").set("ki", _strings(k_tensor))


def _phase_library(design):
    by_id = {entry["id"]: entry for entry in design["phase_library"]}
    order = [
        "phase_plus_2pi_3_seed",
        "phase_zero_seed",
        "phase_minus_2pi_3_seed",
    ]
    return [by_id[name] for name in order]


def ensure_comsol_runtime():
    if _MPH_ERROR is not None:
        raise RuntimeError("MPh is required to build the COMSOL structure") from _MPH_ERROR
    if _JPYPE_ERROR is not None:
        raise RuntimeError("JPype is required to build the COMSOL structure") from _JPYPE_ERROR
    if not any(shutil.which(name) for name in ["comsol", "comsolmphserver", "comsolbatch"]):
        raise RuntimeError("COMSOL executables are not on PATH")


def build_structure(jmodel, config, supercell_count=None, add_physics=True, build_mesh=False):
    design = config["design"]
    if design["task"] != "beam_deflector":
        raise ValueError("The first COMSOL structure builder supports beam_deflector only")
    library = _phase_library(design)
    cells = int(supercell_count or design["supercell_count"])
    include_substrate = bool(design.get("include_substrate", True))
    if cells < 1:
        raise ValueError("supercell_count must be positive")

    _set_parameter(jmodel, "lambda0", design["wavelength_um"], "um", "vacuum wavelength")
    _set_parameter(jmodel, "freq0", "c_const/lambda0", description="optical frequency")
    _set_parameter(jmodel, "wg_w", design["waveguide_width_um"], "um", "Si waveguide width")
    _set_parameter(jmodel, "wg_h", design["waveguide_height_um"], "um", "Si waveguide height")
    _set_parameter(jmodel, "box_h", design["box_thickness_um"], "um", "buried oxide thickness")
    _set_parameter(jmodel, "sub_h", design.get("substrate_thickness_um", 1.0), "um", "modeled Si handle thickness")
    _set_parameter(jmodel, "Lambda", design["supercell_period_um"], "um", "three-atom supercell period")
    _set_parameter(jmodel, "atom_pitch", "Lambda/3", description="meta-atom center spacing")
    _set_parameter(jmodel, "n_cells", cells, description="number of modeled supercells")
    _set_parameter(jmodel, "array_L", "n_cells*Lambda", description="metasurface length")
    _set_parameter(jmodel, "port_buffer", design.get("port_buffer_um", 2.0), "um", "bare waveguide at each end")
    _set_parameter(jmodel, "device_L", "array_L+2*port_buffer", description="total modeled length")
    _set_parameter(jmodel, "domain_w", design.get("computational_width_um", 4.0), "um", "transverse domain width")
    _set_parameter(jmodel, "air_h", design.get("air_height_um", 3.0), "um", "air height above BOX")
    _set_parameter(jmodel, "monitor_z", design.get("monitor_height_um", 1.0), "um", "monitor height above antenna")
    _set_parameter(jmodel, "t_au", design["metal_thickness_um"], "um", "each gold layer thickness")
    _set_parameter(jmodel, "t_d", design["dielectric_thickness_um"], "um", "antenna SiO2 spacer thickness")
    _set_parameter(jmodel, "array_x0", "-array_L/2", description="first supercell origin")
    _set_parameter(jmodel, "sel_tol", "1[nm]", description="boundary selection tolerance")
    _set_parameter(jmodel, "n_air", config["materials"]["air"]["n"])
    _set_parameter(jmodel, "n_si", config["materials"]["silicon"]["n"])
    _set_parameter(jmodel, "n_sio2", config["materials"]["silica"]["n"])
    _set_parameter(jmodel, "n_au", design.get("gold_n_initial", 0.55), description="Au n seed at 1550 nm")
    _set_parameter(jmodel, "k_au", design.get("gold_k_initial", 11.5), description="Au extinction seed at 1550 nm")
    _set_parameter(jmodel, "mesh_bulk", design.get("bulk_mesh_max_um", 0.25), "um", "air-domain mesh maximum")
    _set_parameter(jmodel, "mesh_sio2", design.get("dielectric_mesh_max_um", 0.12), "um", "SiO2 mesh maximum")
    _set_parameter(jmodel, "mesh_si", design.get("silicon_mesh_max_um", 0.05), "um", "silicon mesh maximum")
    _set_parameter(jmodel, "mesh_metal", design.get("metal_mesh_max_um", 0.015), "um", "local antenna mesh maximum")

    phase_suffixes = ["p", "z", "m"]
    for suffix, atom in zip(phase_suffixes, library):
        _set_parameter(jmodel, f"lx_{suffix}", atom["lx_um"], "um", f"{atom['id']} x size")
        _set_parameter(jmodel, f"ly_{suffix}", atom["ly_um"], "um", f"{atom['id']} y size")

    jmodel.component().create("comp1", True)
    component = jmodel.component("comp1")
    component.label("3D guided-wave-driven metasurface")
    component.geom().create("geom1", 3)
    geom = component.geom("geom1")
    geom.label("SOI waveguide and Au-SiO2-Au meta-atoms")
    geom.lengthUnit("um")

    _block(
        geom,
        "air_domain",
        "air computational domain",
        ["-device_L/2", "-domain_w/2", "0"],
        ["device_L", "domain_w", "air_h"],
    )
    _block(
        geom,
        "box",
        "3 um buried silicon dioxide",
        ["-device_L/2", "-domain_w/2", "-box_h"],
        ["device_L", "domain_w", "box_h"],
    )
    if include_substrate:
        _block(
            geom,
            "substrate",
            "silicon handle (truncated)",
            ["-device_L/2", "-domain_w/2", "-box_h-sub_h"],
            ["device_L", "domain_w", "sub_h"],
        )
    _block(
        geom,
        "waveguide",
        "600 nm x 220 nm silicon ridge",
        ["-device_L/2", "-wg_w/2", "0"],
        ["device_L", "wg_w", "wg_h"],
    )

    bottom_au = []
    spacers = []
    top_au = []
    atom_domains = []
    total_atoms = 3 * cells
    for index in range(total_atoms):
        suffix = phase_suffixes[index % 3]
        serial = f"{index:03d}"
        x_center = f"array_x0+({index}+0.5)*atom_pitch"
        x_corner = f"{x_center}-lx_{suffix}/2"
        y_corner = f"-ly_{suffix}/2"
        layer_specs = [
            (f"au_b_{serial}", "bottom Au", "wg_h", "t_au", bottom_au),
            (f"sp_{serial}", "SiO2 spacer", "wg_h+t_au", "t_d", spacers),
            (f"au_t_{serial}", "top Au", "wg_h+t_au+t_d", "t_au", top_au),
        ]
        for tag, layer_name, z_pos, thickness, collector in layer_specs:
            _block(
                geom,
                tag,
                f"atom {index:03d} {layer_name} phase {suffix}",
                [x_corner, y_corner, z_pos],
                [f"lx_{suffix}", f"ly_{suffix}", thickness],
            )
            selection_name = f"geom1_{tag}_dom"
            collector.append(selection_name)
            atom_domains.append(selection_name)

    geom.feature("fin").set("action", "union")
    geom.run()

    silicon_inputs = ["geom1_waveguide_dom"]
    if include_substrate:
        silicon_inputs.append("geom1_substrate_dom")
    _union_selection(component, "sel_si", "silicon waveguide and handle", silicon_inputs)
    _union_selection(component, "sel_au", "all gold antenna layers", bottom_au + top_au)
    _union_selection(component, "sel_sio2", "BOX and antenna SiO2", ["geom1_box_dom"] + spacers)
    _union_selection(component, "sel_atoms", "all antenna domains", atom_domains)
    _union_selection(component, "sel_non_air", "all non-air domains", ["sel_si", "sel_au", "sel_sio2"])
    _difference_selection(component, "sel_air", "air only", ["geom1_air_domain_dom"], ["sel_non_air"])

    domain_bottom = "-box_h-sub_h" if include_substrate else "-box_h"
    full_boundary = {
        "xmin": "-device_L/2-sel_tol",
        "xmax": "device_L/2+sel_tol",
        "ymin": "-domain_w/2-sel_tol",
        "ymax": "domain_w/2+sel_tol",
        "zmin": f"{domain_bottom}-sel_tol",
        "zmax": "air_h+sel_tol",
    }
    left = dict(full_boundary, xmax="-device_L/2+sel_tol")
    right = dict(full_boundary, xmin="device_L/2-sel_tol")
    top = dict(full_boundary, zmin="air_h-sel_tol")
    bottom = dict(full_boundary, zmax=f"{domain_bottom}+sel_tol")
    side_minus = dict(full_boundary, ymax="-domain_w/2+sel_tol")
    side_plus = dict(full_boundary, ymin="domain_w/2-sel_tol")
    _box_selection(component, "sel_port_in", "input port x-min", 2, left)
    _box_selection(component, "sel_port_out", "output port x-max", 2, right)
    _box_selection(component, "sel_open_top", "top scattering boundary", 2, top)
    _box_selection(component, "sel_open_bottom", "bottom scattering boundary", 2, bottom)
    _box_selection(component, "sel_open_ymin", "negative-y scattering boundary", 2, side_minus)
    _box_selection(component, "sel_open_ymax", "positive-y scattering boundary", 2, side_plus)
    _union_selection(
        component,
        "sel_open",
        "all non-port exterior boundaries",
        ["sel_open_top", "sel_open_bottom", "sel_open_ymin", "sel_open_ymax"],
        entity_dim=2,
    )

    _refractive_index_material(component, "mat_air", "Air", "sel_air", "n_air")
    _refractive_index_material(component, "mat_si", "Silicon", "sel_si", "n_si")
    _refractive_index_material(component, "mat_sio2", "Silicon dioxide", "sel_sio2", "n_sio2")
    _refractive_index_material(component, "mat_au", "Gold seed optical constants", "sel_au", "n_au", "k_au")

    if add_physics:
        component.physics().create("ewfd", "ElectromagneticWavesFrequencyDomain", "geom1")
        physics = component.physics("ewfd")
        physics.label("Electromagnetic Waves, Frequency Domain")
        physics.create("port1", "Port", 2)
        physics.feature("port1").label("TE00 numeric input port")
        physics.feature("port1").selection().named("sel_port_in")
        physics.feature("port1").set("PortType", "Numeric")
        physics.feature("port1").set("PortExcitation", "on")
        physics.create("port2", "Port", 2)
        physics.feature("port2").label("numeric output port")
        physics.feature("port2").selection().named("sel_port_out")
        physics.feature("port2").set("PortType", "Numeric")
        physics.feature("port2").set("PortExcitation", "off")
        physics.create("sctr1", "Scattering", 2)
        physics.feature("sctr1").label("top, bottom, and transverse scattering boundaries")
        physics.feature("sctr1").selection().named("sel_open")

    component.mesh().create("mesh1")
    mesh = component.mesh("mesh1")
    mesh.label("paper-seeded wave-optics mesh")
    mesh.automatic(False)
    mesh.feature("size").set("custom", "on")
    mesh.feature("size").set("hmax", "mesh_bulk")
    mesh.feature("size").set("hmin", "mesh_metal/3")
    mesh.create("size_sio2", "Size")
    mesh.feature("size_sio2").selection().named("sel_sio2")
    mesh.feature("size_sio2").set("custom", "on")
    mesh.feature("size_sio2").set("hmax", "mesh_sio2")
    mesh.feature("size_sio2").set("hmin", "mesh_metal/3")
    mesh.create("size_si", "Size")
    mesh.feature("size_si").selection().named("geom1_waveguide_dom")
    mesh.feature("size_si").set("custom", "on")
    mesh.feature("size_si").set("hmax", "mesh_si")
    mesh.feature("size_si").set("hmin", "mesh_metal/3")
    mesh.create("size_atoms", "Size")
    mesh.feature("size_atoms").selection().named("sel_atoms")
    mesh.feature("size_atoms").set("custom", "on")
    mesh.feature("size_atoms").set("hmax", "mesh_metal")
    mesh.feature("size_atoms").set("hmin", "mesh_metal/4")
    if build_mesh:
        mesh.run()

    if add_physics:
        jmodel.study().create("std1")
        jmodel.study("std1").label("1550 nm forward TE00 frequency-domain study")
        jmodel.study("std1").create("bmode1", "BoundaryModeAnalysis")
        jmodel.study("std1").feature("bmode1").label("input-port TE00 boundary mode")
        jmodel.study("std1").feature("bmode1").set("PortName", "1")
        jmodel.study("std1").feature("bmode1").set("modeFreq", "freq0")
        jmodel.study("std1").feature("bmode1").set("neigs", "1")
        jmodel.study("std1").feature("bmode1").set("shift", "2.53")
        jmodel.study("std1").create("bmode2", "BoundaryModeAnalysis")
        jmodel.study("std1").feature("bmode2").label("output-port TE00 boundary mode")
        jmodel.study("std1").feature("bmode2").set("PortName", "2")
        jmodel.study("std1").feature("bmode2").set("modeFreq", "freq0")
        jmodel.study("std1").feature("bmode2").set("neigs", "1")
        jmodel.study("std1").feature("bmode2").set("shift", "2.53")
        jmodel.study("std1").create("freq", "Frequency")
        jmodel.study("std1").feature("freq").set("plist", "freq0")

    jmodel.label("guided_wave_metasurface_structure.mph")
    return {
        "supercell_count": cells,
        "atom_count": total_atoms,
        "layer_block_count": 3 * total_atoms,
        "array_length_um": cells * float(design["supercell_period_um"]),
        "device_length_um": cells * float(design["supercell_period_um"])
        + 2.0 * float(design.get("port_buffer_um", 2.0)),
        "physics_added": bool(add_physics),
        "mesh_built": bool(build_mesh),
        "silicon_handle_included": include_substrate,
        "phase_seed_status": "figure_estimate; recalibrate with the single-atom sweep",
    }


def create_and_save(config, output_directory, supercell_count=None, add_physics=True, build_mesh=False):
    ensure_comsol_runtime()
    os.makedirs(output_directory, exist_ok=True)
    if os.name == "nt":
        mph.option("session", os.environ.get("GWM_WORKFLOW_MPH_SESSION", "client-server"))
    client = mph.start(version=os.environ.get("COMSOL_VERSION"))
    model = client.create("guided_wave_metasurface_structure")
    try:
        summary = build_structure(
            model.java,
            config,
            supercell_count=supercell_count,
            add_physics=add_physics,
            build_mesh=build_mesh,
        )
        mph_path = os.path.abspath(os.path.join(output_directory, "guided_wave_metasurface_structure.mph"))
        java_path = os.path.abspath(os.path.join(output_directory, "GuidedWaveMetasurfaceStructure.java"))
        summary_path = os.path.abspath(os.path.join(output_directory, "structure_summary.json"))
        model.save(mph_path)
        model.save(java_path)
        with open(summary_path, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        summary.update({"mph_path": mph_path, "java_path": java_path, "summary_path": summary_path})
        return summary
    finally:
        client.remove(model)
