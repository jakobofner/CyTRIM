"""3D visualization canvas for PyTRIM GUI.

Provides matplotlib-based 3D plotting for trajectories and target geometries.
"""

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class PlotCanvas3D(FigureCanvasQTAgg):
    """3D matplotlib canvas for PyQt6."""
    
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        """Initialize 3D plot canvas."""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Set labels
        self.ax.set_xlabel('X (Å)', fontsize=10)
        self.ax.set_ylabel('Y (Å)', fontsize=10)
        self.ax.set_zlabel('Z (Å)', fontsize=10)
        self.ax.set_title('3D Ion Trajectories', fontsize=12)
        
    def plot_trajectories(self, trajectories, geometry_obj=None):
        """Plot 3D trajectories with optional geometry."""
        self.ax.clear()
        
        # Plot trajectories
        if trajectories:
            colors = plt.cm.viridis(np.linspace(0, 1, len(trajectories)))
            
            for i, traj in enumerate(trajectories):
                if len(traj) > 0:
                    traj_array = np.array(traj)
                    self.ax.plot(traj_array[:, 0], 
                               traj_array[:, 1], 
                               traj_array[:, 2],
                               color=colors[i],
                               linewidth=1.5,
                               alpha=0.7)
        
        # Plot geometry bounds
        if geometry_obj is not None:
            self._plot_geometry(geometry_obj)
        
        # Set labels
        self.ax.set_xlabel('X (Å)', fontsize=10)
        self.ax.set_ylabel('Y (Å)', fontsize=10)
        self.ax.set_zlabel('Z (Å)', fontsize=10)
        self.ax.set_title('3D Ion Trajectories', fontsize=12)
        
        # Set equal aspect ratio
        self._set_axes_equal()
        
        self.draw()
    
    def _plot_geometry(self, geometry_obj):
        """Plot geometry boundaries."""
        geo_type = type(geometry_obj).__name__
        bounds = geometry_obj.get_bounds()
        
        if geo_type == 'BoxGeometry':
            self._plot_box(bounds)
        elif geo_type == 'CylinderGeometry':
            self._plot_cylinder(geometry_obj)
        elif geo_type == 'SphereGeometry':
            self._plot_sphere(geometry_obj)
        elif geo_type == 'PlanarGeometry':
            self._plot_planar(bounds)
        elif geo_type == 'MultiLayerGeometry':
            self._plot_multilayer(geometry_obj)
    
    def _plot_box(self, bounds):
        """Plot box geometry."""
        (x_min, x_max), (y_min, y_max), (z_min, z_max) = bounds
        
        # Define the vertices of the box
        vertices = [
            [x_min, y_min, z_min],
            [x_max, y_min, z_min],
            [x_max, y_max, z_min],
            [x_min, y_max, z_min],
            [x_min, y_min, z_max],
            [x_max, y_min, z_max],
            [x_max, y_max, z_max],
            [x_min, y_max, z_max]
        ]
        
        # Define the faces
        faces = [
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # Front
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # Back
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # Left
            [vertices[1], vertices[2], vertices[6], vertices[5]],  # Right
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # Bottom
            [vertices[4], vertices[5], vertices[6], vertices[7]]   # Top
        ]
        
        # Create the 3D polygon collection
        poly = Poly3DCollection(faces, alpha=0.1, facecolor='cyan', edgecolor='blue', linewidth=1.5)
        self.ax.add_collection3d(poly)
    
    def _plot_cylinder(self, geo_obj):
        """Plot cylinder geometry."""
        radius = geo_obj.radius
        z_min = geo_obj.z_min
        z_max = geo_obj.z_max
        center_x = geo_obj.center_x
        center_y = geo_obj.center_y
        
        # Create cylinder surface
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(z_min, z_max, 10)
        Theta, Z = np.meshgrid(theta, z)
        X = radius * np.cos(Theta) + center_x
        Y = radius * np.sin(Theta) + center_y
        
        self.ax.plot_surface(X, Y, Z, alpha=0.1, color='cyan', edgecolor='blue', linewidth=0.5)
        
        # Draw circles at top and bottom
        circle_theta = np.linspace(0, 2*np.pi, 50)
        circle_x = radius * np.cos(circle_theta) + center_x
        circle_y = radius * np.sin(circle_theta) + center_y
        
        self.ax.plot(circle_x, circle_y, z_min, 'b-', linewidth=2)
        self.ax.plot(circle_x, circle_y, z_max, 'b-', linewidth=2)
    
    def _plot_sphere(self, geo_obj):
        """Plot sphere geometry."""
        radius = geo_obj.radius
        center = geo_obj.center
        
        # Create sphere surface
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
        
        self.ax.plot_surface(x, y, z, alpha=0.1, color='cyan', edgecolor='blue', linewidth=0.5)
    
    def _plot_planar(self, bounds):
        """Plot planar geometry (just boundary planes)."""
        (x_min, x_max), (y_min, y_max), (z_min, z_max) = bounds
        
        # Limit xy extent for visualization
        max_extent = 1000
        x_range = min(max_extent, (x_max - x_min) / 2)
        y_range = min(max_extent, (y_max - y_min) / 2)
        
        xx, yy = np.meshgrid(
            [- x_range, x_range],
            [-y_range, y_range]
        )
        
        # Plot z_min plane
        self.ax.plot_surface(xx, yy, np.full_like(xx, z_min), 
                           alpha=0.2, color='cyan', edgecolor='blue')
        
        # Plot z_max plane
        self.ax.plot_surface(xx, yy, np.full_like(xx, z_max),
                           alpha=0.2, color='cyan', edgecolor='blue')
    
    def _plot_multilayer(self, geo_obj):
        """Plot multi-layer geometry."""
        bounds = geo_obj.get_bounds()
        (x_min, x_max), (y_min, y_max), (z_min, z_max) = bounds
        
        # Draw box outline
        self._plot_box(bounds)
        
        # Draw layer boundaries
        layer_z = geo_obj.layer_z
        x_range = min(1000, (x_max - x_min) / 2)
        y_range = min(1000, (y_max - y_min) / 2)
        
        xx, yy = np.meshgrid(
            [max(x_min, -x_range), min(x_max, x_range)],
            [max(y_min, -y_range), min(y_max, y_range)]
        )
        
        for i, z in enumerate(layer_z[1:-1], 1):  # Skip first and last (already drawn)
            self.ax.plot_surface(xx, yy, np.full_like(xx, z),
                               alpha=0.15, color='yellow', edgecolor='orange',
                               linestyle='--')
    
    def _set_axes_equal(self):
        """Set equal aspect ratio for 3D plot."""
        limits = np.array([
            self.ax.get_xlim3d(),
            self.ax.get_ylim3d(),
            self.ax.get_zlim3d(),
        ])
        
        origin = np.mean(limits, axis=1)
        radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))
        
        self.ax.set_xlim3d([origin[0] - radius, origin[0] + radius])
        self.ax.set_ylim3d([origin[1] - radius, origin[1] + radius])
        self.ax.set_zlim3d([origin[2] - radius, origin[2] + radius])


# Make plt available for imports
import matplotlib.pyplot as plt
