# Physics from "particleinbox.py"; plotting is done by the JS layer.

from scipy import constants as const
import numpy as np
from units import *
import math
assert np.isclose(joule_eV(const.eV), 1.0) #confirm unit conversion function in case other file got cooked


hbar = const.hbar
h = const.h
pi = const.pi
m_e = const.m_e
a_0  = const.value('Bohr radius')
e = math.e

samples = 20 #number of samples


def boxenergy(n,m,L):
    return (hbar**2 * pi**2 * n**2)/(2*m*L**2)


N = np.arange(1, samples+1)
E = joule_eV(boxenergy(N,m_e,a_0))


def psi(x,t,n,L):  #time evolution
    return np.sqrt(2/L) * e**(-1j * E*t/h) *np.sin(n*pi*x/L)


def psi_x(x,n,L):  #spatial eigenstate
    return np.sqrt(2/L)*np.sin(n*pi*x/L)


# ---- adapter for the web UI ----

def web_state(n, L):
    x = np.linspace(0, L, num=1000)
    y = psi_x(x, n, L)
    return {
        "x": x.tolist(),
        "psi": y.tolist(),
        "psi2": (y**2).tolist(),
        "energy_eV": float(joule_eV(boxenergy(n, m_e, L * a_0))),
    }
