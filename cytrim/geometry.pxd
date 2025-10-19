# cython: language_level=3
"""Header file for geometry module."""
import numpy as np
cimport numpy as cnp

cpdef bint is_inside_target(cnp.ndarray[cnp.float64_t, ndim=1] pos)
