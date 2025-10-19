# cython: language_level=3
"""Header file for scatter module."""
import numpy as np
cimport numpy as cnp

cpdef tuple scatter(double e, cnp.ndarray[cnp.float64_t, ndim=1] dir, 
                    double p, cnp.ndarray[cnp.float64_t, ndim=1] dirp)
