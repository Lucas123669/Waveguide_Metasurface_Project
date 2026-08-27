def build_model_plan(config):
    design = config["design"]
    task = design["task"]
    common = [
        {
            "stage": "waveguide_mode",
            "dimension": "2D cross-section",
            "physics": "Electromagnetic Waves, Frequency Domain / Mode Analysis",
            "outputs": ["TE00 effective index", "mode field", "mode power normalization"],
        },
        {
            "stage": "meta_atom_library",
            "dimension": "3D",
            "physics": "Electromagnetic Waves, Frequency Domain",
            "geometry": "one Au/SiO2/Au nanobar on the silicon ridge",
            "sweep": {
                "lx_um": design["meta_atom_sweep"]["lx_um"],
                "ly_um": design["meta_atom_sweep"]["ly_um"],
            },
            "outputs": [
                "complex extracted Ey/Ez on a monitor plane",
                "phase relative to the guided field below the atom",
                "extracted amplitude and absorbed power",
            ],
        },
    ]
    if task == "beam_deflector":
        common.append(
            {
                "stage": "full_device",
                "dimension": "3D",
                "geometry": "three-atom supercell repeated along the ridge waveguide",
                "checks": [
                    "forward/backward guided excitation",
                    "near-to-far/Fourier-space output angle",
                    "extracted, transmitted, reflected, and absorbed power balance",
                    "supercell-count convergence",
                ],
            }
        )
    else:
        common.append(
            {
                "stage": "full_device",
                "dimension": "3D",
                "geometry": "library-mapped spatial phase profile on a 500 nm x 1.5 um waveguide",
                "checks": [
                    "xz intensity map",
                    "on-axis peak at the designed focus",
                    "focal spot FWHM and focusing efficiency",
                    "aperture and mesh convergence",
                ],
            }
        )
    return {
        "paper": config["metadata"]["citation"],
        "task": task,
        "parameter_policy": "paper_exact > calibrated COMSOL value > figure_estimate > assumption",
        "stages": common,
    }
