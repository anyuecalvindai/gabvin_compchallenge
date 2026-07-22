import numpy as np
import matplotlib.pyplot as plt

N = int(1e6) #number of steps
L = 1 # step size
N_walks = 5
rng = np.random.default_rng()

def random_walk(L, N ,rng=rng):
    theta = 2 *np.pi *rng.random(N)
    dx = L*np.cos(theta)
    dy = L*np.sin(theta)
    x = np.concatenate(([0.0], np.cumsum(dx)))
    y = np.concatenate(([0.0], np.cumsum(dy)))
    return x, y

def main():
    fig, ax = plt.subplots()
    for _ in range(N_walks):
        x, y = random_walk(L, N)
        ax.plot(x, y, color=tuple(rng.random(3)), linewidth=0.5)
 
    ax.grid(True)             
    ax.set_axisbelow(True)
    ax.set_aspect('equal')       
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Random Walk')
    plt.show()

main()