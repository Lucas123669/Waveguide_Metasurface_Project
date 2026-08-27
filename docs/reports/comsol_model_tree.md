# COMSOL model tree for the first calibrated seed

Use Wave Optics -> Electromagnetic Waves, Frequency Domain (`ewfd`) in 3D.
Keep the tags below stable so `scripts/comsol_adapter.py` can drive the saved
template reproducibly.

## Global definitions

Parameters:

- `lambda0`, `freq0=c_const/lambda0`;
- `wg_w`, `wg_h`, `box_h`;
- `lx`, `ly`, `t_au=30[nm]`, `t_sio2=30[nm]`;
- `Lambda=575[nm]`, `atom_pitch=Lambda/3`;
- air/PML/monitor distances, each with a convergence suffix in the name.

Functions/materials:

- wavelength-dependent Au optical data (COMSOL library or an explicitly
  cited imported table);
- Si and SiO2 optical data at the same wavelength;
- variables `gwm_eta`, `gwm_theta_deg`, and later `gwm_focal_z` for automated
  evaluation.

## Component 1: `mode_2d`

1. Cross-section of Si ridge on 3 um BOX with air above.
2. Numeric port/mode-analysis boundaries spanning the full transverse domain.
3. Mode Analysis at 1550 nm; select TE00 by field profile and largest core
   confinement, not only by mode number.
4. Export `neff`, the complex mode field, and power normalization.

Acceptance check: mesh refinement changes Re(neff) by less than 1e-4.

## Component 2: `atom_3d`

1. Finite ridge waveguide with input/output ports and an air box.
2. One Au/SiO2/Au nanobar centered on the ridge; preserve the three separate
   layers and add trapezoidal sidewalls only after the rectangular seed works.
3. Scattering boundaries plus PML on open faces; exclude port faces from PML.
4. A monitor plane above the antenna and a reference point/line immediately
   below it in the guided field.
5. Frequency Domain study at 1550 nm, driven by the forward TE00 port mode.
6. Parametric sweep over `lx` and `ly` using the ranges in the JSON config.

Extract the complex overlap of the monitor field with the chosen free-space
polarization. Compute phase relative to the local guided reference and store
amplitude, radiated power, transmitted port power, reflected port power, and
ohmic loss. The balance error must be reported.

## Component 3: `device_3d`

For the deflector, form a three-atom supercell and repeat it along x. For the
metalens, import `phase_targets.csv` and instantiate the selected library atom
at each x coordinate.

Required studies:

- `std1`: forward TE00 excitation;
- `std_reverse`: backward TE00 excitation;
- optional wavelength sweep after the 1550 nm seed converges.

Required datasets/results:

- xz field slice corresponding to Figs. 2D or 4A;
- near-to-far/Fourier-space intensity and peak angle;
- port transmission/reflection;
- upward radiated flux, material absorption, and power-balance residual;
- mesh and domain-size convergence table.

The first successful GUI-inspected model should be saved under
`comsol_models/` and referenced by a new calibrated config. Do not make the
unverified seed config point to a model that has not passed these checks.
