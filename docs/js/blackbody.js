// Black body radiation — UI for py/blackbody.py.

PROJECTS.push({
  id: 'blackbody',
  name: 'Black Body Radiation',
  blurb: 'Planck curve for a black body. Slide the temperature to watch the peak shift ' +
         '(Wien\'s law) and the curve change colour to match. The 5778 K solar spectrum ' +
         'is plotted for reference, and the y-axis rescales to the adjustable curve.',

  async render(page) {
    let T = 1000;

    const plotDiv = el('div');
    const tempSlider = slider({
      label: 'Temperature', min: 1000, max: 10000, step: 10, value: T,
      fmt: v => v + ' K',
      oninput: v => { T = v; draw(); }
    });

    page.append(el('div', { class: 'controls' }, tempSlider.root),
                el('div', { class: 'card' }, plotDiv));

    // python returns (r, g, b) in 0..1
    const css = c => `rgb(${Math.round(c[0] * 255)},${Math.round(c[1] * 255)},${Math.round(c[2] * 255)})`;

    async function draw() {
      const d = await pyCall('blackbody.web_curves', T);
      Plotly.react(plotDiv, [
        { x: d.wavelengths_nm, y: d.radiance, name: T + ' K', mode: 'lines',
          line: { color: css(d.colour), width: 2.5 } },
        { x: d.wavelengths_nm, y: d.sun, name: '5778 K (Sun)', mode: 'lines',
          line: { color: css(d.sun_colour), width: 2 } }
      ], baseLayout({
        height: 440,
        title: { text: 'Spectral Radiance vs Wavelength' },
        xaxis: { title: { text: 'Wavelength / nm' }, range: [0, 3000] },
        yaxis: { title: { text: 'Spectral radiance / W m⁻² nm⁻¹' }, range: [0, d.peak_radiance * 1.2] }
      }), PLOTCFG);
    }

    await draw();
  }
});
