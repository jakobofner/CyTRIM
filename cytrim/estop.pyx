# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""Calculate the electronic stopping power (Cython optimized).

Currently, only the Lindhard model (Phys. Rev. 124, (1961) 128) with 
a correction factor is implemented.

Available functions:
    setup: setup module variables.
    eloss: calculate the electronic energy loss.
"""
from libc.math cimport sqrt

cdef double FAC_LINDHARD
cdef double DENSITY


def setup(double corr_lindhard, int z1, double m1, int z2, double density):
    """Setup module variables depending on target density.

    Parameters:
        corr_lindhard (float): Correction factor to Lindhard stopping power
        z1 (int): atomic number of projectile
        m1 (float): mass of projectile (amu)
        z2 (int): atomic number of target
        density (float): target density (atoms/A^3)

    Returns:
        None    
    """
    global FAC_LINDHARD, DENSITY
    
    cdef double z1_pow = z1**(7.0/6.0)
    cdef double z1_23 = z1**(2.0/3.0)
    cdef double z2_23 = z2**(2.0/3.0)
    cdef double denominator = (z1_23 + z2_23)**(3.0/2.0) * sqrt(m1)

    FAC_LINDHARD = corr_lindhard * 1.212 * z1_pow * z2 / denominator
    DENSITY = density


cpdef double eloss(double e, double free_path):
    """Calculate the electronic energy loss over a given free path length.

    Parameters:
        e (float): energy of the projectile (eV)
        free_path (float): free path length (A)

    Returns:
        float: energy loss (eV)
    """
    cdef double dee = FAC_LINDHARD * DENSITY * sqrt(e) * free_path
    if dee > e:
        dee = e
    return dee
