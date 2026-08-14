# Brownian motion — how the simulation works

Reference notes for `brownianmotion.py` (desktop) and `docs/py/brownianmotion.py` (web).
Every number quoted as "measured" was obtained by running the code, not by reasoning about it.

> **On authorship:** these notes were written by an AI assistant to explain code you wrote.
> The simulation is yours; this document is a study aid, not your own prose. If any of it ends
> up in a submission or a judge conversation, put it in your own words first.

---

## 1. What is being simulated

A two-dimensional gas of hard discs in a square box. There are two species:

- **Bath particles** — many small discs, standing in for gas molecules.
- **Tracer** — one large, heavy disc, the "Brownian particle".

Discs collide elastically, like billiard balls. There are no forces at all between collisions —
no gravity, no attraction, no friction. A disc travels in a perfectly straight line until it
touches something.

The point of the model: the tracer is bombarded from all sides by bath particles. On average the
kicks cancel, but at any instant there is an imbalance, and that imbalance pushes the tracer
around on a random walk. That is Brownian motion — Einstein's 1905 explanation of why pollen
grains jiggle in water.

The tracer is big and heavy so that it takes many kicks to move it, which is what makes its path
look smooth and random rather than jerky.

---

## 2. The parameters

```python
L = 1.0e-6      # box side, 1 micrometre
T = 1000        # temperature, K

n_bath = 180
m_bath = 4.65e-26   # roughly an N2 molecule, kg
r_bath = 8.0e-9     # 8 nm - deliberately inflated

M_trac = 10 * m_bath
R_trac = 8.0e-8     # 80 nm, ten times the bath radius

dt = 1.0e-12    # timestep, 1 picosecond
spf = 10        # physics steps per animation frame
seed = 2        # fixed, so a run is reproducible
```

`r_bath` is about 50 times larger than a real N₂ molecule. That is on purpose. With realistic
radii the discs would almost never touch each other in a box this size, and nothing visible would
happen. Inflating the radius raises the collision rate to something you can watch.

The web version turns `n_bath`, `m_bath`, `r_bath`, `M_trac`, `R_trac`, `T` and `seed` into
sliders and buttons; the physics code is unchanged, it just reads the globals.

---

## 3. Setting up — `init()`

### 3.1 Masses and radii

```python
n = n_bath + 1
mass   = np.concatenate(([M_trac], np.full(n_bath, m_bath)))
radius = np.concatenate(([R_trac], np.full(n_bath, r_bath)))
```

Both are arrays of length `n`, with **index 0 always the tracer**. That convention holds
everywhere: `pos[0]`, `vel[0]`, `mass[0]`, `radius[0]`.

Because mass and radius are stored per particle rather than per species, the collision code is
already fully general. You could give every particle a different size with no change to `step()`.

### 3.2 Placing the bath particles

```python
k = int(np.ceil(np.sqrt(n_bath * 1.6)))
while True:
    gx, gy = np.meshgrid(np.linspace(0.05*L, 0.95*L, k), np.linspace(0.05*L, 0.95*L, k))
    spawnsites = np.column_stack([gx.ravel(), gy.ravel()])
    spawnsites = spawnsites[np.hypot(*(spawnsites - L/2).T) > R_trac + 2*r_bath]
    if len(spawnsites) >= n_bath:
        break
    k += 2
spawnsites = rng.permutation(spawnsites)[:n_bath]
pos = np.vstack([[L/2, L/2], spawnsites])
```

**Why a grid and not random positions?** If you scattered discs at random, some pairs would land
on top of each other, and you would need a rejection loop to fix it. A grid whose spacing is
bigger than two radii **cannot** produce an overlap. It is the standard way to start a hard-particle
simulation.

**Line by line:**

`k` is the grid size, so there are `k²` sites. The `1.6` is a safety factor — you need more sites
than particles because some get thrown away.

`np.linspace(0.05*L, 0.95*L, k)` gives `k` evenly spaced coordinates, inset 5% from each wall. The
inset matters: a disc centred exactly at `x = 0` already sticks through the wall.

`np.meshgrid` turns those two lists of coordinates into two 2D arrays that together name every
(x, y) point on the grid. `ravel` flattens them and `column_stack` pairs them up, so `spawnsites`
becomes a plain list of points with shape `(k², 2)`.

The filter line is the important one:

- `spawnsites - L/2` is each site's displacement from the centre of the box.
- `.T` flips it to shape `(2, k²)` so row 0 holds all the x-displacements and row 1 all the y.
- The `*` unpacks those two rows into `np.hypot(dx, dy)`, which computes `√(dx² + dy²)` — the
  distance from the centre — for every site at once.
