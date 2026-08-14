# Physics from "Photoelectric Effect.py"; plotting is done by the JS layer.

import numpy as np

#Constants
h = 6.626e-34
e = 1.6021766e-19
c = 2.998e8

red = 4.4e14
yellow = 5.2e14
green = 5.8e14
blue = 6.6e14

metals = {
    "Silver (Ag)" : 4.3,
    "Aluminium (Al)" : 4.3,
    "Gold (Au)" : 5.1,
    "Copper (Cu)" : 4.7,
    "Tin (Sn)" : 4.4,
    "Lead (Pb)" : 4.3,
    "Tungsten (W)" : 4.5,
    "Nickel (Ni)" : 4.6,
    "Sodium (Na)" : 2.4
}


frequencies = np.linspace(0, 2.5e15, 500)


def stoppingVoltage(frequency, metal):
    global metals
    w = metals[metal] * e

    return (h*frequency)/e - (w/e)


# ---- adapter for the web UI ----

def web_metals():
    return list(metals.keys())


def web_lights():
    return [red, yellow, green, blue]


def web_yrange():
    # one fixed frame for every metal: only the curve should move, not the axes
    lo = min(stoppingVoltage(frequencies[0], m) for m in metals)
    hi = max(stoppingVoltage(frequencies[-1], m) for m in metals)
    return [lo - 0.5, hi + 0.5]


def web_curve(metal):
    stopVolts = stoppingVoltage(frequencies, metal)
    cutoff = metals[metal] * e/h
    return {
        "frequencies": frequencies.tolist(),
        "V": stopVolts.tolist(),
        "cutoff": cutoff,
        "W": metals[metal],
    }
