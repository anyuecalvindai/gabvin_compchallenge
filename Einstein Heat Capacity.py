import matplotlib.pyplot as plt
import numpy as np

#Constants
c = 2.998e8
h = 6.626e-34
boltzmann = 1.381e-23
wiens = 2.897771955e-3
gasConstant = 8.31446261815324

elements = {
    "Gold (Au)": 0.2855e13,
    "Copper (Cu)": 0.5769e13,
    "Titanium (Ti)": 0.7054e13,
    "Aluminium (Al)": 0.7188e13,
    "Iron (Fe)": 0.7893e13,
    "Silicon (Si)": 1.0832e13,
    "Carbon (C)": 3.7451e13
}


def heatCapacity(temperature, element):
    global elements
    frequency = elements[element]
    x = (h*frequency)/(boltzmann*temperature)
    return 3*gasConstant*(x**2)*np.exp(x)/((np.exp(x)-1)**2)

temperatures = np.linspace(0,800,500)

fig,ax = plt.subplots()

for element in elements:
    ax.plot(temperatures, heatCapacity(temperatures, element), label = element, linewidth = 0.5)
ax.axhline(3*gasConstant, linewidth = 0.5,linestyle = "--")

ax.set_xlim(0,800)
ax.set_ylim(0,26)
ax.set_xlabel("Temperature/K")
ax.set_ylabel(f"Molar heat capacity/ {r'Jmol$^{-1}$K$^{-1}$'}")
ax.set_title("Einstein model of solid molar heat capacity")
ax.legend()
ax.grid(alpha=0.3)

plt.show()