# Physics from "Einstein Heat Capacity.py"; plotting is done by the JS layer.

import numpy as np

#Constants
c = 2.998e8
h = 6.626e-34
boltzmann = 1.381e-23
wiens = 2.897771955e-3
gasConstant = 8.31446261815324

elements = {
    "Gold (Au)": 0.2855e13,
    "Copper (Cu)": 0.5769e13,
    "Titanium (Ti)": 0.7054e13,
    "Aluminium (Al)": 0.7188e13,
    "Iron (Fe)": 0.7893e13,
    "Silicon (Si)": 1.0832e13,
    "Carbon (C)": 3.7451e13
}


def heatCapacity(temperature, element):
    global elements
    frequency = elements[element]
    x = (h*frequency)/(boltzmann*temperature)
    return 3*gasConstant*(x**2)*np.exp(x)/((np.exp(x)-1)**2)


temperatures = np.linspace(0,800,500)


# ---- adapter for the web UI ----

def web_curves():
    out = {}
    with np.errstate(invalid='ignore', divide='ignore', over='ignore'):
        for element in elements:
            cv = heatCapacity(temperatures, element)
            # T = 0 (and exp overflow at very low T) give nan/inf -> null gaps
            out[element] = [float(v) if np.isfinite(v) else None for v in cv]
    return {
        "temperatures": temperatures.tolist(),
        "curves": out,
        "dulong_petit": 3 * gasConstant,
    }
