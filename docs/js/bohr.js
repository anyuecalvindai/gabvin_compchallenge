// Bohr model spectral series — UI for py/bohr.py. Static plot with hover.

PROJECTS.push({
  id: 'bohr',
  name: 'Bohr Model — Spectral Series',
  blurb: 'Photon energies and wavelengths for hydrogen transitions n → n_low (n up to 30), ' +
         'computed with the reduced-mass Rydberg energy. Hover over a point for the ' +
         'transition details.',

  async render(page) {
    // set explicitly rather than left to plotly's colorway: each series now has two
    // traces (markers + verticals) and the automatic colours would fall out of step
    const SERIES_COLOURS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'];

    const plotDiv = el('div');

    const scaleSelect = el('select', { class: 'btn' });
    for (const [value, label] of [['linear', 'Linear λ axis'], ['log', 'Log λ axis']]) {
      scaleSelect.append(el('option', { value }, label));
    }
    scaleSelect.addEventListener('change', () => draw());

    page.append(el('div', { class: 'controls' }, scaleSelect),
                el('div', { class: 'card' }, plotDiv));

    const seriesList = await pyCall('bohr.web_series');

    // a fixed top so "full height" means something the verticals can be built against
    const yTop = 1.04 * Math.max(...seriesList.flatMap(s => s.energy_eV));

    // one trace per series carries all of that series' verticals: x repeats each
    // wavelength twice and null breaks the line between them
    const verticals = seriesList.map((s, i) => ({
      x: s.wavelength_nm.flatMap(w => [w, w, null]),
      y: s.wavelength_nm.flatMap(() => [0, yTop, null]),
      mode: 'lines',
      line: { color: SERIES_COLOURS[i], width: 1, dash: 'dot' },
      opacity: 0.45,
      legendgroup: s.name,
      showlegend: false,
      hoverinfo: 'skip'
    }));

    const markers = seriesList.map((s, i) => ({
      x: s.wavelength_nm,
      y: s.energy_eV,
      customdata: s.n,
      name: s.name,
      legendgroup: s.name,
      mode: 'markers',
      marker: { size: 6, color: SERIES_COLOURS[i] },
      hovertemplate: `${s.name}: n = %{customdata} → ${s.n_low}<br>` +
                     `λ = %{x:.1f} nm<br>E = %{y:.4f} eV<extra></extra>`
    }));

    function draw() {
      // verticals first so the markers sit on top of their own lines
      Plotly.react(plotDiv, [...verticals, ...markers], baseLayout({
        height: 480,
        title: { text: 'Hydrogen emission series (Bohr model, reduced mass)' },
        xaxis: { title: { text: 'Wavelength / nm' }, type: scaleSelect.value },
        yaxis: { title: { text: 'Photon energy / eV' }, range: [0, yTop] }
      }), PLOTCFG);
    }

    draw();
  }
});
