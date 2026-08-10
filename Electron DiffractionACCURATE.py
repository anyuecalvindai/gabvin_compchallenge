import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

#Constants
h = 6.626e-34
Me = 9.1093837139e-31
e = 1.6021766e-19
c = 2.998e8

r = 65

d1 = 0.123e-9
d2 = 0.213e-9

radii = {}
num = 0

Intensity0 = 5
bragg_angle = 0

themes = {
    'simulation':  {'bg': 'black', 'fg': 'white'},
    'graph': {'bg': 'white', 'fg': 'black'},
}
current_theme = 'simulation'

def applyTheme(theme_name):
    t = themes[theme_name]

    fig.patch.set_facecolor(t['bg'])
    ax.set_facecolor(t['bg'])
    ax_slider.set_facecolor(t['bg'])

    ax.xaxis.label.set_color(t['fg'])
    ax.yaxis.label.set_color(t['fg'])
    ax.title.set_color(t['fg'])
    ax.tick_params(colors=t['fg'])
    for spine in ax.spines.values():
        spine.set_color(t['fg'])

    voltage_slider.label.set_color(t['fg'])
    voltage_slider.valtext.set_color(t['fg'])
    
    update(voltage_slider.val)
    
    if theme_name == "graph":
        for name, circle in circles.items():
            if name[0:2] == "d2":
                circle.set_linestyle(":")
            n = int(name.split("=")[1])
            circle.set_edgecolor(f"C{n}")
        ax.legend()
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    
    else:
        for name, circle in circles.items():
            if name[0:2] == "d2":
                circle.set_linestyle("-")
        ax.legend().remove()
        
    fig.canvas.draw_idle()

def Electron_Wavelength(V):
    return h/((2*Me*V*e*(1+(e*V)/(2*Me*(c**2))))**(1/2))

def Bragg(wavelength,d,n):
    num = n*wavelength/(2*d)
    if num <=1:
        angle = 2* np.arcsin(num)
        if angle <= np.pi/4:
            return angle, r * np.sin(2*angle)
    return None, None

def get_radii(wavelength,d1,d2):
    radii = {}
    angles = {}

    for d, label in [(d1, "d1"),(d2, "d2")]:
        counter = 1
        while True:
            angle, radius = Bragg(wavelength,d,counter)
            if radius is None:
                break
            radii[f"{label}, n={counter}"] = radius
            angles[f"{label}, n={counter}"] = angle
            counter += 1

    return radii, angles

def get_intensity(angle,n,intensity):
    return intensity * np.exp(-2.0 * angle**2)/ n**2

V0 = 5000
wavelength0 = Electron_Wavelength(V0)
radii, angles = get_radii(wavelength0,d1,d2)
Intensity0 = 1e-3 * (V0)

black_green = LinearSegmentedColormap.from_list("black_green", ["black", "limegreen"])

fig, ax = plt.subplots(figsize=(10,6))
plt.subplots_adjust(bottom=0.25)
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

fig.text(0.68, 0.35, "d1 = 0.123 nm\nd2 = 0.213 nm",
          fontsize=10, ha='left', va='top',
          )

circles = {}

for name, radius in radii.items():
    n = int(name.split("=")[1])
    angle = angles[name]
    intensity = get_intensity(angle, n, Intensity0)
    color = black_green(intensity)
    radius = radii.get(name, 0)
    circle = plt.Circle((0, 0), radius, fill=False, linewidth=2, 
                          edgecolor=color, label=name)
    ax.add_patch(circle)
    circles[name] = circle


ax.set_xlim(-70, 70)
ax.set_ylim(-70, 70)
ax.set_xlabel("mm", color='white')
ax.set_ylabel("mm", color='white')
ax.set_aspect('equal')
ax.tick_params(colors='white')
ax.set_title(f"Diffraction Rings (V = {V0} V)", color="white")
plt.grid(alpha=0.3)

ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
voltage_slider = Slider(ax_slider, 'Voltage (V)', 1000, V0, valinit=V0, valstep=10)
voltage_slider.label.set_color('white')
voltage_slider.valtext.set_color('white')

ax_check = plt.axes([0.2, 0.02, 0.15, 0.06])
check = CheckButtons(ax_check, ["Simulation"], [True])

def BraggAngle(wavelength,d,n):
    num = n*wavelength/(2*d)

    return 2* np.arcsin(num)

def update(val):
    V = voltage_slider.val
    wavelength = Electron_Wavelength(V)
    radii, angles = get_radii(wavelength, d1, d2)

    intensityMult = 1e-3 * (V)

    if current_theme == "simulation":
        for name, circle in circles.items():
            radius = radii.get(name, 0)
            circle.set_radius(radius)
            if name in angles:
                n = int(name.split("=")[1])
                intensity = get_intensity(angles[name], n, intensityMult)
                circle.set_edgecolor(black_green(intensity))
    else:
        for name, circle in circles.items():
                radius = radii.get(name, 0)
                circle.set_radius(radius)
    
    ax.set_title(f"Diffraction Rings (V = {V:.0f} V)")
    fig.canvas.draw_idle()

def toggleTheme(label):
    global current_theme
    if current_theme == "simulation":
        current_theme = 'graph'
    else:
        current_theme = 'simulation'
    applyTheme(current_theme)

voltages = np.linspace(1000, 5000, 1000)
wavelengths = Electron_Wavelength(voltages)
phi = BraggAngle(wavelengths,d2,1)

y = np.sin(phi/2)

fig2, ax2 = plt.subplots(figsize=(7,5))
ax2.plot(1/np.sqrt(voltages), y)
ax2.set_xlabel("1/√V")
ax2.set_ylabel("sin(½ϕ)")
ax2.set_title("Innermost Ring Radius vs 1/√V")


voltage_slider.on_changed(update)

check.on_clicked(toggleTheme)
applyTheme("simulation")

plt.show()