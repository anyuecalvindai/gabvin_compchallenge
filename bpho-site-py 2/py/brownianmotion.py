"""2D hard-disc gas with a heavy tracer -> Brownian motion.

Bath particles and the tracer collide elastically as hard discs.
Momentum transfer from the bath kicks the tracer along a random walk.

Physics from "brownianmotion.py"; the animation loop and drawing are done by
the JS layer, which calls step() through web_frame(). The state setup is
wrapped in init() so the web page's Reset button can rerun it.
"""

import numpy as np

kB = 1.380649e-23

# ---------------- parameters ----------------
L = 1.0e-6  # box side, m
T = 1000  # K

n_bath = 180
m_bath = 4.65e-26  # N2 molecule, kg
r_bath = 8.0e-9  # inflated ~50x over real N2 so collisions are frequent

M_trac = 0.1 * m_bath
R_trac = 8.0e-8

dt = 1.0e-12  # s
spf = 10  # physics steps per animation frame


def init():
    global rng, n, mass, radius, pos, vel

    rng = np.random.default_rng(2)

    # ---------------- state ----------------
    n = n_bath + 1  # index 0 is the tracer
    mass = np.concatenate(([M_trac], np.full(n_bath, m_bath)))
    radius = np.concatenate(([R_trac], np.full(n_bath, r_bath)))

    # positions: tracer at centre, bath on a jittered lattice that clears it
    k = int(np.ceil(np.sqrt(n_bath * 1.6)))
    gx, gy = np.meshgrid(np.linspace(0.05 * L, 0.95 * L, k),
                         np.linspace(0.05 * L, 0.95 * L, k))
    cand = np.column_stack([gx.ravel(), gy.ravel()])
    cand = cand[np.hypot(*(cand - L / 2).T) > R_trac + 2 * r_bath]
    cand = rng.permutation(cand)[:n_bath]

    pos = np.vstack([[L / 2, L / 2], cand])

    # velocities: each species from its own Maxwell-Boltzmann
    vel = np.empty((n, 2))
    vel[0] = rng.normal(0.0, np.sqrt(kB * T / M_trac), 2)
    vel[1:] = rng.normal(0.0, np.sqrt(kB * T / m_bath), (n_bath, 2))
    vel -= (mass[:, None] * vel).sum(0) / mass.sum()  # zero total MOMENTUM


# ---------------- physics ----------------
def step():
    global pos  # needed: `pos +=` is an assignment, so Python would make it local
    pos += vel * dt

    # walls: reflect, using abs() so a disc still overlapping can't double-flip
    lo = pos - radius[:, None] < 0.0
    hi = pos + radius[:, None] > L
    vel[lo] = np.abs(vel[lo])
    vel[hi] = -np.abs(vel[hi])
    np.clip(pos, radius[:, None], L - radius[:, None], out=pos)

    # pair overlaps: vectorised O(n^2) detection
    d = pos[:, None, :] - pos[None, :, :]
    dist2 = np.einsum('ijk,ijk->ij', d, d)
    Rsum = radius[:, None] + radius[None, :]
    ia, ib = np.nonzero(np.triu(dist2 < Rsum ** 2, 1))

    for a, b in zip(ia, ib):
        dist = np.sqrt(dist2[a, b])
        nhat = d[a, b] / dist  # unit vector from b to a
        vn = (vel[a] - vel[b]) @ nhat
        if vn >= 0.0:
            continue  # already separating, leave alone

        mu = mass[a] * mass[b] / (mass[a] + mass[b])
        J = 2.0 * mu * vn
        vel[a] -= (J / mass[a]) * nhat
        vel[b] += (J / mass[b]) * nhat

        # separate them, displacement inversely proportional to mass
        overlap = Rsum[a, b] - dist
        fa = mass[b] / (mass[a] + mass[b])
        pos[a] += fa * overlap * nhat
        pos[b] -= (1.0 - fa) * overlap * nhat


def kinetic_energy():
    return 0.5 * (mass * (vel ** 2).sum(1)).sum()


def momentum():
    return (mass[:, None] * vel).sum(0)


init()


# ---- adapter for the web UI ----

def web_setup():
    init()
    return {
        "L": L,
        "T": T,
        "n_bath": n_bath,
        "R_trac": R_trac,
        "r_bath": r_bath,
        "tracer": pos[0].tolist(),
        "bath": pos[1:].tolist(),
    }


def web_frame(substeps):
    for _ in range(int(substeps)):
        step()
    return {
        "tracer": pos[0].tolist(),
        "bath": np.round(pos[1:], 10).tolist(),   # 0.1 nm precision, well under a pixel
    }