- Sites closer than `R_trac + 2*r_bath` are dropped.

The tracer starts at the centre with radius `R_trac`. A bath disc at distance `d` would overlap it
if `d < R_trac + r_bath`. Using `2*r_bath` leaves a full bath radius of clearance instead of exactly
touching. If a disc started inside the tracer, the collision code would fire on the very first step
and fling them apart with an impulse that came from a bad initial condition rather than from physics.

The `while` loop grows the grid if too few sites survived. With the slider limits used on the
website it never runs a second pass — it is a safety net, not part of normal operation.

`rng.permutation(...)[:n_bath]` shuffles the surviving sites and takes the first `n_bath`. **The
shuffle is essential.** The sites are in raster order, so without it you would take the bottom rows
of the grid and every particle would pile into the bottom of the box.

Finally `np.vstack` puts the tracer's position (the box centre) on top as row 0.

### 3.3 Giving them velocities

```python
vel[0]  = rng.normal(0.0, np.sqrt(kB*T/M_trac), 2)
vel[1:] = rng.normal(0.0, np.sqrt(kB*T/m_bath), (n_bath, 2))
```

`rng.normal(mean, standard_deviation, shape)` draws Gaussian random numbers.

**Why Gaussian?** The Boltzmann distribution says the probability of a state falls off as
`exp(−E/kT)`. For a free particle `E = ½m(vₓ² + v_y²)`, and the exponential splits into a product:

```
exp(−E/kT) = exp(−mvₓ²/2kT) × exp(−mv_y²/2kT)
```

Each factor is a Gaussian in one velocity component with variance `kT/m`. The two components are
independent, which is exactly why you can draw them separately.

Check it against equipartition: `⟨½mvₓ²⟩ = ½m × (kT/m) = ½kT` per degree of freedom. Correct.

**A common confusion:** the *components* are Gaussian; the *speed* `√(vₓ² + v_y²)` is not. In 2D the
speed follows a Rayleigh distribution (in 3D it is the familiar Maxwell–Boltzmann speed curve).

Two separate draws because the standard deviation `√(kT/m)` depends on mass. Both species are at the
same `T` — that is what thermal equilibrium means. Same average energy, so the heavier particle is
slower. Measured at 1000 K: bath particles have σ = 545 m/s, the 10× heavier tracer has σ = 172 m/s.

### 3.4 Removing the overall drift

```python
vel -= (mass[:, None] * vel).sum(0) / mass.sum()
```

Reading it in pieces:

| piece | shape | meaning |
|---|---|---|
| `mass[:, None]` | `(n, 1)` | masses as a column, so they broadcast over x and y |
| `mass[:, None] * vel` | `(n, 2)` | each particle's momentum |
| `.sum(0)` | `(2,)` | total momentum **P** |
| `/ mass.sum()` | `(2,)` | **P**/M — the velocity of the centre of mass |
| `vel -= ...` | `(n, 2)` | subtract it from every particle |

Random draws never sum to exactly zero momentum; there is always a leftover fluctuation. Subtracting
the centre-of-mass velocity moves into the frame where total momentum is exactly zero (measured
residual ≈ 1e-37, i.e. floating-point dust).

**Why it matters for this simulation specifically.** With a net drift, the whole gas slides across
the box and the tracer rides along with it. Its displacement would then grow linearly with time on
top of the random wandering, and the mean squared displacement would grow like `t²` instead of `t` —
destroying the diffusive signature the page exists to show.

**A side effect worth knowing.** Subtracting the centre-of-mass velocity also removes the
centre-of-mass kinetic energy, so the gas ends up slightly *colder* than the `T` you asked for. The
energy removed averages exactly `kT`, out of a total `n·kT` — a fractional shortfall of `1/n`.

Measured over 4000 draws, kinetic energy in units of `n·kT`:

| n_bath | before | after | shortfall | 1/n |
|---|---|---|---|---|
| 20 | 1.0043 | 0.9557 | 4.4% | 4.8% |
| 60 | 1.0021 | 0.9856 | 1.4% | 1.6% |
| 180 | 0.9994 | 0.9939 | 0.61% | 0.55% |
| 400 | 0.9995 | 0.9970 | 0.30% | 0.25% |

Independent of the mass ratio (checked at 1×, 10×, 100×). At the default 180 particles this is
0.55% and irrelevant. At the slider's minimum of 20 particles the gas really does run about 5%
cold. This is not a bug — fixing the momentum genuinely removes two degrees of freedom — but if
someone asks why the measured temperature is not exactly 1000 K, that is the reason. A one-line
fix would be to rescale `vel` by `√(T_wanted / T_actual)` afterwards.

