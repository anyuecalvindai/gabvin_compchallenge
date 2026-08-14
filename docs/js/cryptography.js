// Quantum cryptography — UI for py/cryptography.py.
// The detector sketch is drawing only; both probabilities come from Python.

PROJECTS.push({
  id: 'crypto',
  name: '8. Quantum Cryptography',
  blurb: 'Two polarisation detectors at angles φ and θ measuring an entangled photon pair. ' +
         'Compares the mismatch probability from a classical hidden-variable model with ' +
         'the quantum mechanical prediction sin²(φ−θ).',

  async render(page) {
    let phi = 0;
    let theta = 0;

    const W = 660, H = 330;
    const UNIT = 52;           // px per unit length in the detector sketch
    const canvas = el('canvas', { width: W, height: H, style: { background: '#fff' } });
    const ctx = canvas.getContext('2d');
    const formulas = el('div', { class: 'formulas' });

    // draws a line with an arrowhead, returns where the label should go
    function arrow(ox, oy, dx, dy, len, colour) {
      const x1 = ox + dx * len;
      const y1 = oy + dy * len;
      ctx.strokeStyle = colour;
      ctx.fillStyle = colour;
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(x1, y1); ctx.stroke();

      const a = Math.atan2(y1 - oy, x1 - ox);
      const head = 9;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x1 - head * Math.cos(a - 0.42), y1 - head * Math.sin(a - 0.42));
      ctx.lineTo(x1 - head * Math.cos(a + 0.42), y1 - head * Math.sin(a + 0.42));
      ctx.closePath(); ctx.fill();

      return [x1 + dx * 16, y1 + dy * 16];
    }

    // one detector: X arm at the set angle, Y arm perpendicular,
    // plus a dashed vertical reference line
    function detector(ox, oy, angleDeg, xlabel, ylabel, label, colour) {
      const th = rad(angleDeg);
      const xDir = [Math.sin(th), -Math.cos(th)];    // canvas y points down
      const yDir = [-Math.cos(th), -Math.sin(th)];
      const armLen = 1.5 * UNIT;

      ctx.strokeStyle = '#1f77b4';
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 4]);
      ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(ox, oy - armLen); ctx.stroke();
      ctx.setLineDash([]);

      const [xLx, xLy] = arrow(ox, oy, xDir[0], xDir[1], armLen, colour);
      const [yLx, yLy] = arrow(ox, oy, yDir[0], yDir[1], armLen, colour);

      ctx.fillStyle = '#18181b';
      ctx.font = 'italic 13px serif';
      ctx.fillText(xlabel, xLx - 8, xLy + 4);
      ctx.fillText(ylabel, yLx - 8, yLy + 4);
      ctx.font = 'bold 13px sans-serif';
      ctx.fillText(label, ox - 78, oy + 1.5 * UNIT + 24);
    }

    async function draw() {
      const d = await pyCall('cryptography.web_probs', phi, theta);

      ctx.clearRect(0, 0, W, H);
      detector(180, 145, phi, 'Xᴀ', 'Yᴀ', `Detector A: φ = ${phi}°`, '#2ca02c');
      detector(480, 145, theta, 'Xʙ', 'Yʙ', `Detector B: θ = ${theta}°`, '#1f77b4');

      const diff = phi - theta;
      formulas.innerHTML =
        `<div><b>Classical</b><br>` +
        `P(mismatch) = 1 − cos²θ·cos²φ − sin²θ·sin²φ<br>` +
        `= 1 − (${d.cos_t.toFixed(3)})²(${d.cos_p.toFixed(3)})² − (${d.sin_t.toFixed(3)})²(${d.sin_p.toFixed(3)})²<br>` +
        `= <b>${d.classical.toFixed(3)}</b></div>` +
        `<div><b>Quantum mechanics</b><br>` +
        `P(mismatch) = sin²(φ − θ)<br>` +
        `= sin²(${phi}° − (${theta}°)) = sin²(${diff}°)<br>` +
        `= <b>${d.qm.toFixed(3)}</b></div>`;
    }

    const phiSlider = slider({
      label: 'φ (Detector A)', min: -180, max: 180, step: 1, value: 0,
      fmt: v => v + '°', oninput: v => { phi = v; draw(); }
    });
    const thetaSlider = slider({
      label: 'θ (Detector B)', min: -180, max: 180, step: 1, value: 0,
      fmt: v => v + '°', oninput: v => { theta = v; draw(); }
    });

    page.append(el('div', { class: 'controls' }, phiSlider.root, thetaSlider.root),
                el('div', { class: 'card' }, canvas),
                el('div', { class: 'card' }, formulas));
    await draw();
  }
});
