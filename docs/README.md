# BPhO Computational Challenge — simulations site

Interactive site for the computational challenge projects. The physics runs on
real Python (numpy) in the browser via Pyodide: the `py/` modules are the same
functions as the desktop scripts in the main repo, and the JavaScript in `js/`
only handles controls, canvases and Plotly charts.

## Layout

- `py/` — one Python module per challenge, plus `bridge.py` (the JS↔Python
  interface: every call is `module.function(*args) -> JSON`). `scipy/` is a
  tiny stand-in for `scipy.constants` so the originals import unchanged.
- `js/` — one UI file per challenge; `app.js` boots Pyodide and handles navigation.
- `pyodide/` — the self-hosted Python runtime.
- `lib/` — Plotly, vendored locally.

## Running

Host the folder on any static host (GitHub Pages etc.), or locally:

    python3 -m http.server

then open http://localhost:8000. (Opening index.html straight from the file
manager won't work — WebAssembly has to be served over HTTP.)

## Fully offline / no CDN

The repo ships the Pyodide core; the numpy wheel is fetched from the Pyodide
CDN on first load unless you vendor it too:

    python3 get_runtime.py

Run that once (on any network that can reach cdn.jsdelivr.net) and commit the
`pyodide/` folder — after that the site makes no external requests at all.