---

## 4. One timestep — `step()`

### 4.1 Move everything

```python
global pos
pos += vel * dt
```

`global pos` is needed because `+=` counts as assigning to the name `pos`. `vel`, `mass` and
`radius` do not need it, because those lines only ever modify items *inside* the array.

Every disc moves in a straight line. For hard discs there are no forces between collisions, so this
is **exact**, not an approximation. The only error introduced by the timestep is in *when* a
collision gets noticed — never in the path taken between collisions.

### 4.2 Bounce off the walls

```python
lo = pos - radius[:, None] < 0.0
hi = pos + radius[:, None] > L
vel[lo] = np.abs(vel[lo])
vel[hi] = -np.abs(vel[hi])
np.clip(pos, radius[:, None], L - radius[:, None], out=pos)
```

`lo` and `hi` are true/false arrays the same shape as `pos`, marking which coordinate of which
particle has poked out of the box. Because they are 2D, they select individual *components*: a disc
hitting the left wall has only its `vₓ` corrected, its `v_y` untouched. That is right — a wall only
reverses the component along its normal.

**Why `abs` and not just a minus sign?** If you wrote `vel = -vel`, a disc still overlapping the wall
on the next step would flip again, back into the wall, and get stuck vibrating there. `abs` can be
applied over and over with no further effect: once the velocity points away from the wall, it stays
that way.

`np.clip` pushes any disc that went through back to exactly touching.

These walls are perfectly elastic, so **energy is conserved but momentum is not** — the box absorbs
it. See section 5.

### 4.3 Find every overlapping pair at once

```python
d = pos[:, None, :] - pos[None, :, :]
dist2 = np.einsum('ijk,ijk->ij', d, d)
Rsum = radius[:, None] + radius[None, :]
ia, ib = np.nonzero(np.triu(dist2 < Rsum**2, 1))
```

`pos[:, None, :]` is shape `(n, 1, 2)` and `pos[None, :, :]` is `(1, n, 2)`. Subtracting them
broadcasts to `(n, n, 2)`, where `d[i, j]` is the vector from particle j to particle i — every pair
in one operation with no Python loop.

That array is the main cost of the whole simulation: `n × n × 2` numbers allocated every step, which
is why doubling the particle count roughly quadruples the runtime.

`np.einsum('ijk,ijk->ij', d, d)` multiplies `d` by itself element-wise and sums over the `k` axis
(the x and y components), giving `dist2[i, j] = dx² + dy²`. That is the **squared** distance —
keeping it squared avoids `n²` expensive square roots, and comparisons work just as well on squares.

`Rsum[i, j] = r_i + r_j` is the centre-to-centre distance at which those two discs touch.

The last line does three things: `dist2 < Rsum**2` flags overlapping pairs; `np.triu(..., 1)` keeps
only the strict upper triangle, because the matrix is symmetric (each pair would otherwise appear
twice) and the diagonal is every particle "overlapping itself"; `np.nonzero` returns the indices of
what survived.

### 4.4 Resolve each collision

```python
for a, b in zip(ia, ib):
    dist = np.sqrt(dist2[a, b])
    nhat = d[a, b] / dist
    vn = (vel[a] - vel[b]) @ nhat
    if vn >= 0.0:
        continue
```

`nhat` is the unit vector along the line joining the two centres, pointing from b to a. The square
root is only taken for the few overlapping pairs, not all `n²`.

`vn` is the relative velocity along that line — the approach speed. Since `nhat` points from b to a,
a pair moving *together* gives a **negative** `vn`.

**The `if vn >= 0` guard is load-bearing.** Two discs can still be geometrically overlapping on the
next step even after their collision has been handled. Without this check you would hit them with a
second impulse while they are already separating, creating energy from nothing. This single line is
why energy stays flat to ~1e-16 instead of drifting upward.

```python
    mu = mass[a] * mass[b] / (mass[a] + mass[b])
    J = 2.0 * mu * vn
    vel[a] -= (J / mass[a]) * nhat
    vel[b] += (J / mass[b]) * nhat
```

`mu` is the reduced mass. For a perfectly elastic collision the impulse along the normal is exactly
`2μv_n`; it comes from solving conservation of momentum and conservation of energy together, and the
tidy result is that the relative normal velocity simply reverses.

The signs work out: `vn` is negative for an approaching pair, so `J` is negative, so subtracting it
from `vel[a]` pushes a *away* from b.

Two things fall out. Total momentum is unchanged, because the impulses are equal and opposite. And
only the normal component changes — the sideways component passes straight through, which makes
these frictionless, non-spinning discs.

