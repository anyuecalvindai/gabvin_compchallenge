// Einstein heat capacity — UI for py/einstein.py. Static plot, no controls.

PROJECTS.push({
  id: 'einstein',
  name: 'Einstein Heat Capacity',
  blurb: 'Einstein model of the molar heat capacity of solids for seven elements, each with ' +
         'its own Einstein frequency. Every curve approaches the Dulong-Petit limit 3R ' +
         '(dashed line) at high temperature.',

  async render(page) {
    const plotDiv = el('div');
    page.append(el('div', { class: 'card' }, plotDiv));

    const d = await pyCall('einstein.web_curves');

    const traces = Object.entries(d.curves).map(([name, y]) => ({
      x: d.temperatures, y, name, mode: 'lines', line: { width: 1.2 }
    }));

    Plotly.newPlot(plotDiv, traces, baseLayout({
      height: 480,
      title: { text: 'Einstein model of solid molar heat capacity' },
      xaxis: { title: { text: 'Temperature / K' }, range: [0, 800] },
      yaxis: { title: { text: 'Molar heat capacity / J mol⁻¹ K⁻¹' }, range: [0, 26] },
      shapes: [{
        type: 'line', x0: 0, x1: 800, y0: d.dulong_petit, y1: d.dulong_petit,
        line: { color: '#1f77b4', width: 1, dash: 'dash' }
      }]
    }), PLOTCFG);
  }
});
