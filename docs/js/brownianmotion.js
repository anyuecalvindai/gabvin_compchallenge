// Brownian motion — UI for py/brownianmotion.py.
// The hard-disc physics runs in Python; this file only animates the results.

PROJECTS.push({
  id: 'brownian',
  name: '2. Brownian Motion',
  blurb: 'A 2D animation of a large tracer particle, initialised at the centre of the grid, with smaller "bath" particles initialised at randomised positions on a square grid, clear of the tracer. Collisions with walls reverse the component perpendicular to the wall only. Collisions between particles are elastic; energy is conserved to double floating point precision over 5000 steps. Initial bath particle velocity components are sampled from Boltzmann distributions depending on the temperature and particle masses that you can set manually. Time step = 1 picosecond, box width = 1 micrometre. There are 10 timesteps per animation frame. The radii of the particles are inflated compared to actual gas particles in the context of the box size, so that the collisions can actually be seen. You can click save to save the last walk, and automatically start a new one. ',

  async render(page) {
    const SIZE = 520;
    const STEPS_PER_FRAME = 10;   // matches spf in the python module
    const U = 1.66053907e-27;     // atomic mass unit, kg

    // saved walks, drawn under the live one. blue is the bath colour, so it is out
    const SAVED_COLOURS = ['#2ca02c', '#9467bd', '#ff7f0e', '#8c564b', '#e377c2'];

    // slider state, in display units; params() converts to SI for python
    let nBath = 180, mBathU = 28, rBathNm = 8, tracerExp = 1, rTracNm = 80, temp = 1000;
    let seed = 2;

    const params = () => {
      const mBath = mBathU * U;
      return [nBath, mBath, rBathNm * 1e-9, (10 ** tracerExp) * mBath, rTracNm * 1e-9,
              temp, seed];
    };
    const newSeed = () => Math.floor(Math.random() * 1e6);

    const canvas = el('canvas', { width: SIZE, height: SIZE,
      style: { background: '#fff', border: '1px solid #e4e4e7' } });
    const ctx = canvas.getContext('2d');

    // saved walks never change once saved, so they are stroked once into an
    // offscreen canvas and blitted per frame rather than re-stroked every frame
    const savedCanvas = el('canvas', { width: SIZE, height: SIZE });
    const savedCtx = savedCanvas.getContext('2d');
    let savedCount = 0;

    let setup = await pyCall('brownianmotion.web_setup', ...params());
    const SCALE = SIZE / setup.L;
    let bath = setup.bath;
    let trail = [setup.tracer];

    function strokeTrail(c, pts, colour) {
      if (pts.length < 2) return;
      c.strokeStyle = colour;
      c.lineWidth = 1;
      c.beginPath();
      c.moveTo(pts[0][0] * SCALE, SIZE - pts[0][1] * SCALE);
      for (let i = 1; i < pts.length; i++) {
        c.lineTo(pts[i][0] * SCALE, SIZE - pts[i][1] * SCALE);
      }
      c.stroke();
    }

    function draw() {
      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, SIZE, SIZE);

      ctx.drawImage(savedCanvas, 0, 0);
      strokeTrail(ctx, trail, 'rgba(214,39,40,0.6)');

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
    let gen = 0;       // a re-init invalidates any frame still in flight
    let simTime = 0;   // simulated time, seconds — not wall clock

    // tabular-nums keeps the digits from jittering as the clock runs
    const clock = el('span', { class: 'val' });
    const showClock = () => { clock.textContent = 't = ' + (simTime * 1e9).toFixed(2) + ' ns'; };

    async function loop() {
      while (alive) {
        if (running) {
          const my = gen;
          const frame = await pyCall('brownianmotion.web_frame', STEPS_PER_FRAME);
          if (my === gen) {
            bath = frame.bath;
            trail.push(frame.tracer);
            if (trail.length > 6000) trail.shift();
            simTime += STEPS_PER_FRAME * setup.dt;
            showClock();
            draw();
          }
        }
        await new Promise(r => requestAnimationFrame(r));
      }
    }

    const note = el('span', { class: 'note' });

    function noteText() {
      return `${setup.n_bath} bath particles at ${(setup.m_bath / U).toFixed(0)} u, ` +
             `tracer mass ${(setup.M_trac / setup.m_bath).toPrecision(2)}× bath, ` +
             `T = ${setup.T} K, box ${setup.L * 1e6} μm (radii inflated)`;
    }

    async function reinit() {
      const my = ++gen;
      try {
        const s = await pyCall('brownianmotion.web_setup', ...params());
        if (my !== gen) return;
        setup = s;
        bath = s.bath;
        trail = [s.tracer];
        simTime = 0;      // fresh run, fresh clock
        showClock();
        note.textContent = noteText();
        draw();
      } catch (err) {
        // a throw in a control handler would otherwise vanish into the console
        note.textContent = 'setup failed: ' + err.message;
        console.error(err);
      }
    }

    const playBtn = el('button', { class: 'btn', onclick: () => {
      running = !running;
      playBtn.textContent = running ? 'Pause' : 'Play';
    } }, 'Pause');

    // saving without re-rolling the seed would replay the same walk straight on top
    const saveBtn = el('button', { class: 'btn', onclick: () => {
      savedCtx.globalAlpha = 0.45;
      strokeTrail(savedCtx, trail, SAVED_COLOURS[savedCount % SAVED_COLOURS.length]);
      savedCtx.globalAlpha = 1;
      savedCount++;
      seed = newSeed();
      reinit();
    } }, 'Save walk');

    const randBtn = el('button', { class: 'btn', onclick: () => {
      seed = newSeed();
      reinit();
    } }, 'Randomise bath');

    const resetBtn = el('button', { class: 'btn', onclick: () => {
      savedCtx.clearRect(0, 0, SIZE, SIZE);
      savedCount = 0;
      seed = 2;         // back to the reproducible default run
      reinit();
    } }, 'Reset');

    const sliders = [
      slider({ label: 'Bath particles', min: 20, max: 400, step: 10, value: nBath,
        fmt: v => String(v), oninput: v => { nBath = v; } }),
      slider({ label: 'Bath mass', min: 8, max: 120, step: 1, value: mBathU,
        fmt: v => v + ' u', oninput: v => { mBathU = v; } }),
      slider({ label: 'Bath radius', min: 6, max: 16, step: 0.5, value: rBathNm,
        fmt: v => v + ' nm', oninput: v => { rBathNm = v; } }),
      slider({ label: 'Tracer mass', min: -2, max: 2, step: 0.05, value: tracerExp,
        fmt: v => (10 ** v).toPrecision(2) + '× bath', oninput: v => { tracerExp = v; } }),
      slider({ label: 'Tracer radius', min: 20, max: 200, step: 5, value: rTracNm,
        fmt: v => v + ' nm', oninput: v => { rTracNm = v; } }),
      // capped at 3000 K: speeds go as sqrt(T) against a fixed dt, and above that
      // the fixed step starts to miss collisions at the small-radius end
      slider({ label: 'Temperature', min: 100, max: 3000, step: 50, value: temp,
        fmt: v => v + ' K', oninput: v => { temp = v; } })
    ];
    // readouts follow the drag, but rebuilding the whole gas is far too heavy
    // to do per pixel, so the re-init waits for release
    for (const s of sliders) s.inp.addEventListener('change', () => reinit());

    page.append(el('div', { class: 'controls' },
                  playBtn, saveBtn, randBtn, resetBtn,
                  ...sliders.map(s => s.root), note),
                // .canvas-row is the existing flex helper used by diffraction and
                // orbitals; it puts the clock beside the box without new CSS
                el('div', { class: 'card' },
                  el('div', { class: 'canvas-row' }, canvas, clock)));

    note.textContent = noteText();
    showClock();
    draw();
    loop();

    return () => { alive = false; };   // stop the loop when leaving the page
  }
});