```python
    overlap = Rsum[a, b] - dist
    fa = mass[b] / (mass[a] + mass[b])
    pos[a] += fa * overlap * nhat
    pos[b] -= (1.0 - fa) * overlap * nhat
```

Because the collision was spotted late, the discs have sunk into each other by `overlap`. This
pushes them apart until they exactly touch, splitting the movement inversely with mass — note it is
the *other* particle's mass on top of `fa`, which is what makes the heavier disc move less.

Two properties: the fractions add to 1, so they separate by exactly `overlap`; and the centre of
mass does not move, since `m_a × fa = m_b × (1 − fa)`.

This step is a geometric fix-up, not dynamics. It corrects a position error, changes no velocities,
and therefore does not touch the energy.

**Shape of the whole function:** drift → bounce off walls → find all overlapping pairs with array
operations → loop over just those few pairs and fix each one. The expensive part is vectorised; the
cheap part is a plain Python loop.

---

## 5. What is conserved, and what is not

Measured from the default setup:

| quantity | result |
|---|---|
| kinetic energy | conserved to ≤ 3e-16 relative over 5000 steps |
| total momentum | **not** conserved — after 500 steps it is ~12× a single bath particle's momentum |

Energy conservation is the real test of the collision code, and it passes at machine precision.

Momentum drifts because the walls are reflecting: every bounce hands momentum to the box. So the
`# zero total MOMENTUM` line in `init()` describes the state at t = 0 only. That is expected and
correct for a gas in a container, but it is worth being able to say so rather than being caught out.

---

## 6. Does it reproduce real gas physics?

### 6.1 Collision rate against kinetic theory

Simple 2D kinetic theory: a disc sweeps out a strip of width `d = 2r` at the mean relative speed, so
the collision rate per particle is `n_A · d · ⟨v_rel⟩`, with `⟨v_rel⟩ = √2 ⟨v⟩` and the 2D mean speed
`⟨v⟩ = √(πkT/2m)`.

At the defaults this predicts 2.50e11 collisions per second. **Measured: 2.67e11** — 6.7% higher.

That gap is not an error. Dilute-gas theory assumes particles are points as far as *finding* each
other is concerned. At finite density, discs are excluded from each other's volume, which crowds
them together and raises the collision rate. The correction is the pair correlation function at
contact, and for 2D hard discs Henderson's expression gives

```
g(σ) = (1 − 7η/16) / (1 − η)²
```

where `η` is the packing fraction. Testing whether the measured enhancement follows it:

| n_bath | r_bath | packing η | measured / dilute | Enskog g(σ) | difference |
|---|---|---|---|---|---|
| 60 | 8 nm | 0.012 | 0.923 | 1.019 | −9.5% |
| 180 | 8 nm | 0.036 | 1.064 | 1.059 | +0.4% |
| 300 | 8 nm | 0.060 | 1.084 | 1.103 | −1.6% |
| 180 | 12 nm | 0.081 | 1.174 | 1.143 | +2.7% |
| 300 | 12 nm | 0.136 | 1.271 | 1.259 | +1.0% |

Across a factor of 11 in density the enhancement tracks the theory to within a few percent. The
60-particle row is the outlier and is also the noisiest — fewest particles, fewest collisions counted.

**This is the strongest result in the whole simulation.** It shows the code reproduces not just the
textbook dilute-gas result but the dense-gas correction on top of it, which is not something you can
get by accident.

Mean free path at the defaults: 246 nm, against a 1000 nm box. So a particle crosses only about a
quarter of the box between collisions — dense enough to behave like a gas rather than a set of
independent projectiles.

### 6.2 Does the tracer actually diffuse?

For true diffusion the mean squared displacement should grow linearly in time, `⟨Δr²⟩ = 4Dt` in 2D.
For pure ballistic (collisionless) motion it grows as `t²`. Fitting the exponent over 6 runs of
15 000 steps:

| time window | fitted exponent |
|---|---|
| early | 1.74 |
| middle | 1.62 |
| late | 1.10 |

So the tracer starts out nearly ballistic and crosses over towards diffusive, reaching 1.10 by the
late window — close to the diffusive value of 1, but not fully converged.

**Be honest about this one.** The run does not cleanly demonstrate long-time diffusion, and there is
a good reason: by the end of these runs the tracer's rms displacement is 339 nm in a 1000 nm box. It
has explored a large fraction of the container, so the walls are confining it and the MSD is starting
to saturate. There is only a narrow window between "not yet enough collisions" and "already hitting
the walls".

