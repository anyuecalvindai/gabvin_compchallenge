// Particle in a 1D box — UI for py/particleinbox.py.

PROJECTS.push({
  id: 'box',
  name: '7. Particle in a 1D Box',
  blurb: 'Time independent wavefunction of an electron confined to a 1-D infinite square potential well, plotted above its probability density. You set the quantum number n and the box length L, measured in Bohr radii; the energy is shown for the current state. ',

  async render(page) {
    let n = 1;
    let L = 1.0;   // box length in units of a0

    const plotDiv = el('div');
    const energyReadout = el('span', { class: 'val' });

    const nSlider = slider({
      label: 'Quantum number n', min: 1, max: 20, step: 1, value: 1,
      fmt: v => 'n = ' + v,
      oninput: v => { n = v; draw(); }
    });

    const LInput = el('input', { type: 'number', value: '1.0', min: '0.1', step: '0.1' });
    LInput.addEventListener('change', () => {
      const v = parseFloat(LInput.value);
      if (!Number.isFinite(v) || v <= 0) {
        LInput.value = L;   // revert to last good value
        return;
      }
      L = v;
      draw();
    });

    page.append(el('div', { class: 'controls' },
                  nSlider.root,
                  el('div', { class: 'ctl' }, el('span', {}, 'Box length L (bohr)'), LInput),
                  el('div', { class: 'ctl' }, el('span', {}, 'Energy Eₙ'), energyReadout)),
                el('div', { class: 'card' }, plotDiv));

    async function draw() {
      const d = await pyCall('particleinbox.web_state', n, L);
      energyReadout.textContent = d.energy_eV.toPrecision(4) + ' eV';

      const margin = 0.1;   // 10% headroom above the walls
      const psiMax = Math.sqrt(2 / L) * (1 + margin);
      const psi2Max = (2 / L) * (1 + margin);

      const wall = (xPos, yref, y0, y1) => ({
        type: 'line', x0: xPos, x1: xPos, y0, y1,
        xref: 'x', yref, line: { color: '#000', width: 4 }
      });

      Plotly.react(plotDiv, [
        { x: d.x, y: d.psi, mode: 'lines', name: 'ψ',
          line: { color: '#1f77b4' }, xaxis: 'x', yaxis: 'y' },
        { x: d.x, y: d.psi2, mode: 'lines', name: '|ψ|²',
          line: { color: '#d62728' }, fill: 'tozeroy',
          fillcolor: 'rgba(31,119,180,0.45)', xaxis: 'x', yaxis: 'y2' }
      ], baseLayout({
        height: 560, showlegend: false,
        title: { text: `Particle in a 1D box — L = ${L} a₀,  n = ${n}` },
        xaxis: { title: { text: 'x  (bohr, a₀)' }, range: [-L * margin, L * (1 + margin)] },
        yaxis: { title: { text: 'ψ' }, range: [-psiMax, psiMax], domain: [0.56, 1] },
        yaxis2: { title: { text: '|ψ|²' }, range: [0, psi2Max], domain: [0, 0.44] },
        shapes: [
          wall(0, 'y', -psiMax, psiMax), wall(L, 'y', -psiMax, psiMax),
          wall(0, 'y2', 0, psi2Max), wall(L, 'y2', 0, psi2Max)
        ]
      }), PLOTCFG);
    }

    await draw();
  }
});
