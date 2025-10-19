# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""Create the recoil position for the next collision (Cython optimized).

Currently, only amorphous targets are supported. The free path length to
the next collision is assumed to be constant and equal to the atomic
density to the power -1/3.

Available functions:
    setup: setup module variables.
    get_recoil_position: get the recoil position.
"""
from libc.math cimport sqrt, sin, cos, M_PI
import numpy as np
cimport numpy as cnp
from libc.stdlib cimport rand, RAND_MAX

cnp.import_array()

cdef double PMAX
cdef double MEAN_FREE_PATH


def setup(double density):
    """Setup module variables depending on target density.

    Parameters:
        density (float): target density (atoms/A^3)

    Returns:
        None    
    """
    global PMAX, MEAN_FREE_PATH

    MEAN_FREE_PATH = density**(-1.0/3.0)
    PMAX = MEAN_FREE_PATH / sqrt(M_PI)


cdef inline double random_uniform() nogil:
    """Generate random number between 0 and 1."""
    return <double>rand() / <double>RAND_MAX


cpdef tuple get_recoil_position(cnp.ndarray[cnp.float64_t, ndim=1] pos, 
                                 cnp.ndarray[cnp.float64_t, ndim=1] dir):
    """Get the recoil position based on the projectile position and direction.

    Parameters:
        pos (ndarray): position of the projectile (size 3)
        dir (ndarray): direction vector of the projectile (size 3)

    Returns:
        tuple: (free_path, p, dirp, pos_recoil)
    """
    cdef double free_path = MEAN_FREE_PATH
    cdef cnp.ndarray[cnp.float64_t, ndim=1] pos_collision = np.empty(3, dtype=np.float64)
    cdef double p, fi, cos_fi, sin_fi
    cdef int k, i, j
    cdef double cos_alpha, sin_alpha, cos_phi, sin_phi
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dirp = np.empty(3, dtype=np.float64)
    cdef cnp.ndarray[cnp.float64_t, ndim=1] pos_recoil = np.empty(3, dtype=np.float64)
    cdef double norm
    cdef int idx
    
    # Calculate collision position
    for idx in range(3):
        pos_collision[idx] = pos[idx] + free_path * dir[idx]

    # Random impact parameter
    p = PMAX * sqrt(np.random.rand())
    
    # Random azimuthal angle
    fi = 2.0 * M_PI * np.random.rand()
    cos_fi = cos(fi)
    sin_fi = sin(fi)

    # Find index k with smallest |dir[k]|
    k = 0
    cdef double min_abs = abs(dir[0])
    for idx in range(1, 3):
        if abs(dir[idx]) < min_abs:
            min_abs = abs(dir[idx])
            k = idx
    
    i = (k + 1) % 3
    j = (i + 1) % 3
    
    cos_alpha = dir[k]
    sin_alpha = sqrt(dir[i]*dir[i] + dir[j]*dir[j])
    cos_phi = dir[i] / sin_alpha
    sin_phi = dir[j] / sin_alpha

    # Direction vector from collision point to recoil
    dirp[i] = cos_fi*cos_alpha*cos_phi - sin_fi*sin_phi
    dirp[j] = cos_fi*cos_alpha*sin_phi + sin_fi*cos_phi
    dirp[k] = -cos_fi*sin_alpha
    
    # Normalize dirp
    norm = sqrt(dirp[0]*dirp[0] + dirp[1]*dirp[1] + dirp[2]*dirp[2])
    for idx in range(3):
        dirp[idx] /= norm

    # Position of the recoil
    for idx in range(3):
        pos_recoil[idx] = pos_collision[idx] + p * dirp[idx]

    return (free_path, p, dirp, pos_recoil)
