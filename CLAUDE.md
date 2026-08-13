# CLAUDE.md — BPhO Computational Challenge

Context for Claude Code. Save at the **repo root** of `gabvin_compchallenge`; Claude Code loads it automatically.

---

## How to work with me (read this first)

I'm a student doing the British Physics Olympiad computational challenge. **The physics and the maths are mine to write.** I want to learn the tools, not be handed finished code.

- **Don't implement physics or derivations for me.** Explain the method, give me the recurrence/formula, let me write it, then check my attempt. If I paste broken code, point at the bug and make me fix it — don't paste a corrected version unless I explicitly ask twice.
- **Web/UI plumbing is fair game to write for me** — that's not what's being assessed. I'm learning it, but I don't need to derive it.
- **Push back on me.** If my code is wrong, say so plainly. If I'm about to do something dumb, say so.
- I've read a beginner web course grounded in this repo (HTML/CSS/JS/DOM/events/async/canvas/Plotly). Assume I know the basics but not the idioms. I'm fluent in Python + numpy.
- Concise, direct answers. No cheerleading.
- **Give me edits, not whole files.** I once pasted a reference copy of `orbitals.py` over my working one and destroyed my own implementations of `eval_genlaguerre` and `lpmv`. If a whole file is genuinely needed, say explicitly what of mine it would overwrite.
- **Measure before prescribing.** Several fixes in this project came from timing or probing the actual numbers rather than reasoning about them (where the density really falls off; what was actually slow). Prefer that.

**AI-use disclosure:** the site scaffolding was AI-assisted; the challenge physics is mine. Keep it that way — I need to be able to explain every line to a judge.

---

## What this is

Ten (soon eleven) quantum physics simulations from the BPhO computational challenge, originally written as standalone matplotlib scripts, now also published as an interactive website.

**Live:** https://anyuecalvindai.github.io/gabvin_compchallenge/
**Repo:** https://github.com/anyuecalvindai/gabvin_compchallenge

The key architectural decision: **the physics stays in Python.** The site runs real CPython + numpy in the browser via Pyodide (WebAssembly). JavaScript does only UI and drawing. This keeps my challenge code as the single source of truth rather than maintaining a parallel JS port.

---

## Repo layout

```
/                          repo root — original matplotlib scripts live here
├── *.py                   the original standalone challenge scripts (unchanged, still run on desktop)
├── CLAUDE.md              this file
└── docs/                  the website (GitHub Pages serves from main /docs)
    ├── index.html         page skeleton; loads libs then js/ files in order
    ├── styles.css         all styling (CSS custom properties at :root)
    ├── README.md
    ├── .nojekyll          stops Jekyll eating files starting with underscores
    ├── get_runtime.py     run once on desktop: downloads Pyodide + numpy wheel into pyodide/
    ├── check_orbitals.py  run on desktop: verifies my hand-written special functions vs scipy
    ├── lib/               plotly (FULL bundle — basic has no heatmap/3D)
    ├── pyodide/           self-hosted Python runtime (~13 MB + numpy wheel ~8 MB)
    ├── py/                physics modules — THE SOURCE OF TRUTH
    │   ├── bridge.py      the entire JS↔Python interface (~12 lines)
    │   ├── scipy/         SHIM — hand-typed scipy.constants only (see gotchas)
    │   ├── units.py
    │   └── <sim>.py       one per simulation
    └── js/                UI only
        ├── app.js         helpers, Pyodide boot, navigation
        └── <sim>.js       one per simulation: controls + plotting
```

**Note the duplication:** `/(root)/*.py` are the original desktop scripts; `docs/py/*.py` are the web versions (same physics functions, matplotlib stripped, plus `web_*` adapter functions). If I change physics, it should change in both — or we consolidate, which we haven't done.

---

## Architecture

### The bridge (how JS calls Python)

`docs/py/bridge.py` is the whole interface:

```python
def call(path, args_json):
    module_name, func_name = path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    result = getattr(module, func_name)(*json.loads(args_json))
    return json.dumps(result)
```

From JS: `await pyCall('blackbody.web_curves', 5500)` → runs `blackbody.web_curves(5500)` → returns the dict as a JS object. Everything crosses as JSON, so Python must return only JSON-safe types (`.tolist()` on numpy arrays, `float()` on numpy scalars, `None` not `NaN`).

**Adapter convention:** each physics module keeps its original functions untouched and adds `web_*` functions at the bottom under a `# ---- adapter for the web UI ----` comment. Adapters do array→list conversion and rounding to keep payloads small.

### Page registration

`app.js` defines a global `PROJECTS` array. Each `js/<sim>.js` does:

```js
PROJECTS.push({ id, name, blurb, async render(page) { ... } });
```

`show(id)` clears `#main`, builds the heading, and calls `render`. Nav buttons, routing, and error handling are automatic — **adding a simulation needs no changes to `app.js` except adding the .py filename to `PY_MODULES`.**

`render` may return a cleanup function (used by animated pages) which `show` calls before the next page loads.

### No modules

