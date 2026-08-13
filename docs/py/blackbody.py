# Physics from "Black Body Radiation.py"; plotting is done by the JS layer.

import numpy as np

#Constants
c = 2.998e8
h = 6.626e-34
boltzmann = 1.381e-23
wiens = 2.897771955e-3

wavelengths_nm = np.linspace(100, 3000, 500)
wavelengths_m = wavelengths_nm * 1e-9

sunTemp = 5778


def wavelength_to_rgb(wavelength, gamma=0.8):

    wavelength = float(wavelength)

    if wavelength < 380:
        r = 1
        g = 0
        b = 1
    elif 380 <= wavelength < 440:
        r = -(wavelength - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= wavelength < 490:
        r = 0.0
        g = (wavelength - 440) / (490 - 440)
        b = 1.0
    elif 490 <= wavelength < 510:
        r = 0.0
        g = 1.0
        b = -(wavelength - 510) / (510 - 490)
    elif 510 <= wavelength < 580:
        r = (wavelength - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= wavelength < 645:
        r = 1.0
        g = -(wavelength - 645) / (645 - 580)
        b = 0.0
    else:
        r = 1.0
        g = 0.0
        b = 0.0

    r = r ** gamma if r > 0 else 0.0
    g = g ** gamma if g > 0 else 0.0
    b = b ** gamma if b > 0 else 0.0

    return (r, g, b)


def Peak(temperature):
    return wiens/temperature


def Radiance(temp, wavelength):
    value = ((2*h*(c**2))/((wavelength)**5))/(np.exp((h*c)/(wavelength * boltzmann * temp))-1)
    return value


# ---- adapter for the web UI ----

def web_curves(temperature):
    radiance = Radiance(temperature, wavelengths_m) * 1e-9
    sunRadiance = Radiance(sunTemp, wavelengths_m) * 1e-9

    peakLambda = Peak(temperature)
    peakRadiance = Radiance(temperature, peakLambda) * 1e-9

    return {
        "wavelengths_nm": wavelengths_nm.tolist(),
        "radiance": radiance.tolist(),
        "sun": sunRadiance.tolist(),
        "peak_radiance": peakRadiance,
        "colour": wavelength_to_rgb(peakLambda * 1e9),
        "sun_colour": wavelength_to_rgb(Peak(sunTemp) * 1e9),
    }
