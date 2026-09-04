# Reproduction plan

## 1. Freeze the scope and evidence

Start with Figs. 2-4 only. Preserve the supplied paper PDF separately and use
`paper_parameter_register.md` as the single parameter ledger. Do not start the
microring laser until straight-waveguide phase extraction and power balance
are reliable.

## 2. Verify the automation environment

1. Confirm COMSOL Wave Optics is licensed and `comsol`, `comsolbatch`, and
   `comsolmphserver` are visible on `PATH`.
2. Activate Python 3.10 with `mph` and `jpype1`.
3. Run both pure-Python test files and a mock single run.
4. Generate `model_plan.json` and `phase_targets.csv`; archive both with every
   later calibrated configuration.

## 3. Calibrate the bare waveguide

1. Build a 2D mode-analysis model for the 600 x 220 nm Si ridge on 3 um SiO2.
2. Solve the TE00 mode at 1550 nm and write its effective index into a copied
   calibrated config.
3. Repeat for the 1.5 um x 500 nm focusing waveguide.
4. Refine the mesh until effective-index change is below 1e-4.

## 4. Reproduce the meta-atom library

1. Build a 3D port-driven waveguide segment with one Au/SiO2/Au atom.
2. Use 30 nm per layer and sweep lx=90-130 nm, ly=100-400 nm.
3. Excite the forward TE00 mode. Monitor complex extracted field a few
   wavelengths above the waveguide and normalize it to the local guided field.
4. Plot amplitude and wrapped phase. Select at least three near-equal-amplitude
   atoms separated by 2pi/3.
5. Repeat with trapezoidal antenna sidewalls; the paper says this fabrication
   shape was included in the final model.
6. Converge metal-edge mesh, monitor height, air padding, and PML thickness.

Gate: obtain continuous ~2pi phase coverage and power-balance residual below
1% before building a full device.

## 5. Reproduce beam deflection

1. Arrange the calibrated +2pi/3, 0, -2pi/3 atoms in a 575 nm supercell.
2. Repeat 6, 12, and 18 supercells to establish finite-aperture convergence.
3. Solve forward and backward excitation separately.
4. Compare the far-field peak to `sin(theta) = neff - lambda/Lambda`, while
   retaining the explicit plotted-coordinate sign convention.
5. Confirm the backward case has no propagating free-space order.
6. Sweep wavelength and supercell period to recreate the trends in Fig. 3.
7. Report extracted efficiency and all loss channels; the metal design should
   not be judged against the proposed lossless 80% variant.

## 6. Reproduce focusing

1. Use `Delta phi(x) = -k0*sqrt(x^2+f^2) - beta*x` with f=5 um.
2. Replace each continuous phase target by the nearest calibrated library atom;
   use more than three phase levels if the library supports them.
3. Simulate the 500 nm x 1.5 um waveguide and compare the xz intensity map to
   Fig. 4A.
4. Measure focal position, x/z FWHM, focusing efficiency, and phase-quantization
   error. Converge aperture and mesh.
5. Only then scale to the experimental 225 um focal length.

## 7. Extend to the OAM laser

After passive validation, build the 9 um diameter InGaAsP/InP ring, calibrate
its M=59 WGM, add 58 four-atom supercells, and verify l=M-N=1 through the
far-field phase winding. Treat gain/lasing threshold as a separate study from
the passive cold-cavity OAM mode.

## 8. Reproducibility deliverables

For every accepted result retain the config, `phase_targets.csv`, solved
`.mph`, exported `.java`, mesh statistics, power-balance table, convergence
table, and result JSON. Never replace figure-estimated values in place; create
a new calibrated config with a short provenance note.
