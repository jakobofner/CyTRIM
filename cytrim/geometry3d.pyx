# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
"""Cython-optimized 3D geometry support for target definitions.

High-performance versions of geometry classes for fast collision detection.
"""

import numpy as np
cimport numpy as np
from libc.math cimport sqrt, INFINITY

# Abstract base class (Python-level only)
class Geometry3D:
    """Abstract base class for 3D geometries."""
    
    def is_inside_target(self, pos):
        raise NotImplementedError
    
    def get_bounds(self):
        raise NotImplementedError


cdef class BoxGeometry:
    """Cython-optimized rectangular box geometry."""
    
    cdef public double x_min, x_max, y_min, y_max, z_min, z_max
    
    def __init__(self, double x_min, double x_max, double y_min, double y_max,
                 double z_min, double z_max):
        """Initialize box geometry."""
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max
    
    cpdef bint is_inside_target(self, double[:] pos):
        """Check if position is inside the box."""
        return (self.x_min <= pos[0] <= self.x_max and
                self.y_min <= pos[1] <= self.y_max and
                self.z_min <= pos[2] <= self.z_max)
    
    def get_bounds(self):
        """Get bounding box."""
        return ((self.x_min, self.x_max),
                (self.y_min, self.y_max),
                (self.z_min, self.z_max))
    
    def __repr__(self):
        return (f"BoxGeometry(x=[{self.x_min}, {self.x_max}], "
                f"y=[{self.y_min}, {self.y_max}], "
                f"z=[{self.z_min}, {self.z_max}])")


cdef class CylinderGeometry:
    """Cython-optimized cylindrical geometry."""
    
    cdef public double radius, radius_sq, z_min, z_max, center_x, center_y
    
    def __init__(self, double radius, double z_min, double z_max,
                 double center_x=0.0, double center_y=0.0):
        """Initialize cylinder geometry."""
        self.radius = radius
        self.radius_sq = radius * radius
        self.z_min = z_min
        self.z_max = z_max
        self.center_x = center_x
        self.center_y = center_y
    
    cpdef bint is_inside_target(self, double[:] pos):
        """Check if position is inside the cylinder."""
        cdef double dx, dy, r_sq
        
        # Check z bounds
        if not (self.z_min <= pos[2] <= self.z_max):
            return False
        
        # Check radial distance
        dx = pos[0] - self.center_x
        dy = pos[1] - self.center_y
        r_sq = dx * dx + dy * dy
        
        return r_sq <= self.radius_sq
    
    def get_bounds(self):
        """Get bounding box."""
        return ((self.center_x - self.radius, self.center_x + self.radius),
                (self.center_y - self.radius, self.center_y + self.radius),
                (self.z_min, self.z_max))
    
    def __repr__(self):
        return (f"CylinderGeometry(radius={self.radius}, "
                f"z=[{self.z_min}, {self.z_max}], "
                f"center=({self.center_x}, {self.center_y}))")


cdef class SphereGeometry:
    """Cython-optimized spherical geometry."""
    
    cdef public double radius, radius_sq
    cdef public double[:] center
    
    def __init__(self, double radius, double center_x=0.0, 
                 double center_y=0.0, double center_z=0.0):
        """Initialize sphere geometry."""
        self.radius = radius
        self.radius_sq = radius * radius
        self.center = np.array([center_x, center_y, center_z], dtype=np.float64)
    
    cpdef bint is_inside_target(self, double[:] pos):
        """Check if position is inside the sphere."""
        cdef double dx, dy, dz, r_sq
        
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        dz = pos[2] - self.center[2]
        r_sq = dx * dx + dy * dy + dz * dz
        
        return r_sq <= self.radius_sq
    
    def get_bounds(self):
        """Get bounding box."""
        return ((self.center[0] - self.radius, self.center[0] + self.radius),
                (self.center[1] - self.radius, self.center[1] + self.radius),
                (self.center[2] - self.radius, self.center[2] + self.radius))
    
    def __repr__(self):
        return (f"SphereGeometry(radius={self.radius}, "
                f"center=({self.center[0]}, {self.center[1]}, {self.center[2]}))")


