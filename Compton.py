import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

#Constants
h = 6.626e-34
Me = 9.1093837139e-31
e = 1.6021766e-19
c = 2.998e8
compton = h/(Me*c)

theta = np.linspace(0, 180, 500)

energyKeV = 1000
energyJoule = energyKeV * 1000 * e

wavelength = h*c/energyJoule

def delta_wavelength (theta):
    return compton*(1-np.cos(np.radians(theta)))

def electron_recoil_angle(theta, wavelength):
    theta_radians = np.radians(theta)
    tan_angle = np.sin(theta_radians)/(1+compton/wavelength*(1-np.cos(theta_radians))-np.cos(theta_radians))
    return np.degrees(np.arctan(tan_angle))

def electron_recoil_speed(wavelength,wavelength2):
    Mec2 = Me * (c**2)
    denominator = (h*c/wavelength-h*c/wavelength2+Mec2)
    inside_sqrt = 1 - ((Mec2/denominator)**2)
    sqrt = inside_sqrt**0.5
    return c*sqrt

wavelength_change = delta_wavelength(theta)
wavelength2 = wavelength_change + wavelength
wavelength_shift = wavelength_change/wavelength

fig, ax = plt.subplots()
line, = ax.plot(theta, wavelength_shift)
ax.set_xlabel("Photon scattering angle θ/deg")
ax.set_ylabel("∆λ/λ")
ax.set_title("Compton scattering of X-ray photon off an electron")
ax.set_xlim(0, 180)
ax.set_ylim(0, 4)

electron_angle = electron_recoil_angle(theta,wavelength)
fig2, ax2 = plt.subplots()
line2, = ax2.plot(theta, electron_angle)
ax2.set_xlabel("Photon scattering angle θ/deg")
ax2.set_ylabel("Electron recoil angle phi/deg")
ax2.set_title("Compton scattering of X-ray photon off an electron")
ax2.set_xlim(0, 180)
ax2.set_ylim(0, 90)

electron_speed = electron_recoil_speed(wavelength,wavelength2)/c
fig3, ax3 = plt.subplots()
line3, = ax3.plot(theta, electron_speed)
ax3.set_xlabel("Photon scattering angle θ/deg")
ax3.set_ylabel("Electron recoil speed v/c")
ax3.set_title("Compton scattering of X-ray photon off an electron")
ax3.set_xlim(0, 180)
ax3.set_ylim(0, 1)
plt.subplots_adjust(bottom=0.25)

ax_slider = plt.axes([0.3, 0.1, 0.6, 0.03])
energy_slider = Slider(ax_slider, 'Photon Energy /KeV', 50, 1000, valinit=energyKeV, valstep=10)

def update(val):
    energyKeV = val
    energyJoule = energyKeV * 1000 * e

    wavelength = h*c/energyJoule
    wavelength_change = delta_wavelength(theta)
    wavelength2 = wavelength_change + wavelength
    wavelength_shift = wavelength_change/wavelength

    line.set_data(theta,wavelength_shift)

    electron_angle = electron_recoil_angle(theta,wavelength)
    line2.set_data(theta,electron_angle)

    electron_speed = electron_recoil_speed(wavelength,wavelength2)/c
    line3.set_data(theta,electron_speed)
    
    fig.canvas.draw_idle()
    fig2.canvas.draw_idle()
    

energy_slider.on_changed(update)

plt.show()