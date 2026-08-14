# BPhO Computational Challenge — simulations site

Interactive site for the computational challenge projects. The physics runs on Python (numpy) in the browser via Pyodide: the `py/` modules are the same
functions as the desktop scripts in the main repo, and the JavaScript in `js/`
only handles controls, canvases and Plotly charts.

## Layout

- `py/` — one Python module per challenge, plus `bridge.py` (the JS↔Python
  interface: every call is `module.function(*args) -> JSON`). `scipy/` is a
  tiny stand-in for `scipy.constants` so the originals import unchanged. Would have been a 40MB download on opening the website
- `js/` — one UI file per challenge; `app.js` boots Pyodide and handles navigation.
- `pyodide/` — the self-hosted Python runtime.
- `lib/` — Plotly, vendored locally.