Plain `<script src>` tags, one shared global namespace, no `import`/`export`. Load order in `index.html` matters: `app.js` must come first (it creates `PROJECTS`). Keep per-page state inside `render` to avoid collisions.

### Boot sequence

1. `plotly` and `pyodide.js` load
2. `app.js` runs, calls `bootPython()` → returns a promise (`pythonReady`)
3. sim files register themselves in `PROJECTS`
4. `DOMContentLoaded` → build nav → `show(PROJECTS[0].id)`
5. `bootPython` loads numpy, copies `py/` files into Pyodide's virtual FS via `FS.writeFile`, imports `bridge`
6. splash removed; awaiting `pyCall`s proceed

---

## Gotchas (each of these cost real debugging time)

**CDN blocking.** The user's network blocks cdnjs and possibly jsdelivr. Everything must be self-hosted. If something "doesn't render", check the Network tab for a blocked request before anything else. First failure in this project was exactly this: charts silently dead because Plotly never loaded.

**`loadPackage` doesn't throw on failure** — it logs and continues, so Python boots without numpy and every page dies with `ModuleNotFoundError`. Always verify by *running* `import numpy` in a try/catch, not by trusting the call. This is handled in `app.js`; don't regress it.

**The scipy shim shadows real scipy.** `docs/py/scipy/` contains hand-typed constants only. Python finds it before any installed scipy, so `scipy.special` is unavailable in the browser. That's why the orbitals module implements `eval_genlaguerre` and `lpmv` by hand. If real scipy is ever needed, the shim must be deleted first — and that means re-verifying `bohr.py` and `particleinbox.py`, which currently depend on the shim's values.

**Browsers clamp range inputs; jsdom doesn't.** Setting `input.max` below the current value silently clamps `input.value` in a real browser. Code that guards on `if (+inp.value !== newValue)` before dispatching will skip the update, leaving the JS variable out of sync with the visible slider. This caused a real bug in the orbitals n/l/m clamping and **was not caught by the jsdom test harness**. Never guard slider syncing on the DOM value; always set the variable explicitly.

**Caching, twice over.** GitHub Pages' edge cache holds files ~10 min; the browser's holds longer. After pushing, check Actions for a green build, then hard-refresh. Several "your fix didn't work" reports were stale caches.

Worse, the `py/` modules are fetched over HTTP at boot, so **the browser can serve Pyodide a stale copy of a Python file** — the symptom is a traceback that contradicts the source in front of you (`module 'orbitals' has no attribute 'web_volume_signed'` when the function is plainly there). `app.js` appends `?v=' + Date.now()` to those fetches to defeat it. Don't remove that; the files are a few KB.

General rule worth keeping: **when the error contradicts the code you're reading, the thing running isn't the thing you're reading.** Stale cache, wrong directory, or an old deployment.

**WebGL transparency breaks occlusion.** Any Plotly 3D trace with `opacity < 1` stops writing to the depth buffer, so surfaces are blended in draw order rather than depth order — a far lobe can paint over a near one. This produced an orbital that looked inside-out. `opacity: 1` restores correct occlusion. Transparency and correct sorting are fundamentally in tension in real-time 3D; if a 3D plot looks wrong, suspect opacity first.

**3D rendering budget.** Cost ≈ `RES³ × surface.count`, and both levers trade against each other at fixed cost. Smoothness needs voxels-per-shell-radius ≳ 30 (RES 96 gives that); colour gradients need many shells. You cannot have both — which is why the 3D view switched to two sign-coloured isosurfaces rather than ten density shells. Measured: 96³ × 2 ≈ 56³ × 10 in cost, but far smoother.

**`file://` doesn't work.** WebAssembly needs HTTP. Local preview is `cd docs && python3 -m http.server` → http://localhost:8000.

**Errors in event handlers aren't caught.** `show()`'s try/catch only wraps the *initial* render. A throw inside a slider callback vanishes into the console. Prefer returning `{error: msg}` from Python for expected conditions (like invalid quantum numbers) and rendering it as content.

---

## Verification approach

There is a habit here worth keeping: **every physics change is checked numerically against a reference, not eyeballed.**

