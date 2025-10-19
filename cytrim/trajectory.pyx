# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""Simulate projectile trajectories (Cython optimized).

Available functions:
    setup: setup module variables.
    trajectory: simulate one trajectory.
    trajectory_with_path: simulate one trajectory with path recording.
"""
import numpy as np
cimport numpy as cnp
from . cimport select_recoil
from . cimport scatter
from . cimport estop
from . cimport geometry

cnp.import_array()

cdef double EMIN = 5.0


def setup():
    """Setup module variables.

    Parameters:
        None

    Returns:
        None    
    """
    global EMIN
    EMIN = 5.0


cpdef tuple trajectory(cnp.ndarray[cnp.float64_t, ndim=1] pos_init, 
                       cnp.ndarray[cnp.float64_t, ndim=1] dir_init, 
                       double e_init):
    """Simulate one trajectory.
    
    Parameters:
        pos_init (ndarray): initial position of the projectile (size 3)
        dir_init (ndarray): initial direction of the projectile (size 3)
        e_init (float): initial energy of the projectile (eV)

    Returns:
        tuple: (pos, dir, e, is_inside)
    """
    cdef cnp.ndarray[cnp.float64_t, ndim=1] pos = pos_init.copy()
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dir = dir_init.copy()
    cdef double e = e_init
    cdef bint is_inside = True
    cdef double free_path, p, dee
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dirp
    cdef cnp.ndarray[cnp.float64_t, ndim=1] pos_recoil
    cdef int i

    while e > EMIN:
        free_path, p, dirp, pos_recoil = select_recoil.get_recoil_position(pos, dir)
        dee = estop.eloss(e, free_path)
        e -= dee
        
        for i in range(3):
            pos[i] += free_path * dir[i]
        
        if not geometry.is_inside_target(pos):
            is_inside = False
            break
        
        dir, e, _, _ = scatter.scatter(e, dir, p, dirp)

    return (pos, dir, e, is_inside)


def trajectory_with_path(cnp.ndarray[cnp.float64_t, ndim=1] pos_init, 
                         cnp.ndarray[cnp.float64_t, ndim=1] dir_init, 
                         double e_init, bint record_path=False):
    """Simulate one trajectory and optionally record the path.
    
    Parameters:
        pos_init (ndarray): initial position of the projectile (size 3)
        dir_init (ndarray): initial direction of the projectile (size 3)
        e_init (float): initial energy of the projectile (eV)
        record_path (bool): whether to record the trajectory path

    Returns:
        tuple: (pos, dir, e, is_inside, path)
    """
    cdef cnp.ndarray[cnp.float64_t, ndim=1] pos = pos_init.copy()
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dir = dir_init.copy()
    cdef double e = e_init
    cdef bint is_inside = True
    cdef list path = None
    cdef double free_path, p, dee
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dirp
    cdef cnp.ndarray[cnp.float64_t, ndim=1] pos_recoil
    cdef int i
    
    if record_path:
        path = [pos.copy()]

    while e > EMIN:
        free_path, p, dirp, pos_recoil = select_recoil.get_recoil_position(pos, dir)
        dee = estop.eloss(e, free_path)
        e -= dee
        
        for i in range(3):
            pos[i] += free_path * dir[i]
        
        if record_path:
            path.append(pos.copy())
        
        if not geometry.is_inside_target(pos):
            is_inside = False
            break
        
        dir, e, _, _ = scatter.scatter(e, dir, p, dirp)

    return (pos, dir, e, is_inside, path)
