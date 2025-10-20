# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""Target-geometry related operations (Cython optimized).

This module now acts as a compatibility layer to geometry3d.
Redirects calls to the global geometry3d object if available.

Available functions:
    setup: setup module variables.
    is_inside_target: check if a given position is inside the target
"""
import numpy as np
cimport numpy as cnp

cnp.import_array()

cdef double ZMIN
cdef double ZMAX

# Try to import geometry3d for advanced geometries
_geometry3d = None
try:
    from . import geometry3d as _geometry3d
except ImportError:
    pass


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
    # Try to use geometry3d if available
    if _geometry3d is not None:
        global_geo = _geometry3d.get_global_geometry()
        if global_geo is not None:
            return global_geo.is_inside_target(pos)
    
    # Fallback to simple planar geometry
    cdef double z = pos[2]
    return ZMIN <= z <= ZMAX
