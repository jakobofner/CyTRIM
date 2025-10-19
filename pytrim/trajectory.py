"""Simulate projectile trajectories.

Available functions:
    setup: setup module variables.
    trajectory: simulate one trajectory."""
from .select_recoil import get_recoil_position
from .scatter import scatter
from .estop import eloss
from .geometry import is_inside_target

def setup():
    """Setup module variables.

    Parameters:
        None

    Returns:
        None    
    """
    global EMIN

    EMIN = 5.0  # eV


def trajectory(pos_init, dir_init, e_init):
    """Simulate one trajectory.
    
    Parameters:
        pos_init (ndarray): initial position of the projectile (size 3)
        dir_init (ndarray): initial direction of the projectile (size 3)
        e_init (float): initial energy of the projectile (eV)

    Returns:
        ndarray: final position of the projectile (size 3)
        ndarray: final direction of the projectile (size 3)
        float: final energy of the projectile (eV)
        bool: True if projectile is stopped inside the target, 
            False otherwise
    """
    pos = pos_init.copy()
    dir = dir_init.copy()
    e = e_init
    is_inside = True

    while e > EMIN:
        free_path, p, dirp, _ = get_recoil_position(pos, dir)
        dee = eloss(e, free_path)
        e -= dee
        pos += free_path * dir
        if not is_inside_target(pos):
            is_inside = False
            break
        dir, e, _, _ = scatter(e, dir, p, dirp)

    return pos, dir, e, is_inside


def trajectory_with_path(pos_init, dir_init, e_init, record_path=False):
    """Simulate one trajectory and optionally record the path.
    
    Parameters:
        pos_init (ndarray): initial position of the projectile (size 3)
        dir_init (ndarray): initial direction of the projectile (size 3)
        e_init (float): initial energy of the projectile (eV)
        record_path (bool): whether to record the trajectory path

    Returns:
        ndarray: final position of the projectile (size 3)
        ndarray: final direction of the projectile (size 3)
        float: final energy of the projectile (eV)
        bool: True if projectile is stopped inside the target, 
            False otherwise
        list or None: list of positions along the trajectory if record_path
            is True, None otherwise
    """
    import numpy as np
    
    pos = pos_init.copy()
    dir = dir_init.copy()
    e = e_init
    is_inside = True
    
    path = [pos.copy()] if record_path else None

    while e > EMIN:
        free_path, p, dirp, _ = get_recoil_position(pos, dir)
        dee = eloss(e, free_path)
        e -= dee
        pos += free_path * dir
        
        if record_path:
            path.append(pos.copy())
        
        if not is_inside_target(pos):
            is_inside = False
            break
        dir, e, _, _ = scatter(e, dir, p, dirp)

    return pos, dir, e, is_inside, path