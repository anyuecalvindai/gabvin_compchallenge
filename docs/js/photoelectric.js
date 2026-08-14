// Photoelectric effect — UI for py/photoelectric.py.

PROJECTS.push({
  id: 'photoelectric',
  name: '4. Photoelectric Effect',
  blurb: 'The stopping voltage V against light intensity for different metals. The solid line represents the real stopping voltages, whereas the dotted line is its extrapolation below the cutoff frequency. The four coloured lines represent the region of visible light.',

  async render(page) {
    const metals = await pyCall('photoelectric.web_metals');
    const lightFreqs = await pyCall('photoelectric.web_lights');
    // fixed across every metal, so switching material moves the curve, not the frame
    const [yMin, yMax] = await pyCall('photoelectric.web_yrange');
    const lightColours = ['#d62728', '#e6c700', '#2ca02c', '#1f77b4'];   // red yellow green blue

    let metal = metals[0];

    const plotDiv = el('div');
    const group = el('div', { class: 'radio-group' });
    for (const m of metals) {
      const inp = el('input', { type: 'radio', name: 'metal', value: m,
        onchange: () => { metal = m; draw(); } });
      if (m === metal) inp.checked = true;
      group.append(el('label', {}, inp, m));
    }

    page.append(el('div', { class: 'controls' }, group),
                el('div', { class: 'card' }, plotDiv));

    async function draw() {
      const d = await pyCall('photoelectric.web_curve', metal);

      const belowCutoff = d.V.map(v => v <= 0 ? v : null);
      const aboveCutoff = d.V.map(v => v > 0 ? v : null);

      // per-point extras for the hover box; full length so it lines up with the
      // null-masked y arrays
      const extra = d.frequencies.map((_, i) => [d.wavelength_nm[i], d.photon_eV[i]]);

      const common = 'f = %{x:.4~s}Hz<br>λ = %{customdata[0]} nm<br>' +
                     'photon energy = %{customdata[1]} eV<br>';

      Plotly.react(plotDiv, [
        { x: d.frequencies, y: belowCutoff, name: 'Extrapolated stopping voltage',
          mode: 'lines', line: { color: '#1f77b4', dash: 'dot' },
          customdata: extra,
          hovertemplate: common +
            'below cutoff: no emission<br>extrapolated V = %{y:.3f} V<extra></extra>' },
        { x: d.frequencies, y: aboveCutoff, name: 'Stopping voltage',
          mode: 'lines', line: { color: '#1f77b4' },
          customdata: extra,
          hovertemplate: common +
            'stopping voltage = %{y:.3f} V<br>max KE = %{y:.3f} eV<extra></extra>' },
        { x: [d.cutoff, d.cutoff], y: [yMin, yMax], name: `Cutoff frequency ${d.cutoff.toPrecision(3)} Hz`,
          mode: 'lines', line: { color: '#1f77b4', dash: 'dot', width: 1.5 },
          hovertemplate: `cutoff frequency = ${d.cutoff.toPrecision(4)} Hz<br>` +
            `threshold λ = ${d.cutoff_nm.toFixed(1)} nm<br>` +
            `W = ${d.W} eV<extra></extra>` }
      ], baseLayout({
        hovermode: 'closest',
        height: 460,
        title: { text: `Photoelectric effect for ${metal}:  W = ${d.W} eV` },
        xaxis: { title: { text: 'Frequency / Hz' }, range: [0, 2.5e15] },
        yaxis: { title: { text: 'Stopping voltage / V' }, range: [yMin, yMax], zeroline: true },
        shapes: lightFreqs.map((f, i) => ({
          type: 'line', x0: f, x1: f, y0: yMin, y1: yMax,
          line: { color: lightColours[i], width: 1.5 }
        }))
      }), PLOTCFG);
    }

    await draw();
  }
});
