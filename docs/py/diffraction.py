# Physics from "Electron DiffractionACCURATE.py"; plotting is done by the JS layer.

import numpy as np

#Constants
h = 6.626e-34
Me = 9.1093837139e-31
e = 1.6021766e-19
c = 2.998e8

r = 65

d1 = 0.123e-9
d2 = 0.213e-9


def Electron_Wavelength(V):
    return h/((2*Me*V*e*(1+(e*V)/(2*Me*(c**2))))**(1/2))


def Bragg(wavelength,d,n):
    num = n*wavelength/(2*d)
    if num <=1:
        angle = 2* np.arcsin(num)
        if angle <= np.pi/4:
            return angle, r * np.sin(2*angle)
    return None, None


def get_radii(wavelength,d1,d2):
    radii = {}
    angles = {}

    for d, label in [(d1, "d1"),(d2, "d2")]:
        counter = 1
        while True:
            angle, radius = Bragg(wavelength,d,counter)
            if radius is None:
                break
            radii[f"{label}, n={counter}"] = radius
            angles[f"{label}, n={counter}"] = angle
            counter += 1

    return radii, angles


def get_intensity(angle,n,intensity):
    return intensity * np.exp(-2.0 * angle**2)/ n**2


def BraggAngle(wavelength,d,n):
    num = n*wavelength/(2*d)

    return 2* np.arcsin(num)


# ---- adapter for the web UI ----

def web_rings(V):
    wavelength = Electron_Wavelength(V)
    radii, angles = get_radii(wavelength, d1, d2)
    intensityMult = 1e-3 * V

    rings = []
    for name, radius in radii.items():
        n = int(name.split("=")[1])
        rings.append({
            "name": name,
            "d": name[0:2],
            "n": n,
            "radius": float(radius),
            "intensity": float(get_intensity(angles[name], n, intensityMult)),
        })
    return rings


def web_linearisation():
    voltages = np.linspace(1000, 5000, 1000)
    wavelengths = Electron_Wavelength(voltages)
    phi = BraggAngle(wavelengths, d2, 1)
    y = np.sin(phi/2)
    return {
        "x": (1/np.sqrt(voltages)).tolist(),
        "y": y.tolist(),
    }
