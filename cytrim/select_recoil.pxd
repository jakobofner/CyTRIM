# cython: language_level=3
"""Header file for select_recoil module."""
import numpy as np
cimport numpy as cnp

cpdef tuple get_recoil_position(cnp.ndarray[cnp.float64_t, ndim=1] pos, 
                                 cnp.ndarray[cnp.float64_t, ndim=1] dir)
