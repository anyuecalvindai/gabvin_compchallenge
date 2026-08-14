// Hydrogen orbitals — UI for py/orbitals.py.
// 2D: heatmap of |psi|^2 in a chosen plane. 3D: isosurfaces of signed psi,
// so the lobes are coloured by the sign of the wavefunction.
// Needs the FULL plotly bundle in lib/ (basic has no heatmap/3D).

PROJECTS.push({
  id: 'orbitals',
  name: '10. Hydrogen Orbitals',
  blurb: 'Hydrogen eigenstates from the analytic wavefunction (reduced mass, real orbital ' +
         'combinations). Pick n, l, m; view a 2D slice of |ψ|² through the nucleus, or the ' +
         '3D lobes coloured by the sign of ψ — red positive, blue negative. The cutoff ' +
         'slider sets the density below which nothing is drawn.',

  async render(page) {
    const RES = 96;               // 3D grid points per axis; cost grows as RES^3
    let n = 3, l = 2, m = 0;
    let plane = 'xz';
    let iso = 15;                 // hide voxels below this % of max density
    let vol = null;               // cached last web_volume result
    let pts = null;               // cached x/y/z arrays rebuilt from vol.axis

    const plot2d = el('div');
    const plot3d = el('div');

    // ---- controls -------------------------------------------------------
    // l and m depend on n and l: when a parent changes, the children are
    // clamped and their sliders updated without triggering extra redraws.
    let syncing = false;

    const nSlider = slider({ label: 'n', min: 1, max: 6, step: 1, value: n,
      fmt: v => 'n = ' + v,
      oninput: v => { n = v; if (!syncing) { sync(); draw2d(); } } });

    const lSlider = slider({ label: 'l', min: 0, max: n - 1, step: 1, value: l,
      fmt: v => 'l = ' + v,
      oninput: v => { l = v; if (!syncing) { sync(); draw2d(); } } });

    const mSlider = slider({ label: 'm', min: -l, max: l, step: 1, value: m,
      fmt: v => 'm = ' + v,
      oninput: v => { m = v; if (!syncing) draw2d(); } });

    function setSlider(s, min, max, value) {
      s.inp.min = String(min);
      s.inp.max = String(max);
      s.inp.value = String(value);
      // Always dispatch, never guard on the DOM value: browsers silently clamp a
      // range input when you lower its max, so the element can already read the
      // new number while our JS variable still holds the old one. Guarding on
      // that comparison skips the update and the two fall out of sync.
      syncing = true;
      s.inp.dispatchEvent(new Event('input'));   // updates the readout + local var
      syncing = false;
    }

    function sync() {
      setSlider(lSlider, 0, n - 1, Math.min(l, n - 1));
      setSlider(mSlider, -l, l, Math.max(-l, Math.min(l, m)));
    }

    // 3D is heavy, so it redraws on release ('change'), not during the drag
    for (const s of [nSlider, lSlider, mSlider]) {
      s.inp.addEventListener('change', () => draw3d());
    }

    const planeSelect = el('select', { class: 'btn' });
    for (const [value, label] of [['yz', 'y–z plane'], ['xz', 'x–z plane'], ['xy', 'x–y plane']]) {
      const opt = el('option', { value }, label);
      if (value === plane) opt.selected = true;
      planeSelect.append(opt);
    }
    planeSelect.addEventListener('change', () => { plane = planeSelect.value; draw2d(); });

    // readout updates live while dragging, but the volume only re-renders on
    // release: a full Plotly volume redraw is far too heavy to run per pixel
    const isoSlider = slider({ label: 'Density cutoff', min: 1, max: 50, step: 1, value: iso,
      fmt: v => v + '% of max',
      oninput: v => { iso = v; } });
    // full recompute, not just a redraw: the cutoff now determines the box size
    isoSlider.inp.addEventListener('change', () => draw3d());

    const col2d = el('div', { style: { flex: '1 1 440px', minWidth: '420px' } },
      el('div', { class: 'controls' }, planeSelect),
      el('div', { class: 'card' }, plot2d));

    // two discrete sign levels, so a key rather than a continuous colour bar
    const swatch = colour => el('span', { style: {
      display: 'inline-block', width: '14px', height: '14px', borderRadius: '3px',
      background: colour, marginRight: '8px', verticalAlign: 'middle' } });

    const key = el('div', { class: 'legend', style: { marginTop: '10px' } },
      el('div', {}, swatch('rgb(178,10,28)'), 'ψ > 0'),
      el('div', {}, swatch('rgb(5,10,172)'), 'ψ < 0'),
      el('div', { class: 'note' }, 'surfaces drawn where |ψ|² reaches the cutoff'));

    const col3d = el('div', { style: { flex: '1 1 440px', minWidth: '420px' } },
      el('div', { class: 'controls' }, isoSlider.root),
      el('div', { class: 'card' }, plot3d, key));

    page.append(
      el('div', { class: 'controls' }, nSlider.root, lSlider.root, mSlider.root),
      el('div', { class: 'canvas-row' }, col2d, col3d));

    // ---- 2D slice -------------------------------------------------------
    async function draw2d() {
      const d = await pyCall('orbitals.web_plane', n, l, m, plane);
      Plotly.react(plot2d, [{
        z: d.rho, x: d.axis, y: d.axis,
        type: 'heatmap', colorscale: 'Viridis', zmin: 0, zmax: 1,
        colorbar: { title: { text: '|ψ|² / max' } }
      }], baseLayout({
        height: 480, showlegend: false,
        title: { text: `|ψ|² slice through the nucleus — n=${n}, l=${l}, m=${m}` },
        xaxis: { title: { text: d.xlabel } },
        yaxis: { title: { text: d.ylabel }, scaleanchor: 'x' }   // equal aspect
      }), PLOTCFG);
    }

    // ---- 3D -------------------------------------------------------------
    // busy/dirty guard: if a slider commit lands while a recompute is running,
    // remember it and run once more at the end instead of piling up requests
    let busy = false, dirty = false;

    async function draw3d() {
      if (busy) { dirty = true; return; }
      busy = true;
      try {
        // signed psi, not |psi|^2, so the two lobes can be coloured by sign.
        // the cutoff also goes over so Python sizes the box to what we draw.
        const d = await pyCall('orbitals.web_volume_signed', n, l, m, RES, iso / 100);
        vol = d;
        // typed arrays: ~10x faster to fill than push() at this size
        const N = RES ** 3;
        pts = { x: new Float64Array(N), y: new Float64Array(N), z: new Float64Array(N) };
        let i = 0;
        for (let ax = 0; ax < RES; ax++)
          for (let by = 0; by < RES; by++)
            for (let cz = 0; cz < RES; cz++) {
              pts.x[i] = d.axis[ax]; pts.y[i] = d.axis[by]; pts.z[i] = d.axis[cz]; i++;
            }
        render3d();
      } finally {
        busy = false;
        if (dirty) { dirty = false; draw3d(); }
      }
    }

    function render3d() {
      if (!vol) return;
      // the slider is a density cutoff but the data is amplitude, and density
      // goes as psi^2 — so a 15% density threshold is a sqrt(0.15) = 39% one
      const t = Math.sqrt(iso / 100);

      Plotly.react(plot3d, [{
        x: pts.x, y: pts.y, z: pts.z, value: vol.value,
        type: 'isosurface',
        isomin: -t, isomax: t,
        surface: { count: 2 },     // one shell per sign of psi
        cmin: -1, cmax: 1,         // keep 0 at the midpoint so the colours stay symmetric
        colorscale: 'RdBu',
        showscale: false,          // only two levels here, so a gradient bar is misleading
        // must stay fully opaque: anything less and WebGL blends surfaces in draw
        // order instead of depth order, so a near lobe can appear behind a far one
        opacity: 1,
        flatshading: false,
        lighting: { ambient: 0.75, diffuse: 0.8, specular: 0.05 },
        caps: { x: { show: false }, y: { show: false }, z: { show: false } }
      }], baseLayout({
        height: 560, showlegend: false,
        title: { text: `ψ — n=${n}, l=${l}, m=${m}` },
        margin: { l: 0, r: 0, t: 42, b: 0 },
        scene: {
          xaxis: { title: { text: 'x / Å' } },
          yaxis: { title: { text: 'y / Å' } },
          zaxis: { title: { text: 'z / Å' } },
          aspectmode: 'cube'
        }
      }), PLOTCFG);
    }

    await draw2d();
    await draw3d();
  }
});