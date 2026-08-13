# Physics from "bohr.py"; plotting is done by the JS layer.

from scipy import constants as const

Z = 1 #hydrogen
N_max = 30
names = {1: "Lyman", 2: "Balmer", 3: "Paschen", 4: "Brackett", 5: "Pfund"}

me = const.m_e
mp = const.m_p
h = const.h
c= const.c
q_e=const.e
e_0 = const.epsilon_0

mu = (me*mp)/(me+mp)

"""
reduced mass improves accuracy, bc Bohr assumed the electron orbited a fixed proton.
actually orbit CoM, so we use reduced mass.
"""

E_rydberg = (mu * (q_e** 4))/(8*(e_0**2)* (h**2)) #ionisation energy of hydrogen


def e_levels(n):   #calculate energy associated with this energy level
    return -(Z**2 * E_rydberg)/n**2


def photon_energy(n_low, n_high):
    return abs(e_levels(n_high) - e_levels(n_low))


def transition_wl(n_low, n_high):   #returns photon wavelength given two energy level indices
    return (h* c)/photon_energy(n_low, n_high)


def compute_elevels(J):  #calculate J energy levels
    return [e_levels(i) for i in range (1, J+1)]


def series(n_low, n_max=N_max):
    n_values = list(range(n_low + 1, n_max + 1))
    energies = [photon_energy(n_low, n) for n in n_values]
    wavelength = [transition_wl(n_low, n) for n in n_values]
    return {
        "name": names.get(n_low, f"n={n_low}"),
        "n_low": n_low,
        "n": n_values,
        "energy": energies,
        "energy_eV": [E/q_e for E in energies],
        "wavelengths": wavelength,
        "wavelength_nm": [L *1e9 for L in wavelength]
    }


# ---- adapter for the web UI ----

def web_series():
    return [series(k) for k in range(1, 6)]
