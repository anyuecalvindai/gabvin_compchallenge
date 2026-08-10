import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

#Constants
c = 2.998e8
h = 6.626e-34
boltzmann = 1.381e-23
wiens = 2.897771955e-3

wavelengths_nm = np.linspace(100, 3000, 500)
wavelengths_m = wavelengths_nm * 1e-9

sunTemp = 5778
temperature = 1000

def wavelength_to_rgb(wavelength, gamma=0.8):

    wavelength = float(wavelength)

    if wavelength < 380:
        r = 1
        g = 0
        b = 1
    elif 380 <= wavelength < 440:
        r = -(wavelength - 440) / (440 - 380)
        g = 0.0
        b = 1.0
    elif 440 <= wavelength < 490:
        r = 0.0
        g = (wavelength - 440) / (490 - 440)
        b = 1.0
    elif 490 <= wavelength < 510:
        r = 0.0
        g = 1.0
        b = -(wavelength - 510) / (510 - 490)
    elif 510 <= wavelength < 580:
        r = (wavelength - 510) / (580 - 510)
        g = 1.0
        b = 0.0
    elif 580 <= wavelength < 645:
        r = 1.0
        g = -(wavelength - 645) / (645 - 580)
        b = 0.0
    else:
        r = 1.0
        g = 0.0
        b = 0.0

    r = r ** gamma if r > 0 else 0.0
    g = g ** gamma if g > 0 else 0.0
    b = b ** gamma if b > 0 else 0.0

    return (r, g, b)

def Peak(temperature):
    return wiens/temperature

def Radiance(temp,wavelength):
    value = ((2*h*(c**2))/((wavelength)**5))/(np.exp((h*c)/(wavelength * boltzmann * temp))-1)
    return value

radiance = Radiance(temperature,wavelengths_m) * 1e-9
sunRadiance = Radiance(sunTemp,wavelengths_m) * 1e-9

peakLambda = Peak(temperature)

peakRadiance = Radiance(temperature, peakLambda) * 1e-9

fig,ax = plt.subplots()

line0, = ax.plot(wavelengths_nm, radiance, label = f"{temperature}K", color = wavelength_to_rgb(peakLambda*(10**9)))
ax.plot(wavelengths_nm,sunRadiance, label = "5778K", color = wavelength_to_rgb(Peak(sunTemp)*10**9))
ax.set_xlim(0, 3000)
ax.set_ylim(0, peakRadiance *1.2)
ax.set_xlabel("Wavelength /nm")
ax.set_ylabel("Spectral Radiance/ W/m²/nm")
ax.set_title("Spectral Radiance vs Wavelength")
ax.legend()

plt.subplots_adjust(bottom=0.25)

ax_slider = plt.axes([0.3, 0.1, 0.6, 0.03])
temp_slider= Slider(ax_slider, 'Temperature /K', 1000, 10000, valinit=1000, valstep=10)

def update(value):
    temperature = value
    radiance = Radiance(temperature,wavelengths_m) * 1e-9
    
    peakLambda = Peak(temperature)
    peakRadiance = Radiance(temperature, peakLambda) * 1e-9
    
    line0.set_data(wavelengths_nm,radiance)
    line0.set_label(f"{temperature}K")
    line0.set_color(wavelength_to_rgb(peakLambda*(10**9)))
    
    ax.set_ylim(0, peakRadiance *1.2)
    ax.legend()
    
    fig.canvas.draw_idle

temp_slider.on_changed(update)
ax.grid(alpha=0.3)

plt.show()
