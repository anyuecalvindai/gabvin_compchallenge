import matplotlib.pyplot as plt
import numpy as np

#Constants
c = 2.998e8
h = 6.626e-34
boltzmann = 1.381e-23

B = 0

wavelengths_nm = np.linspace(100, 3000, 500)
wavelengths_m = wavelengths_nm * 1e-9

temperatures = [3000, 4000, 5000, 5778, 7000]

radiances = []

wavelength = 0

def Radiance(temp,wavelength):
    value = ((2*h*(c**2))/((wavelength)**5))/(np.exp((h*c)/(wavelength * boltzmann * temp))-1)
    return value



for T in temperatures:
    B = Radiance(T,wavelengths_m) * 1e-9
    plt.plot(wavelengths_nm, B, label =f"T= {T}K")



plt.xlabel("Wavelength (nm)")
plt.ylabel("Spectral Radiance (W/m²/nm)")
plt.title(f"Spectral Radiance vs Wavelength")
plt.legend()
plt.show()
