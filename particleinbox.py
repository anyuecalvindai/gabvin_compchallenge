from scipy import constants as const
import numpy as np
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.widgets import Slider, TextBox
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

def psi(x,t,n,L):  #time evolution
    return np.sqrt(2/L) * e**(-1j * E*t/h) *np.sin(n*pi*x/L)

def psi_x(x,n,L):  #spatial eigenstate
    return np.sqrt(2/L)*np.sin(n*pi*x/L)

fig, (psiy, psi2y) = plt.subplots(2, sharex=True, figsize=(8, 7))
plt.subplots_adjust(hspace=0, bottom=0.25)  # leave room at bottom for widgets

n_0 = 1
L_0 = 1.0 

def draw(n, L):
    psiy.cla()
    psi2y.cla()  # clear both subplots
 
    x = np.linspace(0, L, num=1000)
 
    #psi#######
    psiy.plot(x, psi_x(x, n, L))
    psiy.set_title('Particle in a 1D box\n' + r'$L$=' + f'{L:.3g}' + r' $a_0$, $n$=' + str(n))
    psiy.set_ylabel(r'$\psi$')
 
    ymax = np.sqrt(2 / L)     #max value of psix is sqrt2/l -- sin max value = 1
    margin = 0.1  # 10% margin, also used to widen walls
    yupb = ymax * (1 + margin) #top of wall 10% higher than ymax
    ylowb = -yupb

    #walls 
    psiy.plot([0, 0], [ylowb, yupb], 'black', linewidth=4)   #left
    psiy.plot([L, L], [ylowb, yupb], 'black', linewidth=4)   #right
    psiy.set_ylim(ylowb, yupb)
    psiy.grid(True)
 
    #psi^2 ###########
    psi2 = psi_x(x, n, L) ** 2
    psi2y.plot(x, psi2, c='r')
    psi2y.fill_between(x, psi2, color='b', alpha=0.5) #alpha = transparency
    psi2y.set_xlabel(r'$x$ (bohr, $a_0$)')
    psi2y.set_ylabel(r'$|\psi|^2$')
    
    ymax2 = 2 / L #same argument, squared
    yupb2 = ymax2 * (1 + margin)
    ylowb2 = -yupb2 
    #walls
    psi2y.plot([0, 0], [ylowb2, yupb2], 'black', linewidth=4)  # left wall
    psi2y.plot([L, L], [ylowb2, yupb2], 'black', linewidth=4)  # right wall
    psi2y.set_ylim(0, yupb2)
    psi2y.set_xlim(-L * margin, L*(1+margin))
    psi2y.grid(True)
 
    fig.canvas.draw_idle()
 

ax_n = fig.add_axes([0.15, 0.10, 0.7, 0.03]) #n slider object
n_slider = Slider(ax_n, r'$n$', 1, 20, valinit=n_0, valstep=1)
 
ax_L = fig.add_axes([0.35, 0.03, 0.15, 0.05]) #L input textbox
L_box = TextBox(ax_L, r'$L$ (bohr):', initial=str(L_0))
 
current_L = [L_0]
def on_n_change(val):
    n = int(n_slider.val)
    L = current_L[0]
    draw(n, L)


def on_L_submit(text):
    try:
        L = float(text)
        if L <= 0:
            raise ValueError
    except ValueError:
        L_box.set_val(str(current_L[0]))  # revert to last good value
        return
    current_L[0] = L
    n = int(n_slider.val)
    draw(n, L)


n_slider.on_changed(on_n_change)
L_box.on_submit(on_L_submit)
 
# initial render
draw(n_0, L_0)
 
plt.show()