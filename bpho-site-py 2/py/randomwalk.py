# Physics from "randomwalk.py"; plotting is done by the JS layer.

import numpy as np

L = 1 # step size
rng = np.random.default_rng()


def random_walk(L, N ,rng=rng):
    theta = 2 *np.pi *rng.random(N)
    dx = L*np.cos(theta)
    dy = L*np.sin(theta)
    x = np.concatenate(([0.0], np.cumsum(dx)))
    y = np.concatenate(([0.0], np.cumsum(dy)))
    return x, y


# ---- adapter for the web UI ----

def web_walks(n_walks, N):
    walks = []
    for _ in range(int(n_walks)):
        x, y = random_walk(L, int(N))
        # 3 d.p. is far below one pixel; keeps the JSON payload sane at 10^6 steps
        walks.append({
            "x": np.round(x, 3).tolist(),
            "y": np.round(y, 3).tolist(),
        })
    return walks
