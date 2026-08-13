# Physics from "orbitals.py"; plotting is done by the JS layer.

import numpy as np
import math
from scipy import constants as const

hbar = const.hbar
h = const.h
pi = const.pi
me = const.m_e
mp = const.m_p
a0 = const.value('Bohr radius')

Z = 1
mu = (me*mp)/(me+mp)
a = me*a0/(mu*Z)

#scipy.special is not available in  browser, so laguerre and legendre polynomial evaluation is defined here

def eval_genlaguerre(k, alpha, x):
    if k == 0:
        return np.full_like(x,1)
    if k == 1:
        return 1 + alpha - x
    i = 2
    prev = 1
    curr = 1 + alpha - x
    while i <= k:
        j = i-1
        nxt = ((2*j + 1 + alpha -x) * curr - (j+alpha)*prev)/(j+1)
        prev = curr
        curr = nxt
        i = i+1
    return curr

def double_factorial(n):
    return math.prod(range(n, 0, -2))

def lpmv(m, l, x):
    if m < 0:
        mm = -m
        return (-1)**mm * math.factorial(l - mm) / math.factorial(l + mm) * lpmv(mm, l, x)

    pmm =(-1)**m * double_factorial(2*m-1) * (1-x**2)**(m/2)          
    if l == m:
        return pmm

    pm1 = x * (2*m+1) * pmm  
    if l == m + 1:
        return pm1

    prev= pmm
    curr = pm1
    for j in range(m + 2, l + 1):
        nxt = (x*(2*j-1)*curr - (j+m-1)*prev)/(j-m)
        prev=curr
        curr = nxt
    return curr


# ---- wavefunction ---------------------------------------------------------

def zeta(x, l, n):
    k = n - l - 1
    alpha = 2*l + 1
    return eval_genlaguerre(k, alpha, x)


def radial(r, n, l):
    x = 2*r/(a*n)
    return np.sqrt(math.factorial(n-l-1)/(2*n*math.factorial(n+l))) * (2/(a*n))**1.5 * x**l * np.exp(-x/2) * zeta(x, l, n)


def spherharm(theta, phi, l, m):
    return (-1)**m * pow(((2*l+1)*math.factorial(l-m))/(4*pi*(math.factorial(l+m))), 0.5) * lpmv(m, l, np.cos(theta)) * np.exp(1j*m*phi)


def angular(theta, phi, l, m):
    if m == 0:
        return spherharm(theta, phi, l, 0)
    if m > 0:
        return spherharm(theta, phi, l, m) + spherharm(theta, phi, l, -m)
    if m < 0:
        return spherharm(theta, phi, l, -m) - spherharm(theta, phi, l, m)


def psi(r, theta, phi, n, l, m):
    return radial(r, n, l) * angular(theta, phi, l, m)


def density(X, Y, Zc, n, l, m):
    r = np.sqrt(X**2 + Y**2 + Zc**2)
    ratio = np.divide(Zc, r, out=np.zeros_like(r), where=r > 0)
    theta = np.arccos(np.clip(ratio, -1, 1))   # clip: float error can push |Z/r| past 1
    phi = np.arctan2(Y, X)
    return np.abs(radial(r, n, l) * angular(theta, phi, l, m))**2


# ---- adapters for the web UI ----------------------------------------------

def _invalid(n, l, m):
    """Return a message if (n, l, m) is not a valid orbital, else None."""
    if l > n - 1:
        return f"no bound state has n={n} with l={l} — l can be at most n−1"
    if abs(m) > l:
        return f"no orbital has l={l} with m={m} — |m| can be at most l"
    return None

def _extent(n, l, m, frac=0.01, rays=13, samples=400):
    """Largest radius at which the density is still above `frac` of its maximum."""
    r = np.linspace(1e-13, (4 * n**2 + 2) * a, samples)
    fan = []
    for th in np.linspace(0.0, np.pi, rays):
        for ph in (0.0, np.pi / 2):
            fan.append(density(r * np.sin(th) * np.cos(ph),
                               r * np.sin(th) * np.sin(ph),
                               r * np.cos(th), n, l, m))
    fan = np.array(fan)
    peak = fan.max()
    if peak <= 0:
        return n**2 * a
    hits = np.where((fan / peak > frac).any(axis=0))[0]
    return r[hits[-1]] if len(hits) else n**2 * a

def box_limit(n, l=0, m=0, frac=0.01):
    # `frac` should match what the viewer actually displays -- sizing the box at
    # 1% while only drawing above 15% leaves the cloud floating in empty space.
    return 1.15 * _extent(n, l, m, frac) + 0.5 * a


def web_plane(n, l, m, plane, res=200):
    n, l, m = int(n), int(l), int(m)
    err = _invalid(n, l, m)
    if err:
        return {"error": err}
    limit = box_limit(n, l, m)
    s = np.linspace(-limit, limit, int(res))
    A, B = np.meshgrid(s, s)

    if plane == 'yz':
        rho = density(0.0, A, B, n, l, m)
        labels = ('y / Å', 'z / Å')
    elif plane == 'xz':
        rho = density(A, 0.0, B, n, l, m)
        labels = ('x / Å', 'z / Å')
    else:
        rho = density(A, B, 0.0, n, l, m)
        labels = ('x / Å', 'y / Å')

    rho = rho / rho.max()
    return {
        "axis": np.round(s / 1e-10, 4).tolist(),
        "rho": np.round(rho, 4).tolist(),
        "xlabel": labels[0],
        "ylabel": labels[1],
    }


def web_volume(n, l, m, res=48, frac=0.15):
    n, l, m = int(n), int(l), int(m)
    err = _invalid(n, l, m)
    if err:
        return {"error": err}
    limit = box_limit(n, l, m, float(frac))
    s = np.linspace(-limit, limit, int(res))
    X, Y, Zc = np.meshgrid(s, s, s, indexing='ij')
    rho = density(X, Y, Zc, n, l, m)
    rho = rho / rho.max()
    # x/y/z are rebuilt in JS from `axis` (same ij order) to keep the payload small
    return {
        "axis": np.round(s / 1e-10, 4).tolist(),
        "value": np.round(rho.ravel(), 4).tolist(),
    }

def web_volume_signed(n, l, m, res=48, frac=0.15):
    """Signed amplitude psi (not |psi|^2), normalised to [-1, 1]."""
    n, l, m = int(n), int(l), int(m)
    err = _invalid(n, l, m)
    if err:
        return {"error": err}
    limit = box_limit(n, l, m, float(frac))
    s = np.linspace(-limit, limit, int(res))
    X, Y, Zc = np.meshgrid(s, s, s, indexing='ij')
    r = np.sqrt(X**2 + Y**2 + Zc**2)
    ratio = np.divide(Zc, r, out=np.zeros_like(r), where=r > 0)
    theta = np.arccos(np.clip(ratio, -1, 1))
    phi = np.arctan2(Y, X)

    amp = radial(r, n, l) * angular(theta, phi, l, m)
    # the real combinations come out purely real for some (l, m) and purely
    # imaginary for others depending on the parity of m, and never both --
    # so adding the parts picks out whichever one carries the signal
    signed = amp.real + amp.imag
    signed = signed / np.abs(signed).max()

    return {
        "axis": np.round(s / 1e-10, 4).tolist(),
        "value": np.round(signed.ravel(), 4).tolist(),
    }