The late-time slope gives D ≈ 2.4e-6 m²/s, but treat that as an order-of-magnitude estimate, not a
measurement.

If you wanted to show clean diffusion you would need a bigger box relative to the tracer, or a
heavier tracer so it moves less far. Both cost simulation time.

---

## 7. Numerical limits

### 7.1 The timestep and "tunnelling"

Collisions are only detected at the end of a step. If a pair moves far enough in a single step, they
can pass straight through one another without ever being seen to overlap. Since speeds go as `√T`
and the timestep is fixed, this sets a temperature ceiling.

Test: run at `dt` and at `dt/4` and compare the number of collisions per unit of *physical* time. If
the coarse step were missing collisions, it would count fewer. Run at the harshest settings —
lightest bath particles (8 u) and smallest radius (6 nm), so the fastest particles and thinnest
targets — averaged over 3 seeds:

| T / K | 1000 | 2000 | 3000 | 4000 | 5000 |
|---|---|---|---|---|---|
| missed vs `dt/4` | −2.9% | +3.1% | +4.1% | +3.8% | +2.8% |

There is **no trend** — it sits at 3–4% across the whole range, which is seed-to-seed noise rather
than degradation. So no breakdown could actually be resolved anywhere in 1000–5000 K. The website's
3000 K slider cap is a conservative choice, not a measured cliff.

### 7.2 Starting overlaps

The grid spacing must exceed two bath radii or particles start out already touching. Spacing is
`0.9L/(k−1)`, and `k` grows with `√n_bath`. At the maximum 400 particles the spacing is 36 nm, so
the bath radius slider is capped at 16 nm (2 × 16 = 32 nm, safely under).

Note that a *larger* `1.6` safety factor makes this worse, not better: more sites means a finer grid
means less clearance. The exclusion filter only actually requires a factor of about 1.04 at default
settings and 1.27 at the most extreme tracer size, so 1.6 is generous, and spending it costs radius
headroom.

### 7.3 Cost

Measured on desktop CPython, per animation frame (10 steps):

| n_bath | 20 | 180 | 300 | 400 |
|---|---|---|---|---|
| ms/frame | 0.17 | 3.8 | 11.7 | 17.4 |

Roughly quadratic, as expected from the `n × n` pair array. Interestingly the cost barely depends on
density — at 400 particles it is ~17 ms whether the packing fraction is 10% or 45% — which confirms
the bottleneck is the array allocation in the broad phase, not the Python loop over actual contacts.

In the browser (Pyodide/WebAssembly) everything is several times slower, so expect the frame rate to
sag above roughly 300 particles.

---

## 8. Known imperfections

Things that are defensible but that you should be able to explain if asked:

1. **The comment says "jittered lattice" but there is no jitter.** Particles sit exactly on grid
   points; the only randomness is which sites get used. So the starting configuration is a dilute
   lattice gas, not a properly equilibrated hard-disc configuration. It relaxes within a few hundred
   steps, so it does not matter in practice — but the comment claims something the code does not do.
   Either add real jitter (a random offset up to ±(spacing/2 − r_bath), which keeps the no-overlap
   guarantee) or fix the wording.

2. **The gas runs slightly cold**, by `1/n` — about 5% at the lowest particle count. See §3.4.

3. **Overlaps are resolved one pair at a time, in index order.** If three discs overlap
   simultaneously, fixing pair (a,b) can push a into c. With a dilute gas this is rare, but at high
   packing the order of resolution matters slightly and the result is not perfectly symmetric.

4. **`spf = 10` in the Python file is dead code on the web path** — the JavaScript has its own
   `STEPS_PER_FRAME = 10`. Two constants that have to be kept in step by hand.

5. **The box is small relative to the tracer** (1000 nm vs an 80 nm radius), which is why clean
   long-time diffusion cannot be observed. See §6.2.

6. **The desktop and web copies of the physics are duplicated** and must be edited together.

---

## 9. Quick reference — the numbers at default settings

| quantity | value |
|---|---|
| box | 1 µm square |
| temperature | 1000 K |
| bath particles | 180, mass 4.65e-26 kg, radius 8 nm |
| tracer | mass 10× bath, radius 80 nm |
| bath σ per velocity component | 545 m/s |
| bath mean speed (2D) | 683 m/s |
| tracer σ per component | 172 m/s |
| packing fraction | 5.6% |
| mean free path | 246 nm |
| collision rate (bath–bath) | 2.67e11 s⁻¹ |
| timestep | 1 ps; 10 ps of simulated time per animation frame |
| energy drift | ≤ 3e-16 over 5000 steps |
