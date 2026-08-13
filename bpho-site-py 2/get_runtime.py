#!/usr/bin/env python3
"""Download the Pyodide runtime + numpy wheel into pyodide/ so the site is
fully self-hosted and needs no CDN at runtime.

Run once from this folder, then commit the pyodide/ directory:

    python3 get_runtime.py
"""
import pathlib
import urllib.request

VERSION = "314.0.3"
BASE = f"https://cdn.jsdelivr.net/pyodide/v{VERSION}/full/"
FILES = [
    "pyodide.js",
    "pyodide.mjs",
    "pyodide.asm.mjs",
    "pyodide.asm.wasm",
    "python_stdlib.zip",
    "pyodide-lock.json",
    "numpy-2.4.3-cp314-cp314-pyemscripten_2026_0_wasm32.whl",
]

dest = pathlib.Path(__file__).parent / "pyodide"
dest.mkdir(exist_ok=True)

for name in FILES:
    target = dest / name
    if target.exists() and target.stat().st_size > 0:
        print("already have", name)
        continue
    print("downloading", name, "...")
    urllib.request.urlretrieve(BASE + name, target)

print("done - the site now runs without any CDN")
