// Brownian motion — UI for py/brownianmotion.py.
// The hard-disc physics runs in Python; this file only animates the results.

PROJECTS.push({
  id: 'brownian',
  name: 'Brownian Motion',
  blurb: '2D hard-disc gas with a tracer particle (red), simulated by the numpy code from ' +
         'the challenge. Bath particles and the tracer collide elastically; momentum ' +
         'transfer from the bath kicks the tracer along a random walk, traced in red.',

  async render(page) {
    const SIZE = 520;
    const STEPS_PER_FRAME = 10;   // matches spf in the python module

    const canvas = el('canvas', { width: SIZE, height: SIZE,
      style: { background: '#fff', border: '1px solid #e4e4e7' } });
    const ctx = canvas.getContext('2d');

    let setup = await pyCall('brownianmotion.web_setup');
    const SCALE = SIZE / setup.L;
    let bath = setup.bath;
    let trail = [setup.tracer];

    function draw() {
      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, SIZE, SIZE);

      // tracer trail
      ctx.strokeStyle = 'rgba(214,39,40,0.6)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(trail[0][0] * SCALE, SIZE - trail[0][1] * SCALE);
      for (let i = 1; i < trail.length; i++) {
        ctx.lineTo(trail[i][0] * SCALE, SIZE - trail[i][1] * SCALE);
      }
      ctx.stroke();

      ctx.fillStyle = 'rgba(31,119,180,0.7)';
      for (const p of bath) {
        ctx.beginPath();
        ctx.arc(p[0] * SCALE, SIZE - p[1] * SCALE, setup.r_bath * SCALE, 0, 2 * Math.PI);
        ctx.fill();
      }

      const t = trail[trail.length - 1];
      ctx.fillStyle = '#d62728';
      ctx.beginPath();
      ctx.arc(t[0] * SCALE, SIZE - t[1] * SCALE, setup.R_trac * SCALE, 0, 2 * Math.PI);
      ctx.fill();
    }

    let running = true;
    let alive = true;

    async function loop() {
      while (alive) {
        if (running) {
          const frame = await pyCall('brownianmotion.web_frame', STEPS_PER_FRAME);
          bath = frame.bath;
          trail.push(frame.tracer);
          if (trail.length > 6000) trail.shift();
          draw();
        }
        await new Promise(r => requestAnimationFrame(r));
      }
    }

    const playBtn = el('button', { class: 'btn', onclick: () => {
      running = !running;
      playBtn.textContent = running ? 'Pause' : 'Play';
    } }, 'Pause');

    const resetBtn = el('button', { class: 'btn', onclick: async () => {
      setup = await pyCall('brownianmotion.web_setup');
      bath = setup.bath;
      trail = [setup.tracer];
      draw();
    } }, 'Reset');

    page.append(el('div', { class: 'controls' }, playBtn, resetBtn,
                  el('span', { class: 'note' },
                    `${setup.n_bath} bath particles (N₂-like, radius inflated), T = ${setup.T} K, ` +
                    `box ${setup.L * 1e6} μm`)),
                el('div', { class: 'card' }, canvas));

    draw();
    loop();

    return () => { alive = false; };   // stop the loop when leaving the page
  }
});
