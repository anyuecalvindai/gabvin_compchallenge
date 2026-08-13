import numpy as np
import math
from scipy import constants as const
from scipy.special import eval_genlaguerre
from scipy.special import lpmv
from matplotlib.widgets import Slider
from matplotlib import cm, colors
import matplotlib.pyplot as plt

hbar = const.hbar
h = const.h
pi = const.pi
me = const.m_e
mp = const.m_p
a0  = const.value('Bohr radius')

Z = 1
mu = (me*mp)/(me+mp)
a = me *a0/(mu*Z)

def zeta(x,l,n):
    k = n - l - 1
    alpha = 2*l+1
    return eval_genlaguerre(k, alpha, x)

def radial(r,n,l):
    x = 2*r/(a*n)
    return np.sqrt(math.factorial(n-l-1)/(2*n*math.factorial(n+l))) * (2/(a*n))**1.5  * x**l * np.exp(-x/2) * zeta(x,l,n)

def spherharm(theta,phi,l,m):  
    return (-1)**m * pow(((2*l+1)*math.factorial(l-m))/(4*pi*(math.factorial(l+m))), 0.5) * lpmv(m, l, np.cos(theta))* np.exp(1j*m*phi) #must use np as math.exp only takes real inputs

def angular(theta,phi,l,m):
    if m == 0:
        return spherharm(theta,phi,l,0)
    if m > 0:
        return spherharm(theta,phi,l,m) + spherharm(theta,phi,l,-m)
    if m < 0: 
        return spherharm(theta,phi,l,-m) - spherharm(theta,phi,l,m)


def psi(r,theta,phi,n,l,m):
    return radial(r,n,l) * angular(theta,phi,l,m)


def planeplot(p):
    limit = 10e-10
    spaces = 500
    x = np.linspace(-limit, limit, spaces)
    y = np.linspace(-limit, limit, spaces)
    z = np.linspace(-limit, limit, spaces)

    """
    define p = 1 to be yz plane, p=2 xz, p=3 xy
    """
    if p == 1:
        Y,Z = np.meshgrid(y,z)
        X = 0.0 #since 2D
        h,v = Y, Z #horizontal and vertical axes
    elif p == 2:
        X,Z = np.meshgrid(x,z)
        Y = 0.0
        h,v = X,Z
    elif p == 3:
        X,Y = np.meshgrid(x,y)
        Z = 0.0
        h,v = X,Y
    return X,Y,Z, h, v

def exampleplaneplot():
    n,l,m = 3,2,-2
    X, Y, Z, h, v = planeplot(3)
    r = np.sqrt(X**2 + Y**2 + Z**2)
    theta = np.arccos(Z/r)
    phi = np.arctan2(Y, X)    


    rho = np.abs(psi(r, theta, phi, n, l, m))**2
    rho = rho / rho.max()

    fig, ax = plt.subplots()
    mesh = ax.pcolormesh(X, Y, rho, shading='auto', vmin=0, vmax=1)
    ax.set_aspect('equal') 
    fig.colorbar(mesh, ax=ax)
    plt.show()

exampleplaneplot()

def density(X, Y, Zc, n, l, m):
    r = np.sqrt(X**2 + Y**2 + Zc**2)
    theta = np.arccos(np.divide(Zc, r, out=np.zeros_like(r), where=r>0))
    phi = np.arctan2(Y, X)
    return np.abs(radial(r, n, l) * angular(theta, phi, l, m))**2


def glass(n, l, m, limit=14e-10, res=100, nslice=19,
          alpha_max=0.55, gamma=1.4, cmap=cm.plasma):
    if l > n-1:      raise ValueError(f"l must be <= n-1 (got n={n}, l={l})")
    if abs(m) > l:   raise ValueError(f"|m| must be <= l (got l={l}, m={m})")

    s = np.linspace(-limit, limit, res)
    X, Y = np.meshgrid(s, s)
    zs = np.linspace(-limit, limit, nslice)

    # pass 1: every slice, then ONE global maximum
    rhos = [density(X, Y, z, n, l, m) for z in zs]
    gmax = max(rr.max() for rr in rhos)

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(projection='3d')

    # pass 2: draw back to front
    for k in np.argsort(zs):
        d = rhos[k] / gmax
        rgba = cmap(d)
        rgba[..., 3] = alpha_max * d**gamma
        ax.plot_surface(X/1e-10, Y/1e-10, np.full_like(X, zs[k]/1e-10),
                        facecolors=rgba, shade=False,
                        rcount=res, ccount=res,
                        linewidth=0, antialiased=False)

    L = limit/1e-10
    ax.set_xlim(-L, L); ax.set_ylim(-L, L); ax.set_zlim(-L, L)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel('x /Å'); ax.set_ylabel('y /Å'); ax.set_zlabel('z /Å')
    ax.set_title(f"n={n}, l={l}, m={m}")
    plt.show()


glass(5,4,-4)