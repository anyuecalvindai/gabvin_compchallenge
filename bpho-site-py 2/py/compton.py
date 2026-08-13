# Physics from "Compton.py"; plotting is done by the JS layer.

import numpy as np

#Constants
h = 6.626e-34
Me = 9.1093837139e-31
e = 1.6021766e-19
c = 2.998e8
compton = h/(Me*c)

theta = np.linspace(0, 180, 500)


def delta_wavelength (theta):
    return compton*(1-np.cos(np.radians(theta)))


def electron_recoil_angle(theta, wavelength):
    theta_radians = np.radians(theta)
    tan_angle = np.sin(theta_radians)/(1+compton/wavelength*(1-np.cos(theta_radians))-np.cos(theta_radians))
    return np.degrees(np.arctan(tan_angle))


def electron_recoil_speed(wavelength,wavelength2):
    Mec2 = Me * (c**2)
    denominator = (h*c/wavelength-h*c/wavelength2+Mec2)
    inside_sqrt = 1 - ((Mec2/denominator)**2)
    sqrt = inside_sqrt**0.5
    return c*sqrt


# ---- adapter for the web UI ----

def _clean(a):
    # JSON has no NaN, so undefined points (e.g. 0/0 at theta = 0) become null
    return [float(x) if np.isfinite(x) else None for x in a]


def web_curves(energyKeV):
    energyJoule = energyKeV * 1000 * e
    wavelength = h*c/energyJoule

    wavelength_change = delta_wavelength(theta)
    wavelength2 = wavelength_change + wavelength
    wavelength_shift = wavelength_change/wavelength

    with np.errstate(invalid='ignore', divide='ignore'):
        electron_angle = electron_recoil_angle(theta, wavelength)
        electron_speed = electron_recoil_speed(wavelength, wavelength2)/c

    return {
        "theta": theta.tolist(),
        "shift": _clean(wavelength_shift),
        "phi": _clean(electron_angle),
        "speed": _clean(electron_speed),
    }
