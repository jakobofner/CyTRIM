"""Advanced 3D geometry support for target definitions.

This module provides various geometry types for more realistic target simulations:
- BoxGeometry: Rectangular box (x_min/max, y_min/max, z_min/max)
- CylinderGeometry: Cylindrical target (radius, height)
- SphereGeometry: Spherical target (radius)
- MultiLayerGeometry: Stacked layers with different materials

All geometries support:
- is_inside_target(pos): Check if position is inside
- get_bounds(): Get bounding box for visualization
- get_intersection(pos, dir): Ray-target intersection
"""

import numpy as np
from abc import ABC, abstractmethod


class Geometry3D(ABC):
    """Abstract base class for 3D geometries."""
    
    @abstractmethod
    def is_inside_target(self, pos):
        """Check if a position is inside the target.
        
        Parameters:
            pos (ndarray): position to check (size 3, in Angstrom)
            
        Returns:
            bool: True if inside target, False otherwise
        """
        pass
    
    @abstractmethod
    def get_bounds(self):
        """Get bounding box of the geometry.
        
        Returns:
            tuple: ((x_min, x_max), (y_min, y_max), (z_min, z_max))
        """
        pass
    
    def get_intersection(self, pos, direction):
        """Calculate intersection point of a ray with the target surface.
        
        Parameters:
            pos (ndarray): starting position (size 3)
            direction (ndarray): ray direction (size 3, normalized)
            
        Returns:
            ndarray or None: intersection point, or None if no intersection
            float: distance to intersection, or np.inf if no intersection
        """
        # Default implementation: simple ray marching
        # Subclasses can override with analytical solutions
        max_distance = 10000.0  # Angstrom
        step_size = 10.0
        
        current_pos = pos.copy()
        distance = 0.0
        
        was_inside = self.is_inside_target(pos)
        
        while distance < max_distance:
            current_pos = pos + direction * distance
            is_inside = self.is_inside_target(current_pos)
            
            # Detect boundary crossing
            if was_inside != is_inside:
                # Refine with smaller steps
                back_pos = pos + direction * (distance - step_size)
                for i in range(10):
                    mid_pos = (current_pos + back_pos) / 2
                    if self.is_inside_target(mid_pos) == is_inside:
                        current_pos = mid_pos
                    else:
                        back_pos = mid_pos
                return current_pos, distance
            
            distance += step_size
        
        return None, np.inf


class BoxGeometry(Geometry3D):
    """Rectangular box geometry.
    
    Defines a target as a 3D box with specified bounds in each direction.
    """
    
    def __init__(self, x_min, x_max, y_min, y_max, z_min, z_max):
        """Initialize box geometry.
        
        Parameters:
            x_min, x_max (float): x bounds in Angstrom
            y_min, y_max (float): y bounds in Angstrom
            z_min, z_max (float): z bounds in Angstrom
        """
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max
    
    def is_inside_target(self, pos):
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


class CylinderGeometry(Geometry3D):
    """Cylindrical geometry.
    
    Defines a cylinder with axis along z-direction.
    """
    
    def __init__(self, radius, z_min, z_max, center_x=0.0, center_y=0.0):
        """Initialize cylinder geometry.
        
        Parameters:
            radius (float): cylinder radius in Angstrom
            z_min, z_max (float): z bounds in Angstrom
            center_x, center_y (float): center position in x-y plane
        """
        self.radius = radius
        self.radius_sq = radius * radius
        self.z_min = z_min
        self.z_max = z_max
        self.center_x = center_x
        self.center_y = center_y
    
    def is_inside_target(self, pos):
        """Check if position is inside the cylinder."""
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


class SphereGeometry(Geometry3D):
    """Spherical geometry.
    
    Defines a spherical target.
    """
    
    def __init__(self, radius, center_x=0.0, center_y=0.0, center_z=0.0):
        """Initialize sphere geometry.
        
        Parameters:
            radius (float): sphere radius in Angstrom
            center_x, center_y, center_z (float): center position
        """
        self.radius = radius
        self.radius_sq = radius * radius
        self.center = np.array([center_x, center_y, center_z])
    
    def is_inside_target(self, pos):
        """Check if position is inside the sphere."""
        diff = pos - self.center
        r_sq = np.dot(diff, diff)
        return r_sq <= self.radius_sq
    
    def get_bounds(self):
        """Get bounding box."""
        return ((self.center[0] - self.radius, self.center[0] + self.radius),
                (self.center[1] - self.radius, self.center[1] + self.radius),
                (self.center[2] - self.radius, self.center[2] + self.radius))
    
    def __repr__(self):
        return (f"SphereGeometry(radius={self.radius}, "
                f"center=({self.center[0]}, {self.center[1]}, {self.center[2]}))")


