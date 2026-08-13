import numpy as np
import scipy.special as sp   # real scipy — must be imported before py/ is on the path
import sys
sys.path.insert(0, 'py')
import orbitals as o

x = np.linspace(-0.99, 0.99, 41)
ok = True
for l in range(6):
    for m in range(-l, l + 1):
        if not np.allclose(o.lpmv(m, l, x), sp.lpmv(m, l, x)):
            print('lpmv disagrees at l =', l, ', m =', m); ok = False

t = np.linspace(0.0, 30.0, 50)
for k in range(6):
    for alpha in range(1, 12, 2):
        if not np.allclose(o.eval_genlaguerre(k, alpha, t), sp.eval_genlaguerre(k, alpha, t)):
            print('laguerre disagrees at k =', k, ', alpha =', alpha); ok = False

print('ALL GOOD — push it' if ok else 'fix the above before pushing')