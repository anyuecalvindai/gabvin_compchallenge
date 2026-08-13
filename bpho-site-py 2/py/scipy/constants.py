# Values copied from scipy.constants (CODATA), so results match the
# desktop versions of the scripts exactly.

h = 6.62607015e-34
hbar = 1.0545718176461565e-34
c = 299792458.0
e = 1.602176634e-19
eV = 1.602176634e-19
m_e = 9.1093837139e-31
m_p = 1.67262192595e-27
epsilon_0 = 8.8541878188e-12
pi = 3.141592653589793

_values = {
    'Bohr radius': 5.29177210544e-11,
}


def value(key):
    return _values[key]
