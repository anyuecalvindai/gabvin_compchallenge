import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import numpy as np

#Constants
h = 6.626e-34
e = 1.6021766e-19
c = 2.998e8

red = 4.4e14
yellow = 5.2e14
green = 5.8e14
blue = 6.6e14

metals = {
    "Silver (Ag)" : 4.3,
    "Aluminium (Al)" : 4.3,
    "Gold (Au)" : 5.1,
    "Copper (Cu)" : 4.7,
    "Tin (Sn)" : 4.4,
    "Lead (Pb)" : 4.3,
    "Tungsten (W)" : 4.5,
    "Nickel (Ni)" : 4.6,
    "Sodium (Na)" : 2.4
}


frequencies = np.linspace(0, 2.5e15, 500)


def stoppingVoltage(frequency, metal):
    global metals
    w = metals[metal] * e
    
    return (h*frequency)/e - (w/e)

metal = "Silver (Ag)"

stopVolts = stoppingVoltage(frequencies, metal)
cutoff = metals[metal] * e/h

VNeg = np.where(stopVolts <= 0, stopVolts, np.nan)
VPos = np.where(stopVolts > 0, stopVolts, np.nan)

fig, ax = plt.subplots()

plt.subplots_adjust(left=0.3)

rax = plt.axes([0.02, 0.4, 0.2, 0.2])
select = RadioButtons(rax, list(metals.keys()))

line0, = ax.plot(frequencies, VNeg, ":", color = "C0", label = "Extrapolated Stopping Voltage")
line1, = ax.plot(frequencies, VPos, "-", color = "C0",label = "Stopping Voltage")
freq = ax.axvline(cutoff, color='C0', linestyle=':', label = f"Cutoff frequency {cutoff:.3g}Hz")
ax.axvline(red, color='red')
ax.axvline(yellow, color='yellow')
ax.axvline(green, color='green')
ax.axvline(blue, color='blue')

ax.set_ylim(-5, 6)
ax.set_xlim(0, 2.5e15)
ax.set_xlabel("Frequency / Hz")
ax.set_ylabel("Stopping Voltage / V")
ax.set_title(f"Photoelectric effect for {metal}: W = {metals[metal]}")
ax.legend()
ax.grid(alpha=0.3)

def update(item):
    metal = item
    stopVolts = stoppingVoltage(frequencies, metal)
    cutoff = metals[metal] * e/h

    VNeg = np.where(stopVolts <= 0, stopVolts, np.nan)
    VPos = np.where(stopVolts > 0, stopVolts, np.nan)
    
    line0.set_data(frequencies,VNeg)
    line1.set_data(frequencies,VPos)
    freq.set_xdata([cutoff,cutoff])
    freq.set_label(f"Cutoff frequency {cutoff:.3g}Hz")
    ax.set_title(f"Photoelectric effect for {metal}: W = {metals[metal]}")
    ax.legend()
    
    fig.canvas.draw_idle()

select.on_clicked(update)

plt.show()