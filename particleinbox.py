from scipy import constants as const
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
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
print(E) #debug

def psi(x,t,n):
    return np.sqrt(2/a_0) * e**(-1j * E[n]*t/h) *np.sin(n*pi*x/a_0)





