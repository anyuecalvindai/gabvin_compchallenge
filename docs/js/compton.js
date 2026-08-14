// Compton scattering — UI for py/compton.py.

PROJECTS.push({
  id: 'compton',
  name: '9. Compton Scattering',
  blurb: 'A series of graphs showing how photons and stationary electrons interact when they collide, showing the wavelength shift, electron velocity and the direction of the electron’s motion depending on which angle θ the photon is scattered by.',

  async render(page) {
    let energyKeV = 1000;

    const shiftDiv = el('div');
    const angleDiv = el('div');
    const speedDiv = el('div');

    const energySlider = slider({
      label: 'Photon energy', min: 50, max: 1000, step: 10, value: energyKeV,
      fmt: v => v + ' keV',
      oninput: v => { energyKeV = v; draw(); }
    });

    page.append(el('div', { class: 'controls' }, energySlider.root),
                el('div', { class: 'card' }, shiftDiv),
                el('div', { class: 'card' }, angleDiv),
                el('div', { class: 'card' }, speedDiv));

    async function draw() {
      const d = await pyCall('compton.web_curves', energyKeV);

      const plot = (div, y, yTitle, yRange, name) => Plotly.react(div,
        [{ x: d.theta, y, mode: 'lines', name, line: { color: '#1f77b4' } }],
        baseLayout({
          height: 330, showlegend: false, title: { text: name },
          xaxis: { title: { text: 'Photon scattering angle θ / deg' }, range: [0, 180] },
          yaxis: { title: { text: yTitle }, range: yRange }
        }), PLOTCFG);

      plot(shiftDiv, d.shift, 'Δλ/λ', [0, 4], 'Fractional wavelength shift');
      plot(angleDiv, d.phi, 'Electron recoil angle φ / deg', [0, 90], 'Electron recoil angle');
      plot(speedDiv, d.speed, 'Electron recoil speed  v/c', [0, 1], 'Electron recoil speed');
    }

    await draw();
  }
});