- The original ten sims were verified by running the site in jsdom with real Plotly, capturing the actual plotted arrays, and comparing against CPython references computed from the original scripts — 30/30 checks passing at ~1e-13 relative error, plus conservation laws (energy drift ~1e-15 over 2000 Brownian steps), equipartition, and known physical limits (Wien's law, Dulong–Petit 3R, Compton backscatter, H-alpha 656.47 nm, normalisation ∫|ψ|²dx = 1).
- `docs/check_orbitals.py` compares my hand-written `eval_genlaguerre` and `lpmv` against scipy across many (k, α) and (l, m) — run on desktop, where scipy exists.
- **Sweep parameters, don't spot-check.** A single test point passed by luck during the Laguerre debugging (α=1, x=2 makes two independent errors cancel). Test ranges.

Before shipping any JS edit: `node --check docs/js/<file>.js`. This catches whole-file paste accidents (duplicated function bodies, orphaned lines) instantly.

**Test-harness blind spot:** the jsdom harness does *not* implement HTML value sanitisation, so it cannot reproduce the range-input clamping bug described above, and it has no WebGL so it cannot see 3D rendering problems at all. A green harness run is not proof; visual/interaction changes need a real browser.

---

## Current state

**Working and verified (10 sims):** black body, photoelectric, Compton, Einstein heat capacity, electron diffraction, quantum cryptography, particle in a box, Bohr model, random walk, Brownian motion. All 11 pages are live.

**Orbitals (11th) — working.** Layout is two columns: 2D on the left (plane dropdown yz/xz/xy), 3D on the right (density-cutoff slider), with shared n/l/m sliders above. The n/l/m sliders clamp each other (l ≤ n−1, |m| ≤ l).

- **2D**: `web_plane` → Viridis heatmap of |ψ|²/max, box sized at the 1% contour (it shows the whole gradient).
- **3D**: `web_volume_signed` → two `isosurface` shells of *signed* ψ, RdBu, red ψ>0 / blue ψ<0, fully opaque, `RES = 96`, with an HTML key instead of a colour bar. Box sized at the *display cutoff*, passed in from JS.

Design history worth not re-litigating: a `volume` cloud with a full-spectrum colourscale was tried and abandoned — nested translucent shells looked like a jumble of triangles, and the low-density (blue) end was invisible under `opacityscale`. A plain isosurface of |ψ|² is smooth but necessarily single-coloured. Colouring by the sign of ψ is what gives both smoothness and meaningful colour.

**The parity subtlety (load-bearing).** `angular()` returns a complex array that is purely **real** for some (l, m) and purely **imaginary** for others, flipping with the parity of m — never both. So `web_volume_signed` extracts the signed amplitude as `amp.real + amp.imag` (one term is always zero). Taking `.real` alone would silently produce an empty plot for half the states.

Other recent changes:
- `eval_genlaguerre` / `lpmv` implemented by hand from recurrences (student's own work), verified against scipy by `check_orbitals.py`
- `box_limit(n, l, m, frac)` sized from the orbital itself via `_extent()` — a ray-fan probe finding where density drops below `frac` of max — rather than an n-only formula. Visible extent varies hugely with l (n=6: ~2 Å for l=0, ~36 Å for l=5), and `frac` must match what's displayed or the cloud floats in an oversized box wasting grid resolution.
- `setSlider` no longer guards on the DOM value (the range-clamping bug above)
- axis rounding 2 dp → 4 dp; at small box sizes 2 dp produced duplicate coordinates, which breaks a heatmap
- `_check` (raises) replaced by `_invalid` (returns a message) so bad quantum numbers render as text, not a traceback — expected conditions are data, not exceptions

### Known issues / next steps

1. **s-orbitals look like a dot in 2D.** For l=0, |ψ|² is dominated by the nuclear cusp, so normalising to max hides all outer shell structure (at n=6 the 1% contour is only ~2 Å). Options: plot the radial probability r²|ψ|² instead, or apply a gamma/log transform to the colour mapping. Physics decision, not yet made. Less of an issue in 3D now that the box tracks the display cutoff.
2. **2D and 3D plot different quantities.** The heatmap shows |ψ|², the 3D shows signed ψ. Titles say so, but a signed 2D heatmap (same RdBu treatment) would be more coherent. Not done.
3. **`web_volume` is now unused** — superseded by `web_volume_signed`. Kept because it's harmless and useful for testing; delete if tidying.
4. **Real spherical-harmonic convention.** The real combinations `Y_m ± Y_{−m}` lack the 1/√2 normalisation, and for odd m the sin/cos assignment is swapped versus the usual convention (so m=+1 is the sine-type orbital, meaning e.g. the m=+1 p-orbital points along y rather than x). Harmless for shapes since everything is normalised, but the labels are technically off. Worth fixing or explicitly documenting before judging.
5. **`RES = 96` is untuned for slow machines.** Cost is RES³; if the 3D view is sluggish on a weaker laptop, drop to 72. It's a single named constant at the top of `render`.
6. **numpy wheel may still come from the CDN.** If `docs/pyodide/` has no `.whl` file, `get_runtime.py` hasn't been run — the site then depends on jsdelivr on first visit. Run it on an unfiltered network and commit.
7. **Mobile layout.** Fixed 250px sidebar; no media queries. The orbitals two-column layout does wrap correctly on narrow screens.
8. **Root vs docs duplication** of the physics modules (see layout note).

---

## Conventions

- Python: keep original challenge code verbatim where possible; additions go under a clearly marked adapter section. Comments explain *why*, not *what*.
- JS: `const` by default, `el()` helper for DOM building (in `app.js`), page state as closure variables inside `render`, `Plotly.react` for updates and `newPlot` only for first draw.
- Sliders fire `'input'` (live) for cheap redraws; use `'change'` (on release) for expensive ones.
- Style: 2-space JS indent, comments lowercase and sparse, no emoji.
