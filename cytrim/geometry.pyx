# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""Target-geometry related operations (Cython optimized).

Currently, only a planar target geometry is supported.

Available functions:
    setup: setup module variables.
    is_inside_target: check if a given position is inside the target
"""
import numpy as np
cimport numpy as cnp

cnp.import_array()

cdef double ZMIN
cdef double ZMAX


def setup(double zmin, double zmax):
    """Define the geometry of the target.
    
    Parameters:
        zmin (float): minimum z coordinate of the target (A)
        zmax (float): maximum z coordinate of the target (A)

    Returns:
        None
    """
    global ZMIN, ZMAX

    ZMIN = zmin
    ZMAX = zmax


cpdef bint is_inside_target(cnp.ndarray[cnp.float64_t, ndim=1] pos):
    """Check if a given position is inside the target.

    Parameters:
        pos (ndarray): position to check (size 3)

    Returns:
        bool: True if position is inside the target, False otherwise
    """
    cdef double z = pos[2]
    return ZMIN <= z <= ZMAX
