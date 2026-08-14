// Random walk — UI for py/randomwalk.py.

PROJECTS.push({
  id: 'randomwalk',
  name: '1. Random Walk',
  blurb: '2D random walks with fixed step length and uniformly random direction, generated ' +
         'by numpy. Regenerate to draw a new set; the view auto-scales to fit every path.',

  async render(page) {
    const SIZE = 560;
    const canvas = el('canvas', { width: SIZE, height: SIZE, style: { background: '#fff' } });
    const ctx = canvas.getContext('2d');

    let steps = 1e5;
    let walks = 5;

    const stepSelect = el('select', { class: 'btn' });
    for (const [value, label] of [[1e4, '10 000'], [1e5, '100 000'], [1e6, '1 000 000']]) {
      const opt = el('option', { value }, label + ' steps');
      if (value === steps) opt.selected = true;
      stepSelect.append(opt);
    }
    stepSelect.addEventListener('change', () => { steps = +stepSelect.value; draw(); });

    const walkSlider = slider({
      label: 'Number of walks', min: 1, max: 10, step: 1, value: walks,
      fmt: v => String(v),
      oninput: v => { walks = v; draw(); }
    });

    const regen = el('button', { class: 'btn', onclick: () => draw() }, 'Regenerate');

    page.append(el('div', { class: 'controls' }, walkSlider.root, stepSelect, regen),
                el('div', { class: 'card' }, canvas,
                  el('div', { class: 'note' },
                    'Step length L = 1; axes auto-scaled, equal aspect. 10⁶ steps takes a few seconds.')));

    async function draw() {
      const paths = await pyCall('randomwalk.web_walks', walks, steps);

      let xmin = 0, xmax = 0, ymin = 0, ymax = 0;
      for (const p of paths) {
        for (const x of p.x) { if (x < xmin) xmin = x; if (x > xmax) xmax = x; }
        for (const y of p.y) { if (y < ymin) ymin = y; if (y > ymax) ymax = y; }
      }

      // fit everything in view, equal aspect, small margin
      const span = Math.max(xmax - xmin, ymax - ymin, 1e-9);
      const scale = (SIZE - 40) / span;
      const offX = (SIZE - (xmax - xmin) * scale) / 2 - xmin * scale;
      const offY = (SIZE - (ymax - ymin) * scale) / 2 - ymin * scale;

      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, SIZE, SIZE);

      // axes through the origin
      ctx.strokeStyle = 'rgba(0,0,0,0.12)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(offX, 0); ctx.lineTo(offX, SIZE);
      ctx.moveTo(0, SIZE - offY); ctx.lineTo(SIZE, SIZE - offY);
      ctx.stroke();

      for (const p of paths) {
        const r = (Math.random() * 200) | 0;
        const g = (Math.random() * 200) | 0;
        const b = (Math.random() * 200) | 0;
        ctx.strokeStyle = `rgb(${r},${g},${b})`;
        ctx.lineWidth = 0.6;
        ctx.beginPath();
        ctx.moveTo(offX + p.x[0] * scale, SIZE - (offY + p.y[0] * scale));
        for (let i = 1; i < p.x.length; i++) {
          ctx.lineTo(offX + p.x[i] * scale, SIZE - (offY + p.y[i] * scale));
        }
        ctx.stroke();
      }
    }

    await draw();
  }
});
