import copy
import json


SUPPORTED_TASKS = {"beam_deflector", "metalens"}


def load_config(path):
    with open(path, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    validate_config(config)
    return config


def design_with_params(config, params):
    design = copy.deepcopy(config["design"])
    for key, value in params.items():
        if key not in design:
            raise ValueError(f"Unknown design override: {key}")
        design[key] = float(value)
    return design


def validate_config(config):
    for section in ["metadata", "design", "materials", "simulation"]:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")

    design = config["design"]
    task = design.get("task")
    if task not in SUPPORTED_TASKS:
        raise ValueError(f"design.task must be one of {sorted(SUPPORTED_TASKS)}")

    positive = [
        "wavelength_um",
        "effective_index_initial",
        "waveguide_width_um",
        "waveguide_height_um",
        "box_thickness_um",
        "atom_pitch_um",
    ]
    for name in positive:
        if float(design.get(name, 0.0)) <= 0.0:
            raise ValueError(f"design.{name} must be positive")

    if task == "beam_deflector":
        for name in ["supercell_period_um", "atoms_per_supercell", "supercell_count"]:
            if float(design.get(name, 0.0)) <= 0.0:
                raise ValueError(f"design.{name} must be positive")
    else:
        for name in ["focal_length_um", "aperture_um"]:
            if float(design.get(name, 0.0)) <= 0.0:
                raise ValueError(f"design.{name} must be positive")

    library = design.get("phase_library", [])
    if len(library) < 3:
        raise ValueError("design.phase_library requires at least three entries")
    for atom in library:
        for name in ["id", "lx_um", "ly_um", "phase_rad", "status"]:
            if name not in atom:
                raise ValueError(f"Phase-library entry is missing {name}")

    mesh = config["simulation"].get("mesh", {})
    if int(mesh.get("elements_per_wavelength_min", 0)) < 10:
        raise ValueError("The paper requires at least 10 mesh steps per wavelength")