cdef class MultiLayerGeometry:
    """Cython-optimized multi-layer planar geometry."""
    
    cdef public double[:] layer_z
    cdef public double z_min, z_max, x_min, x_max, y_min, y_max
    cdef public int n_layers
    
    def __init__(self, layer_z_positions, double x_min=-INFINITY, double x_max=INFINITY,
                 double y_min=-INFINITY, double y_max=INFINITY):
        """Initialize multi-layer geometry."""
        self.layer_z = np.array(sorted(layer_z_positions), dtype=np.float64)
        self.n_layers = len(layer_z_positions) - 1
        self.z_min = self.layer_z[0]
        self.z_max = self.layer_z[self.n_layers]
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
    
    cpdef bint is_inside_target(self, double[:] pos):
        """Check if position is inside any layer."""
        # Check lateral bounds
        if not (self.x_min <= pos[0] <= self.x_max and
                self.y_min <= pos[1] <= self.y_max):
            return False
        
        # Check z bounds
        return self.z_min <= pos[2] <= self.z_max
    
    cpdef int get_layer_index(self, double z):
        """Get the layer index for a given z position."""
        cdef int i
        
        if z < self.z_min or z > self.z_max:
            return -1
        
        for i in range(self.n_layers):
            if self.layer_z[i] <= z < self.layer_z[i + 1]:
                return i
        
        # Handle z exactly at last boundary
        if z == self.z_max:
            return self.n_layers - 1
        
        return -1
    
    def get_bounds(self):
        """Get bounding box."""
        return ((self.x_min, self.x_max),
                (self.y_min, self.y_max),
                (self.z_min, self.z_max))
    
    def __repr__(self):
        return f"MultiLayerGeometry({self.n_layers} layers, z={np.asarray(self.layer_z)})"


cdef class PlanarGeometry:
    """Cython-optimized planar geometry (backward compatibility)."""
    
    cdef public double z_min, z_max
    
    def __init__(self, double z_min, double z_max):
        """Initialize planar geometry."""
        self.z_min = z_min
        self.z_max = z_max
    
    cpdef bint is_inside_target(self, double[:] pos):
        """Check if position is inside the slab."""
        return self.z_min <= pos[2] <= self.z_max
    
    def get_bounds(self):
        """Get bounding box."""
        cdef double large = 5000.0
        return ((-large, large), (-large, large), (self.z_min, self.z_max))
    
    def __repr__(self):
        return f"PlanarGeometry(z=[{self.z_min}, {self.z_max}])"


# Factory function
def create_geometry(geometry_type, **params):
    """Factory function to create geometry objects.
    
    Parameters:
        geometry_type (str): Type of geometry ('box', 'cylinder', 'sphere', 
                            'multilayer', 'planar')
        **params: Geometry-specific parameters
        
    Returns:
        Geometry object
    """
    geometry_type = geometry_type.lower()
    
    if geometry_type == 'box':
        return BoxGeometry(**params)
    elif geometry_type == 'cylinder':
        return CylinderGeometry(**params)
    elif geometry_type == 'sphere':
        return SphereGeometry(**params)
    elif geometry_type == 'multilayer':
        return MultiLayerGeometry(**params)
    elif geometry_type == 'planar':
        return PlanarGeometry(**params)
    else:
        raise ValueError(f"Unknown geometry type: {geometry_type}")


# For backward compatibility
_global_geometry = None

def setup_geometry(geometry):
    """Set global geometry instance."""
    global _global_geometry
    _global_geometry = geometry

def is_inside_target(double[:] pos):
    """Check if position is inside the global geometry."""
    if _global_geometry is None:
        raise RuntimeError("Geometry not set up. Call setup_geometry() first.")
    return _global_geometry.is_inside_target(pos)

def get_global_geometry():
    """Get the current global geometry instance."""
    return _global_geometry
