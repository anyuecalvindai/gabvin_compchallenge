// Photoelectric effect — UI for py/photoelectric.py.

PROJECTS.push({
  id: 'photoelectric',
  name: 'Photoelectric Effect',
  blurb: 'Stopping voltage against photon frequency for a chosen metal. The solid line is ' +
         'the physical stopping voltage and the dotted part its extrapolation below the ' +
         'cutoff frequency. The coloured verticals mark four visible-light frequencies.',

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

      Plotly.react(plotDiv, [
        { x: d.frequencies, y: belowCutoff, name: 'Extrapolated stopping voltage',
          mode: 'lines', line: { color: '#1f77b4', dash: 'dot' } },
        { x: d.frequencies, y: aboveCutoff, name: 'Stopping voltage',
          mode: 'lines', line: { color: '#1f77b4' } },
        { x: [d.cutoff, d.cutoff], y: [yMin, yMax], name: `Cutoff frequency ${d.cutoff.toPrecision(3)} Hz`,
          mode: 'lines', line: { color: '#1f77b4', dash: 'dot', width: 1.5 } }
      ], baseLayout({
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
