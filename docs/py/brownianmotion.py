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

M_trac = 10 * m_bath
R_trac = 8.0e-8

dt = 1.0e-12  # s
spf = 10  # physics steps per animation frame
seed = 2  # fixed by default so a run is reproducible; the web UI can re-roll it


def init():
    global rng, n, mass, radius, pos, vel

    rng = np.random.default_rng(seed)

    # ---------------- state ----------------
    n = n_bath + 1  #total number of particles: index 0 is the tracer
    mass = np.concatenate(([M_trac], np.full(n_bath, m_bath)))
    radius = np.concatenate(([R_trac], np.full(n_bath, r_bath)))

    # grow the lattice until enough sites survive the tracer exclusion, otherwise
    # a big tracer or a large n_bath silently leaves pos shorter than mass/radius
    k = int(np.ceil(np.sqrt(n_bath * 1.6)))
    while True:
        gx, gy = np.meshgrid(np.linspace(0.05 * L, 0.95 * L, k), np.linspace(0.05 * L, 0.95 * L, k))
        spawnsites = np.column_stack([gx.ravel(), gy.ravel()]) #every possible site of current grid
        spawnsites = spawnsites[np.hypot(*(spawnsites - L / 2).T) > R_trac + 2 * r_bath] #sites clear of tracer
        if len(spawnsites) >= n_bath:
            break
        k += 2
    spawnsites = rng.permutation(spawnsites)[:n_bath] #chose some random bath spawn sites

    pos = np.vstack([[L / 2, L / 2], spawnsites]) #[L/2,L/2] is default tracer origin, so we just stack that with spawnsites to get a full array of all the initial particle positions

    # velocities: each species from its own Maxwell-Boltzmann
    vel = np.empty((n, 2)) #n rows for n particles, each row contains vx and vy
    vel[0] = rng.normal(0.0, np.sqrt(kB * T / M_trac), 2)  #tracer velocity    #syntax: rng.normal(mean, std, size of output)
    vel[1:] = rng.normal(0.0, np.sqrt(kB * T / m_bath), (n_bath, 2)) #1: - 1 onwards. bath particle velocities.
    vel -= (mass[:, None] * vel).sum(0) / mass.sum()  # calculate centre of mass velocity and subtract from all velocities, such that we are in the zero momentum frame at initialisation, so gas particles don't all drift apart immediately.


# ---------------- physics ----------------
def step():
    global pos  # needed: `pos +=` is an assignment, so Python would make it local
    pos += vel * dt #moves every particle in a straight line at constant velocity per step

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

def web_setup(n_bath_=n_bath, m_bath_=m_bath, r_bath_=r_bath,
              M_trac_=M_trac, R_trac_=R_trac, T_=T, seed_=seed):
    # defaults are bound at def time to the module values above, so a bare
    # web_setup() still rebuilds the standard run
    global n_bath, m_bath, r_bath, M_trac, R_trac, T, seed
    n_bath, seed = int(n_bath_), int(seed_)   # range inputs arrive as JSON floats
    m_bath, r_bath = float(m_bath_), float(r_bath_)
    M_trac, R_trac = float(M_trac_), float(R_trac_)
    T = float(T_)
    init()
    return {
        "L": L,
        "T": T,
        "dt": dt,          # so the UI can turn frames into simulated time
        "n_bath": n_bath,
        "m_bath": m_bath,
        "M_trac": M_trac,
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
