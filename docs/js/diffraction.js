// Electron diffraction — UI for py/diffraction.py.

PROJECTS.push({
  id: 'diffraction',
  name: '6. Electron Diffraction',
  blurb: 'Bragg diffraction rings from a polycrystalline graphite target (plane spacings ' +
         'd1 = 0.123 nm, d2 = 0.213 nm) on a screen 65 mm away. Toggle between the ' +
         'phosphor-screen simulation and an annotated graph view. Below: the linearisation ' +
         'sin(½ϕ) ∝ 1/√V for the innermost ring.',

  async render(page) {
    const SIZE = 520;
    const SCALE = (SIZE / 2 - 10) / 70;   // px per mm, +-70 mm view
    // matplotlib's default colour cycle, so the graph view matches the Python plots
    const CYCLE = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];

    let V = 5000;
    let theme = 'simulation';

    // brightness ramp for the phosphor screen look
    function ringColour(intensity) {
      const t = Math.max(0, Math.min(1, intensity));
      return `rgb(${Math.round(50 * t)},${Math.round(205 * t)},${Math.round(50 * t)})`;
    }

    const canvas = el('canvas', { width: SIZE, height: SIZE });
    const ctx = canvas.getContext('2d');
    const legend = el('div', { class: 'legend' });
    const title = el('div', { class: 'val', style: { marginBottom: '8px', fontSize: '14px' } });

    const voltSlider = slider({
      label: 'Accelerating voltage', min: 1000, max: 5000, step: 10, value: V,
      fmt: v => v + ' V',
      oninput: v => { V = v; draw(); }
    });

    const themeBtn = el('button', { class: 'btn', onclick: () => {
      theme = (theme === 'simulation') ? 'graph' : 'simulation';
      themeBtn.textContent = (theme === 'simulation') ? 'Switch to graph view' : 'Switch to simulation view';
      draw();
    } }, 'Switch to graph view');

    const linPlot = el('div');

    page.append(
      el('div', { class: 'controls' }, voltSlider.root, themeBtn),
      el('div', { class: 'card' }, title,
        el('div', { class: 'canvas-row' }, canvas,
          el('div', {}, legend,
            el('div', { class: 'note' }, 'd1 = 0.123 nm', el('br'), 'd2 = 0.213 nm')))),
      el('div', { class: 'card' }, linPlot));

    async function draw() {
      const rings = await pyCall('diffraction.web_rings', V);
      const sim = (theme === 'simulation');
      const cx = SIZE / 2, cy = SIZE / 2;

      ctx.fillStyle = sim ? '#000000' : '#ffffff';
      ctx.fillRect(0, 0, SIZE, SIZE);

      // faint grid every 20 mm with labels
      ctx.strokeStyle = sim ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.10)';
      ctx.fillStyle = sim ? 'rgba(255,255,255,0.45)' : 'rgba(0,0,0,0.45)';
      ctx.lineWidth = 1;
      ctx.font = '10px sans-serif';
      for (let mm = -60; mm <= 60; mm += 20) {
        const x = cx + mm * SCALE;
        const y = cy - mm * SCALE;
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, SIZE); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(SIZE, y); ctx.stroke();
        ctx.fillText(String(mm), x + 2, SIZE - 4);
        if (mm !== -60) ctx.fillText(String(mm), 3, y - 3);
      }
      ctx.fillText('mm', SIZE - 22, SIZE - 16);

      legend.innerHTML = '';
      for (const ring of rings) {
        ctx.beginPath();
        ctx.setLineDash(!sim && ring.d === 'd2' ? [4, 4] : []);
        ctx.lineWidth = 2;
        ctx.strokeStyle = sim ? ringColour(ring.intensity) : CYCLE[ring.n % 10];
        ctx.arc(cx, cy, ring.radius * SCALE, 0, 2 * Math.PI);
        ctx.stroke();

        if (!sim) {
          legend.append(el('div', {},
            el('span', { class: 'swatch', style: {
              borderTopColor: CYCLE[ring.n % 10],
              borderTopStyle: ring.d === 'd2' ? 'dotted' : 'solid'
            } }),
            ring.name));
        }
      }
      ctx.setLineDash([]);

      title.textContent = `Diffraction Rings (V = ${V} V) — ${sim ? 'simulation' : 'graph'} view`;
    }

    await draw();

    // linearisation for the innermost ring (d2, n=1)
    const lin = await pyCall('diffraction.web_linearisation');
    Plotly.newPlot(linPlot, [{
      x: lin.x, y: lin.y, mode: 'lines', line: { color: '#1f77b4' }
    }], baseLayout({
      height: 340, showlegend: false,
      title: { text: 'Innermost Ring: sin(½ϕ) vs 1/√V' },
      xaxis: { title: { text: '1/√V  /  V^(−½)' } },
      yaxis: { title: { text: 'sin(½ϕ)' } }
    }), PLOTCFG);
  }
});
