import numpy as np
import math
from scipy import constants as const
from scipy.special import eval_genlaguerre

hbar = const.hbar
h = const.h
pi = const.pi
me = const.m_e
mp = const.m_p
a0  = const.value('Bohr radius')


#asldkjfhalskdnbfalkjdsfhalidfjha

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
    