class MultiLayerGeometry(Geometry3D):
    """Multi-layer planar geometry.
    
    Defines multiple horizontal layers stacked in z-direction.
    Each layer can have different material properties (handled externally).
    """
    
    def __init__(self, layer_z_positions, x_min=-np.inf, x_max=np.inf, 
                 y_min=-np.inf, y_max=np.inf):
        """Initialize multi-layer geometry.
        
        Parameters:
            layer_z_positions (list): z positions of layer boundaries, sorted
                Example: [0, 100, 300] creates 2 layers: [0,100] and [100,300]
            x_min, x_max (float): optional lateral bounds
            y_min, y_max (float): optional lateral bounds
        """
        self.layer_z = sorted(layer_z_positions)
        self.z_min = self.layer_z[0]
        self.z_max = self.layer_z[-1]
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
    
    def is_inside_target(self, pos):
        """Check if position is inside any layer."""
        # Check lateral bounds
        if not (self.x_min <= pos[0] <= self.x_max and
                self.y_min <= pos[1] <= self.y_max):
            return False
        
        # Check z bounds
        return self.z_min <= pos[2] <= self.z_max
    
    def get_layer_index(self, z):
        """Get the layer index for a given z position.
        
        Parameters:
            z (float): z position
            
        Returns:
            int: layer index (0 to n_layers-1), or -1 if outside
        """
        if z < self.z_min or z > self.z_max:
            return -1
        
        for i in range(len(self.layer_z) - 1):
            if self.layer_z[i] <= z < self.layer_z[i + 1]:
                return i
        
        # Handle z exactly at last boundary
        if z == self.z_max:
            return len(self.layer_z) - 2
        
        return -1
    
    def get_bounds(self):
        """Get bounding box."""
        return ((self.x_min, self.x_max),
                (self.y_min, self.y_max),
                (self.z_min, self.z_max))
    
    def __repr__(self):
        return (f"MultiLayerGeometry({len(self.layer_z)-1} layers, "
                f"z={self.layer_z})")


class PlanarGeometry(Geometry3D):
    """Simple planar geometry (for backward compatibility).
    
    Infinite slab in x-y directions, bounded only in z.
    This is equivalent to the original geometry.py behavior.
    """
    
    def __init__(self, z_min, z_max):
        """Initialize planar geometry.
        
        Parameters:
            z_min, z_max (float): z bounds in Angstrom
        """
        self.z_min = z_min
        self.z_max = z_max
    
    def is_inside_target(self, pos):
        """Check if position is inside the slab."""
        return self.z_min <= pos[2] <= self.z_max
    
    def get_bounds(self):
        """Get bounding box."""
        # Use large but finite bounds for visualization
        large = 5000.0
        return ((-large, large), (-large, large), (self.z_min, self.z_max))
    
    def __repr__(self):
        return f"PlanarGeometry(z=[{self.z_min}, {self.z_max}])"


# Factory function for easy geometry creation
def create_geometry(geometry_type, **params):
    """Factory function to create geometry objects.
    
    Parameters:
        geometry_type (str): Type of geometry ('box', 'cylinder', 'sphere', 
                            'multilayer', 'planar')
        **params: Geometry-specific parameters
        
    Returns:
        Geometry3D: Geometry object
        
    Examples:
        >>> geo = create_geometry('box', x_min=-100, x_max=100, 
        ...                       y_min=-100, y_max=100, z_min=0, z_max=500)
        >>> geo = create_geometry('cylinder', radius=200, z_min=0, z_max=1000)
        >>> geo = create_geometry('sphere', radius=300)
        >>> geo = create_geometry('multilayer', layer_z_positions=[0, 100, 300])
        >>> geo = create_geometry('planar', z_min=0, z_max=500)
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


# For backward compatibility with old geometry.py
_global_geometry = None

def setup_geometry(geometry):
    """Set global geometry instance (for backward compatibility).
    
    Parameters:
        geometry (Geometry3D): Geometry object to use globally
    """
    global _global_geometry
    _global_geometry = geometry

def is_inside_target(pos):
    """Check if position is inside the global geometry.
    
    Parameters:
        pos (ndarray): position to check
        
    Returns:
        bool: True if inside, False otherwise
    """
    if _global_geometry is None:
        raise RuntimeError("Geometry not set up. Call setup_geometry() first.")
    return _global_geometry.is_inside_target(pos)

def get_global_geometry():
    """Get the current global geometry instance."""
    return _global_geometry
