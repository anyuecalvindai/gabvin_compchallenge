// Bohr model spectral series — UI for py/bohr.py. Static plot with hover.

PROJECTS.push({
  id: 'bohr',
  name: 'Bohr Model — Spectral Series',
  blurb: 'Photon energies and wavelengths for hydrogen transitions n → n_low (n up to 30), ' +
         'computed with the reduced-mass Rydberg energy. Hover over a point for the ' +
         'transition details.',

  async render(page) {
    const plotDiv = el('div');
    page.append(el('div', { class: 'card' }, plotDiv));

    const seriesList = await pyCall('bohr.web_series');

    const traces = seriesList.map(s => ({
      x: s.wavelength_nm,
      y: s.energy_eV,
      customdata: s.n,
      name: s.name,
      mode: 'markers',
      marker: { size: 6 },
      hovertemplate: `${s.name}: n = %{customdata} → ${s.n_low}<br>` +
                     `λ = %{x:.1f} nm<br>E = %{y:.4f} eV<extra></extra>`
    }));

    Plotly.newPlot(plotDiv, traces, baseLayout({
      height: 480,
      title: { text: 'Hydrogen emission series (Bohr model, reduced mass)' },
      xaxis: { title: { text: 'Wavelength / nm' } },
      yaxis: { title: { text: 'Photon energy / eV' } }
    }), PLOTCFG);
  }
});
