import math


TAU = 2.0 * math.pi


def wrap_phase(phase_rad):
    """Wrap a phase to [-pi, pi)."""
    return (float(phase_rad) + math.pi) % TAU - math.pi


def circular_phase_error(first_rad, second_rad):
    return abs(wrap_phase(float(first_rad) - float(second_rad)))


def propagation_constant(wavelength_um, effective_index):
    return TAU * float(effective_index) / float(wavelength_um)


def beam_deflection(
    wavelength_um,
    effective_index,
    supercell_period_um,
    reported_angle_sign=1.0,
):
    """Return the paper's phase-matching prediction for both launch directions.

    `physical_angle_deg` follows kx = beta - 2*pi/Lambda. The paper's plotted
    angular coordinate uses the opposite sign for the supplied seed config, so
    `reported_angle_sign` is explicit rather than hidden in the formula.
    """
    wavelength_um = float(wavelength_um)
    effective_index = float(effective_index)
    period_um = float(supercell_period_um)
    normalized_forward_kx = effective_index - wavelength_um / period_um
    forward_radiates = abs(normalized_forward_kx) <= 1.0
    physical_angle_deg = None
    reported_angle_deg = None
    if forward_radiates:
        physical_angle_deg = math.degrees(math.asin(normalized_forward_kx))
        reported_angle_deg = float(reported_angle_sign) * physical_angle_deg

    normalized_reverse_kx = -effective_index - wavelength_um / period_um
    return {
        "normalized_forward_kx": normalized_forward_kx,
        "forward_radiates": forward_radiates,
        "physical_angle_deg": physical_angle_deg,
        "reported_angle_deg": reported_angle_deg,
        "normalized_reverse_kx": normalized_reverse_kx,
        "reverse_radiates": abs(normalized_reverse_kx) <= 1.0,
    }


def metalens_phase(x_um, wavelength_um, effective_index, focal_length_um):
    """Equation (2) of the paper, wrapped to [-pi, pi)."""
    x_um = float(x_um)
    k0 = TAU / float(wavelength_um)
    beta = propagation_constant(wavelength_um, effective_index)
    raw = -k0 * math.sqrt(x_um * x_um + float(focal_length_um) ** 2) - beta * x_um
    return wrap_phase(raw)


def nearest_phase_atom(target_phase_rad, phase_library):
    atom = min(
        phase_library,
        key=lambda item: circular_phase_error(target_phase_rad, item["phase_rad"]),
    )
    result = dict(atom)
    result["phase_error_rad"] = circular_phase_error(
        target_phase_rad, atom["phase_rad"]
    )
    return result


def _centered_positions(count, pitch_um):
    center = 0.5 * (count - 1)
    return [(index - center) * pitch_um for index in range(count)]


def build_phase_targets(design):
    task = design["task"]
    library = design["phase_library"]
    pitch_um = float(design["atom_pitch_um"])
    targets = []

    if task == "beam_deflector":
        atoms_per_supercell = int(design["atoms_per_supercell"])
        supercells = int(design["supercell_count"])
        count = atoms_per_supercell * supercells
        positions = _centered_positions(count, pitch_um)
        phase_step = -TAU / atoms_per_supercell
        for index, x_um in enumerate(positions):
            target_phase = wrap_phase(-phase_step + (index % atoms_per_supercell) * phase_step)
            atom = nearest_phase_atom(target_phase, library)
            targets.append(
                {
                    "index": index,
                    "x_um": x_um,
                    "target_phase_rad": target_phase,
                    "atom_id": atom["id"],
                    "lx_um": atom["lx_um"],
                    "ly_um": atom["ly_um"],
                    "library_phase_rad": atom["phase_rad"],
                    "phase_error_rad": atom["phase_error_rad"],
                    "parameter_status": atom["status"],
                }
            )
        return targets

    count = max(1, int(round(float(design["aperture_um"]) / pitch_um)))
    for index, x_um in enumerate(_centered_positions(count, pitch_um)):
        target_phase = metalens_phase(
            x_um,
            design["wavelength_um"],
            design["effective_index_initial"],
            design["focal_length_um"],
        )
        atom = nearest_phase_atom(target_phase, library)
        targets.append(
            {
                "index": index,
                "x_um": x_um,
                "target_phase_rad": target_phase,
                "atom_id": atom["id"],
                "lx_um": atom["lx_um"],
                "ly_um": atom["ly_um"],
                "library_phase_rad": atom["phase_rad"],
                "phase_error_rad": atom["phase_error_rad"],
                "parameter_status": atom["status"],
            }
        )
    return targets
