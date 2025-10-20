"""Target-geometry related operations.

This module now acts as a compatibility layer to geometry3d.
Redirects calls to the global geometry3d object if available.

Available functions:
    setup: setup module variables.
    is_inside_target: check if a given position is inside the target
"""

# Try to import geometry3d for advanced geometries
try:
    from . import geometry3d as _geometry3d
except ImportError:
    _geometry3d = None

ZMIN = 0
ZMAX = 0


def setup(zmin, zmax):
    """Define the geometry of the target.
    
    Parameters:
        zmin (int): minimum z coordinate of the target (A)
        zmax (int): maximum z coordinate of the target (A)

    Returns:
        None
    """
    global ZMIN, ZMAX

    ZMIN = zmin
    ZMAX = zmax


def is_inside_target(pos):
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
    if ZMIN <= pos[2] <= ZMAX:
        return True
    else:
        return False