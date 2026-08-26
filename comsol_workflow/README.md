# Guided-wave-driven metasurface reproduction workflow

This project is an initial COMSOL automation framework for reproducing Guo
et al., *Science Advances* **6**, eabb4142 (2020), “Molding free-space light
with guided wave-driven metasurfaces”. It follows the configuration/backend/
workspace pattern already used by the sibling `bilayer-grating-workflow` and
`coupler` projects.

## Latest reproduced model

The current release contains the corrected right-forward beam deflector:

- 15 supercells, 45 meta-atoms, and 135 Au/SiO2/Au layers;
- target free-space propagation direction: `+45 deg` in the x-z plane;
- simulated angular-spectrum peak: `+45.0147 deg`;
- supercell period: `897.331 nm`;
- air-domain height doubled from `1.8 um` to `3.6 um`.

The reproducible COMSOL Java program, unsolved `.mph` model, processed field
data, plots, and run parameters are in
`comsol_models/beam_deflector_right45_15cells_air2x/`. The 923 MB solved COMSOL
file is intentionally excluded from GitHub; rerun the command in
[`docs/right45_air2x_result.md`](docs/right45_air2x_result.md) to regenerate it.

The first milestone is deliberately limited to the passive straight-waveguide
results in Figs. 2-4:

1. calibrate the Au/SiO2/Au meta-atom phase/amplitude library at 1550 nm;
2. reproduce the three-element, 575 nm supercell beam deflector;
3. reproduce the 5 um focal-length numerical metalens.

The active InGaAsP/InP microring OAM laser is a second-stage model because it
adds gain, azimuthal eigenmode tracking, and a substantially larger 3D solve.

## Layout

```text
gwm_workflow/
  config.py          Configuration loading and validation
  phase_design.py    Steering and metalens phase equations
  model_plan.py      Machine-readable COMSOL construction plan
  results.py         Backend result data structure
  backends.py        Mock and external COMSOL backends
  workflow.py        Candidate/target generation and artifact writing
configs/
  beam_deflector_1550nm.json
  metalens_1550nm.json
docs/
  paper_parameter_register.md
  reproduction_plan.md
  comsol_model_tree.md
scripts/
  plan_model.py
  build_phase_targets.py
  run_single.py
  comsol_adapter.py
tests/
```

## Quick checks without COMSOL

From this directory:

```powershell
python tests\test_phase_design.py
python tests\test_workflow_mock.py
python scripts\plan_model.py --config configs\beam_deflector_1550nm.json
python scripts\build_phase_targets.py --config configs\beam_deflector_1550nm.json
python scripts\run_single.py --config configs\beam_deflector_1550nm.json --backend mock
python scripts\run_single.py --config configs\metalens_1550nm.json --backend mock
```

Build an inspectable COMSOL 3D structure model without solving it:

```powershell
python scripts\build_comsol_structure.py
```

This writes `guided_wave_metasurface_structure.mph`, the COMSOL-exported
`GuidedWaveMetasurfaceStructure.java`, and `structure_summary.json` under
`comsol_models/beam_deflector_structure/`. Use `--supercells 3` for a smaller
geometry check and add `--build-mesh` only after the geometry/material
selections have been inspected in the COMSOL GUI.

The generated model and native COMSOL commands are documented in
[`docs/comsol_structure_program.md`](docs/comsol_structure_program.md).

Outputs are written below `workspaces/` by default. Override the location with
`GWM_WORKFLOW_WORKSPACES_DIR`.

## COMSOL handoff

The COMSOL backend is template-driven so the first calibrated model can remain
inspectable in the GUI. Build the model tree described in
[`docs/comsol_model_tree.md`](docs/comsol_model_tree.md), save it as an `.mph`
file, and set `simulation.comsol.template_model` in the selected config. The
adapter then sets named parameters, runs the configured study, evaluates the
configured global expressions, and saves the solved `.mph` and `.java` files.

```powershell
where comsol
python -c "import mph, jpype; print('COMSOL Python bridge OK')"
python scripts\run_single.py --config configs\beam_deflector_1550nm.json --backend comsol
```

Until a calibrated template is supplied, `--backend comsol` stops with an
explicit missing-template error. The `mock` output is only a pipeline/theory
check and is not an electromagnetic prediction.

## Parameter-status rule

Every paper-derived value is classified in
[`docs/paper_parameter_register.md`](docs/paper_parameter_register.md) as one
of:

- `paper_exact`: stated numerically in the article;
- `figure_estimate`: read approximately from a plotted figure;
- `assumption`: an initial value requiring COMSOL calibration;
- `derived`: calculated from another registered value.

This distinction is important here because the supplied desktop folder does
not contain the paper's own supplementary PDF, and the main article does not
publish every antenna and boundary-domain dimension.
