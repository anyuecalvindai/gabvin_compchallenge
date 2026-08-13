// Shared helpers, the Pyodide boot, and page navigation.
// All physics lives in the py/ modules; each page asks Python for its data
// through pyCall() and only does controls + plotting here.

'use strict';

const PYODIDE_CDN = 'https://cdn.jsdelivr.net/pyodide/v314.0.3/full/';
const NUMPY_WHEEL = 'numpy-2.4.3-cp314-cp314-pyemscripten_2026_0_wasm32.whl';

// every python file the site needs, copied into the in-browser filesystem
const PY_MODULES = [
  'bridge.py',
  'scipy/__init__.py', 'scipy/constants.py', 'units.py',
  'blackbody.py', 'photoelectric.py', 'compton.py', 'einstein.py',
  'diffraction.py', 'cryptography.py', 'particleinbox.py', 'bohr.py',
  'randomwalk.py', 'brownianmotion.py'
];

async function bootPython() {
  const status = document.getElementById('boot-status');
  const say = t => { if (status) status.textContent = t; };

  let py;
  try {
    say('Starting Python runtime…');
    py = await loadPyodide({ indexURL: 'pyodide/' });
  } catch (err) {
    say('Local runtime failed, retrying from CDN…');
    py = await loadPyodide({ indexURL: PYODIDE_CDN });
  }

  say('Loading numpy…');
  try {
    await py.loadPackage('numpy');           // resolves locally once get_runtime.py has run
  } catch (err) {
    await py.loadPackage(PYODIDE_CDN + NUMPY_WHEEL);
  }

  say('Loading the physics modules…');
  py.FS.mkdirTree('/home/pyodide/scipy');
  for (const path of PY_MODULES) {
    const resp = await fetch('py/' + path);
    if (!resp.ok) throw new Error('could not fetch py/' + path);
    py.FS.writeFile('/home/pyodide/' + path, await resp.text());
  }
  py.runPython('import bridge');
  return py;
}

const pythonReady = bootPython();

pythonReady.then(() => {
  const splash = document.getElementById('splash');
  if (splash) splash.remove();
}).catch(err => {
  const status = document.getElementById('boot-status');
  if (status) status.textContent = 'Python failed to start: ' + err.message;
  console.error(err);
});

// call a python function by dotted name; arguments and result travel as JSON
async function pyCall(path, ...args) {
  const py = await pythonReady;
  py.globals.set('_bridge_args', JSON.stringify(args));
  return JSON.parse(py.runPython(`bridge.call(${JSON.stringify(path)}, _bridge_args)`));
}

// ---- generic DOM/plot helpers ----

const rad = d => d * Math.PI / 180;

function el(tag, attrs = {}, ...kids) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'style') Object.assign(node.style, v);
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), v);
    else if (k === 'html') node.innerHTML = v;
    else node.setAttribute(k, v);
  }
  for (const kid of kids) node.append(kid);
  return node;
}

// labelled range slider with a live value readout
function slider({ label, min, max, step, value, fmt = v => v, oninput }) {
  const val = el('span', { class: 'val' }, fmt(value));
  const inp = el('input', { type: 'range', min, max, step, value });

  inp.addEventListener('input', () => {
    const v = +inp.value;
    val.textContent = fmt(v);
    oninput(v);
  });

  const root = el('div', { class: 'ctl' },
    el('div', { class: 'ctl-top' }, el('span', {}, label), val),
    inp);
  return { root, inp };
}

const PLOTCFG = { displayModeBar: false, responsive: true };

function baseLayout(overrides) {
  return Object.assign({
    margin: { l: 65, r: 20, t: 42, b: 50 },
    font: { size: 12 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: '#ffffff',
    showlegend: true
  }, overrides);
}

// ---- navigation ----

const PROJECTS = [];
let cleanup = null;    // set by pages that run animations
let epoch = 0;         // guards against a slow page landing after a newer click

async function show(id) {
  const myEpoch = ++epoch;
  if (cleanup) {
    cleanup();
    cleanup = null;
  }

  const p = PROJECTS.find(q => q.id === id);
  document.querySelectorAll('.navbtn').forEach(b =>
    b.classList.toggle('active', b.dataset.id === id));

  const main = document.getElementById('main');
  main.innerHTML = '';

  // pages render into their own container: if the user switches away mid-load,
  // the stale container is already detached and nothing leaks onto the new page
  const page = el('div');
  main.append(el('h2', {}, p.name), el('p', { class: 'blurb' }, p.blurb), page);
  main.scrollTop = 0;

  let ret = null;
  try {
    ret = await p.render(page);
  } catch (err) {
    page.append(el('div', { class: 'card', style: { borderColor: '#d62728', color: '#d62728' } },
      'This page failed to render: ' + err.message));
    console.error(err);
  }
  if (typeof ret === 'function') {
    if (myEpoch === epoch) cleanup = ret;
    else ret();   // superseded while loading: stop its animation immediately
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const nav = document.getElementById('nav');
  for (const p of PROJECTS) {
    nav.append(el('button', { class: 'navbtn', 'data-id': p.id, onclick: () => show(p.id) }, p.name));
  }
  show(PROJECTS[0].id);
});
