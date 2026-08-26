# Paper parameter register

Source: X. Guo, Y. Ding, X. Chen, Y. Duan, and X. Ni, “Molding
free-space light with guided wave-driven metasurfaces,” *Science Advances*
**6**, eabb4142 (2020), DOI 10.1126/sciadv.abb4142.

## Passive straight-waveguide model

| Quantity | Value used | Status | Evidence / action |
|---|---:|---|---|
| Design wavelength | 1550 nm | `paper_exact` | Figs. 2-4 and Simulation methods |
| Deflector Si waveguide | 220 nm high, 600 nm wide | `paper_exact` | Fig. 3 caption |
| Metalens Si waveguide | 500 nm high, 1.5 um wide | `paper_exact` | Fig. 4 caption |
| Buried SiO2 | 3 um | `paper_exact` | Materials and Methods |
| Meta-atom stack | Au/SiO2/Au | `paper_exact` | Main text and Fig. 2 |
| Each stack layer | 30 nm | `paper_exact` | Fig. 2 caption |
| Antenna sweep range | lx 90-130 nm; ly 100-400 nm | `figure_estimate` | Fig. 2B axes; use a denser local resweep near selected points |
| Three phase targets | +2pi/3, 0, -2pi/3 | `paper_exact` | Fig. 2C |
| Three seed geometries | (110,190), (100,275), (110,295) nm | `figure_estimate` | Read from Fig. 2B; mapping must be recalibrated in COMSOL |
| Deflector supercell | 575 nm, 3 atoms | `paper_exact` | Fig. 3B and main text |
| Numerical focal length | 5 um | `paper_exact` | Fig. 4A |
| Experimental focal length | 225 um | `paper_exact` | Fig. 4B |
| FEM element order | third order | `paper_exact` | Simulation methods |
| Mesh density | at least 10 steps/wavelength | `paper_exact` | Simulation methods |
| Metal-device efficiency ceiling | about 9% | `paper_exact` | Main text |
| Proposed dielectric ceiling | up to about 80% with enough cells | `paper_exact` | Main text; not the fabricated Au design |
| Initial TE00 effective index | 2.4 (deflector), 3.1 (metalens) | `assumption` | Replace with COMSOL mode-analysis results before full-device solve |

The sign of the angle plotted in Fig. 3 is opposite to the internal
`kx = beta - 2*pi/Lambda` convention used in the framework. The config stores
that coordinate choice explicitly as `reported_angle_sign = -1`.

## Values missing from the supplied main PDF

- Exact complex optical constants/interpolation datasets used for Au, Si, and
  SiO2.
- Exact trapezoidal sidewall angles and the final three fabricated antenna
  dimensions.
- Air-domain, port, monitor-plane, and PML distances.
- Exact number of supercells/aperture samples in each simulated device.
- Detailed amplitude normalization used to produce the phase map.

These are calibration variables, not silently fixed paper facts. Record every
resolved value in a new `configs/*_calibrated.json` rather than overwriting the
paper-seed configs.

## Second-stage OAM model

The main paper gives a 9 um diameter, 1.1 um wide microring; a 500 nm InGaAsP
MQW layer on 1 um InP; four Au/Si/Au atoms per supercell; 58 supercells; WGM
order M=59; and the relation `l = M - N`. The atoms are offset by 140 nm from
the waveguide center. This stage is postponed until the passive meta-atom
library and far-field extraction are converged.
