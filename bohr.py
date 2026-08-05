import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from scipy import constants as const

Z = 1 #hydrogen


me = const.m_e
mp = const.m_p

mu = (me*mp)/(me+mp)

"""
reduced mass improves accuracy, bc Bohr assumed the electron orbited a fixed proton. 
actually orbit CoM, so we use reduced mass.
"""

elevels = []


E_rydberg = (mu * (const.e ** 4))/(8*(const.epsilon_0**2)* (const.h**2)) #ionisation energy of hydrogen

print(E_rydberg)#debug

def e_levels(n):   #calculate energy associated with this energy level
    return -(Z**2 * E_rydberg)/n**2

def transition_wl(n_low, n_high):   #returns photon wavelength given two energy level indices
    E_diff = abs(e_levels(n_high) - e_levels(n_low))
    return (const.h * const.c)/E_diff

def compute_elevels(J):  #calculate J energy levels
    for i in range (1,J):
        elevels.append(e_levels(i))
    print(elevels) #debug

















