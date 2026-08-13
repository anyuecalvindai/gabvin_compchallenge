# Physics from "Quantum Cryptography.py"; the detector sketch is drawn by the JS layer.

import numpy as np


def ClassicalProb(phi, theta):
    return 1 - ((np.cos(np.radians(theta))**2)*(np.cos(np.radians(phi))**2)) - ((np.sin(np.radians(theta))**2)*(np.sin(np.radians(phi))**2))


def QMProb(phi, theta):
    return np.sin(np.radians(phi-theta))**2


# ---- adapter for the web UI ----

def web_probs(phi, theta):
    return {
        "classical": float(ClassicalProb(phi, theta)),
        "qm": float(QMProb(phi, theta)),
        "cos_t": float(np.cos(np.radians(theta))),
        "cos_p": float(np.cos(np.radians(phi))),
        "sin_t": float(np.sin(np.radians(theta))),
        "sin_p": float(np.sin(np.radians(phi))),
    }
