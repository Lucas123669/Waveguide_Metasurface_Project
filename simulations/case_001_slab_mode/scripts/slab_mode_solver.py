"""1D multilayer slab-waveguide mode solver (TE/TM) using the transfer-matrix method.

Structure (top to bottom): air / PMMA 0.30 um / Si3N4 0.30 um / SiO2 (semi-infinite).
Only numpy is required.
"""

import numpy as np

LAMBDA0 = 1.55  # um
K0 = 2 * np.pi / LAMBDA0

LAYERS = [
    ("air", 1.00, None),
    ("PMMA", 1.48, 0.30),
    ("Si3N4", 2.00, 0.30),
    ("SiO2", 1.44, None),
]
N_TOP = LAYERS[0][1]
N_BOT = LAYERS[-1][1]


def mode_condition(neff, tm=True):
    """Return the transfer-matrix mode condition f(neff); guided modes are roots."""
    M = np.eye(2, dtype=complex)
    for _, n, d in LAYERS[1:-1]:
        k = K0 * np.sqrt(n**2 - neff**2 + 0j)
        kk = k / (n**2) if tm else k
        m = np.array(
            [
                [np.cos(k * d), np.sin(k * d) / kk],
                [-kk * np.sin(k * d), np.cos(k * d)],
            ]
        )
        M = m @ M
    gt = K0 * np.sqrt(neff**2 - N_TOP**2 + 0j)
    gb = K0 * np.sqrt(neff**2 - N_BOT**2 + 0j)
    gt_ = gt / (N_TOP**2) if tm else gt
    gb_ = gb / (N_BOT**2) if tm else gb
    return M[1, 0] + M[1, 1] * gt_ + gb_ * (M[0, 0] + M[0, 1] * gt_)


def find_modes(tm=True, nmin=1.44 + 1e-6, nmax=2.00 - 1e-6, npts=12000):
    roots = []
    xs = np.linspace(nmin, nmax, npts)
    prev_x, prev_f = xs[0], mode_condition(xs[0], tm)
    for x in xs[1:]:
        f = mode_condition(x, tm)
        if prev_f.real * f.real < 0 and abs(f.imag) < 1e-3:
            a, b, fa = prev_x, x, prev_f.real
            for _ in range(120):
                mid = 0.5 * (a + b)
                fm = mode_condition(mid, tm).real
                if fa * fm <= 0:
                    b = mid
                else:
                    a, fa = mid, fm
            roots.append(0.5 * (a + b))
        prev_x, prev_f = x, f
    return roots


def main():
    print(f"lambda0 = {LAMBDA0} um")
    for tm, name in ((False, "TE"), (True, "TM")):
        for neff in find_modes(tm=tm):
            print(
                f"{name}0: neff = {neff:.4f}, "
                f"lambda_guided = {LAMBDA0 / neff:.3f} um"
            )


if __name__ == "__main__":
    main()
