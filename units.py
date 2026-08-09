#File containing useful custom unit conversions to make code look a bit nicer
#Feel free to add your own, import to each file you want to use it in separately.

import scipy.constants as const

def joule_eV(E):
    return E/const.e

def eV_joule(E):
    return E*const.e
