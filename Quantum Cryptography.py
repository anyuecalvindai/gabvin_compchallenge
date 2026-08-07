import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

phi = 0
theta = 0

def ClassicalProb(phi, theta):
    return 1 - ((np.cos(np.radians(theta))**2)*(np.cos(np.radians(phi))**2)) - ((np.sin(np.radians(theta))**2)*(np.sin(np.radians(phi))**2))

def QMProb(phi, theta):
    return np.sin(np.radians(phi-theta))**2

def plot_detector(ax, origin, angle_deg, label="Detector", 
                   xlabel="X", ylabel="Y", color="green"):
    
    theta = np.radians(angle_deg)


    x_dir = np.array([np.sin(theta), np.cos(theta)])
    # Y-arm: perpendicular to X-arm (rotate by -90 deg)
    y_dir = np.array([x_dir[1], -x_dir[0]]) * -1  
    # (tune sign so Y points "down-left" like in the figure)

    ox, oy = origin
    L = 1.5  # arm length

    # dashed vertical reference line
    ax.plot([ox, ox], [oy, oy + L], 'b--', lw=1)

    # X arrow
    ax.arrow(ox, oy, x_dir[0]*L, x_dir[1]*L, head_width=0.1, head_length=0.1, fc=color, ec=color, length_includes_head=True)
    ax.text(ox + x_dir[0]*L*1.2, oy + x_dir[1]*L*1.2, xlabel, color="black")

    # Y arrow
    ax.arrow(ox, oy, y_dir[0]*L, y_dir[1]*L, head_width=0.1, head_length=0.1, fc=color, ec=color, length_includes_head=True)
    ax.text(ox + y_dir[0]*L*1.2, oy + y_dir[1]*L*1.2, ylabel, color="black")

    # angle arc/label
    ax.text(ox-1.6, oy - L*1.4, label, fontweight='bold')

formula_artists = []
def draw_formulas(fig, phi_val, theta_val):
    global formula_artists
    # remove previous formula text
    for artist in formula_artists:
        artist.remove()
    formula_artists = []

    cos_t = np.cos(np.radians(theta_val))
    cos_p = np.cos(np.radians(phi_val))
    sin_t = np.sin(np.radians(theta_val))
    sin_p = np.sin(np.radians(phi_val))
    classical = ClassicalProb(phi_val, theta_val)

    diff = phi_val - theta_val
    sin_diff = np.sin(np.radians(diff))
    qm = QMProb(phi_val, theta_val)

    classical_text = (
        r"$\bf{Classical}$" + "\n"
        r"$P(\mathrm{mismatch}) = 1-\cos^2\theta\cos^2\phi-\sin^2\theta\sin^2\phi$" + "\n"
        fr"$=1-({cos_t:.3f})^2({cos_p:.3f})^2-({sin_t:.3f})^2({sin_p:.3f})^2$" + "\n"
        fr"$=\mathbf{{{classical:.3f}}}$"
    )

    qm_text = (
        r"$\bf{QM}$" + "\n"
        r"$P(\mathrm{mismatch}) = \sin^2(\phi-\theta)$" + "\n"
        fr"$=\sin^2({phi_val}^\circ-({theta_val}^\circ))=\sin^2({diff}^\circ)$" + "\n"
        fr"$=\mathbf{{{qm:.3f}}}$"
    )

    t1 = fig.text(0.15, 0.20, classical_text, fontsize=10, va='top', ha='left')
    t2 = fig.text(0.55, 0.20, qm_text, fontsize=10, va='top', ha='left')
    formula_artists = [t1, t2]

def draw_all(ax, phi_val, theta_val):
    ax.clear()

    plot_detector(ax, origin=(0,4), angle_deg=phi_val,
                  xlabel="$X_A$", ylabel="$Y_A$", label=f"Detector A: φ = {phi_val}", color="green")

    plot_detector(ax, origin=(4,4), angle_deg=theta_val,
                  xlabel="$X_B$", ylabel="$Y_B$", label=f"Detector B: θ = {theta_val}", color="blue")

    ax.set_xlim(-2, 6)
    ax.set_ylim(2, 6)
    ax.set_aspect('equal')
    ax.axis('off')

    draw_formulas(fig, phi_val, theta_val)

fig, ax = plt.subplots(figsize=(6,6))
plt.subplots_adjust(bottom=0.35)

draw_all(ax, phi, theta)

phi_ax_slider = plt.axes([0.25, 0.35, 0.2, 0.03])
phi_slider = Slider(phi_ax_slider, '', -180, 180, valinit=0, valstep=1)
phi_ax_slider.text(0.5, -1.0, 'φ (Detector A)', transform=phi_ax_slider.transAxes,
                    ha='center', va='top', fontsize=9)

theta_ax_slider = plt.axes([0.55, 0.35, 0.2, 0.03])
theta_slider = Slider(theta_ax_slider, '', -180, 180, valinit=0, valstep=1)
theta_ax_slider.text(0.5, -1.0, 'θ (Detector B)', transform=theta_ax_slider.transAxes,
                      ha='center', va='top', fontsize=9)

def update (val):
    draw_all(ax, phi_slider.val, theta_slider.val)
    fig.canvas.draw_idle()

phi_slider.on_changed(update)
theta_slider.on_changed(update)

plt.show()