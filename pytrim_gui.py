"""PyQt6 GUI for PyTRIM simulation.

This module provides a modern graphical user interface for running
TRIM simulations with real-time visualization and parameter control.
"""
import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QProgressBar,
    QTextEdit, QTabWidget, QGridLayout, QDoubleSpinBox, QSpinBox,
    QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

from pytrim.simulation import (
    TRIMSimulation, SimulationParameters, 
    is_using_cython, is_cython_available, set_use_cython
)
from pytrim import geometry3d


class SimulationThread(QThread):
    """Thread for running simulation without blocking GUI."""
    
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(object)     # results
    error = pyqtSignal(str)           # error message
    
    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        
    def run(self):
        """Run the simulation."""
        try:
            self.simulation.set_progress_callback(self.on_progress)
            results = self.simulation.run(record_trajectories=True, max_trajectories=10)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))
            
    def on_progress(self, current, total):
        """Emit progress signal."""
        self.progress.emit(current, total)
        
    def stop(self):
        """Stop the simulation."""
        self.simulation.stop()


class ParameterWidget(QGroupBox):
    """Widget for entering simulation parameters."""
    
    def __init__(self, parent=None):
        super().__init__("Simulation Parameters", parent)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI."""
        layout = QGridLayout()
        
        # Number of ions
        layout.addWidget(QLabel("Number of Ions:"), 0, 0)
        self.nion_spin = QSpinBox()
        self.nion_spin.setRange(1, 1000000)
        self.nion_spin.setValue(1000)
        self.nion_spin.setSingleStep(100)
        layout.addWidget(self.nion_spin, 0, 1)
        
        # Target geometry
        layout.addWidget(QLabel("Target z_min (Å):"), 1, 0)
        self.zmin_spin = QDoubleSpinBox()
        self.zmin_spin.setRange(-10000, 10000)
        self.zmin_spin.setValue(0.0)
        self.zmin_spin.setDecimals(1)
        layout.addWidget(self.zmin_spin, 1, 1)
        
        layout.addWidget(QLabel("Target z_max (Å):"), 2, 0)
        self.zmax_spin = QDoubleSpinBox()
        self.zmax_spin.setRange(-10000, 10000)
        self.zmax_spin.setValue(4000.0)
        self.zmax_spin.setDecimals(1)
        layout.addWidget(self.zmax_spin, 2, 1)
        
        # Projectile
        layout.addWidget(QLabel("Projectile Z:"), 3, 0)
        self.z1_spin = QSpinBox()
        self.z1_spin.setRange(1, 118)
        self.z1_spin.setValue(5)
        layout.addWidget(self.z1_spin, 3, 1)
        
        layout.addWidget(QLabel("Projectile Mass (amu):"), 4, 0)
        self.m1_spin = QDoubleSpinBox()
        self.m1_spin.setRange(1.0, 300.0)
        self.m1_spin.setValue(11.009)
        self.m1_spin.setDecimals(3)
        layout.addWidget(self.m1_spin, 4, 1)
        
        # Target
        layout.addWidget(QLabel("Target Z:"), 5, 0)
        self.z2_spin = QSpinBox()
        self.z2_spin.setRange(1, 118)
        self.z2_spin.setValue(14)
        layout.addWidget(self.z2_spin, 5, 1)
        
        layout.addWidget(QLabel("Target Mass (amu):"), 6, 0)
        self.m2_spin = QDoubleSpinBox()
        self.m2_spin.setRange(1.0, 300.0)
        self.m2_spin.setValue(28.086)
        self.m2_spin.setDecimals(3)
        layout.addWidget(self.m2_spin, 6, 1)
        
        layout.addWidget(QLabel("Density (atoms/Å³):"), 7, 0)
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(0.001, 1.0)
        self.density_spin.setValue(0.04994)
        self.density_spin.setDecimals(5)
        self.density_spin.setSingleStep(0.001)
        layout.addWidget(self.density_spin, 7, 1)
        
        # Stopping power correction
        layout.addWidget(QLabel("Lindhard Correction:"), 8, 0)
        self.corr_spin = QDoubleSpinBox()
        self.corr_spin.setRange(0.1, 10.0)
        self.corr_spin.setValue(1.5)
        self.corr_spin.setDecimals(2)
        self.corr_spin.setSingleStep(0.1)
        layout.addWidget(self.corr_spin, 8, 1)
        
        # Initial energy
        layout.addWidget(QLabel("Initial Energy (eV):"), 9, 0)
        self.e_init_spin = QDoubleSpinBox()
        self.e_init_spin.setRange(100, 1000000)
        self.e_init_spin.setValue(50000.0)
        self.e_init_spin.setDecimals(0)
        self.e_init_spin.setSingleStep(1000)
        layout.addWidget(self.e_init_spin, 9, 1)
        
        # Initial position
        layout.addWidget(QLabel("Start Position (Å):"), 10, 0)
        pos_layout = QHBoxLayout()
        self.x_init_spin = QDoubleSpinBox()
        self.x_init_spin.setRange(-10000, 10000)
        self.x_init_spin.setValue(0.0)
        self.x_init_spin.setPrefix("x: ")
        pos_layout.addWidget(self.x_init_spin)
        
        self.y_init_spin = QDoubleSpinBox()
        self.y_init_spin.setRange(-10000, 10000)
        self.y_init_spin.setValue(0.0)
        self.y_init_spin.setPrefix("y: ")
        pos_layout.addWidget(self.y_init_spin)
        
        self.z_init_spin = QDoubleSpinBox()
        self.z_init_spin.setRange(-10000, 10000)
        self.z_init_spin.setValue(0.0)
        self.z_init_spin.setPrefix("z: ")
        pos_layout.addWidget(self.z_init_spin)
        layout.addLayout(pos_layout, 10, 1)
        
        # Initial direction
        layout.addWidget(QLabel("Direction (Unit Vector):"), 11, 0)
        dir_layout = QHBoxLayout()
        self.dir_x_spin = QDoubleSpinBox()
        self.dir_x_spin.setRange(-1, 1)
        self.dir_x_spin.setValue(0.0)
        self.dir_x_spin.setDecimals(3)
        self.dir_x_spin.setPrefix("x: ")
        dir_layout.addWidget(self.dir_x_spin)
        
        self.dir_y_spin = QDoubleSpinBox()
        self.dir_y_spin.setRange(-1, 1)
        self.dir_y_spin.setValue(0.0)
        self.dir_y_spin.setDecimals(3)
        self.dir_y_spin.setPrefix("y: ")
        dir_layout.addWidget(self.dir_y_spin)
        
        self.dir_z_spin = QDoubleSpinBox()
        self.dir_z_spin.setRange(-1, 1)
        self.dir_z_spin.setValue(1.0)
        self.dir_z_spin.setDecimals(3)
        self.dir_z_spin.setPrefix("z: ")
        dir_layout.addWidget(self.dir_z_spin)
        layout.addLayout(dir_layout, 11, 1)
        
        self.setLayout(layout)
        
    def get_parameters(self):
        """Get simulation parameters from widgets.
        
        Returns:
            SimulationParameters: Parameters object
        """
        params = SimulationParameters()
        params.nion = self.nion_spin.value()
        params.zmin = self.zmin_spin.value()
        params.zmax = self.zmax_spin.value()
        params.z1 = self.z1_spin.value()
        params.m1 = self.m1_spin.value()
        params.z2 = self.z2_spin.value()
        params.m2 = self.m2_spin.value()
        params.density = self.density_spin.value()
        params.corr_lindhard = self.corr_spin.value()
        params.e_init = self.e_init_spin.value()
        params.x_init = self.x_init_spin.value()
        params.y_init = self.y_init_spin.value()
        params.z_init = self.z_init_spin.value()
        params.dir_x = self.dir_x_spin.value()
        params.dir_y = self.dir_y_spin.value()
        params.dir_z = self.dir_z_spin.value()
        return params
        
    def set_enabled(self, enabled):
        """Enable or disable all parameter widgets."""
        for child in self.findChildren(QSpinBox):
            child.setEnabled(enabled)
        for child in self.findChildren(QDoubleSpinBox):
            child.setEnabled(enabled)


class PlotCanvas(FigureCanvas):
    """Canvas for matplotlib plots (2D)."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
    def clear(self):
        """Clear all axes."""
        self.fig.clear()
        
    def plot_trajectories(self, trajectories, zmin, zmax, projection='xz'):
        """Plot ion trajectories (2D projection).
        
        Parameters:
            trajectories: List of trajectory paths
            zmin, zmax: Target boundaries
            projection: 'xz' for x-z projection or 'yz' for y-z projection
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        for traj in trajectories:
            if traj is not None and len(traj) > 0:
                traj_array = np.array(traj)
                if projection == 'xz':
                    # Plot x-z projection
                    ax.plot(traj_array[:, 2], traj_array[:, 0], alpha=0.6, linewidth=0.8)
                elif projection == 'yz':
                    # Plot y-z projection
                    ax.plot(traj_array[:, 2], traj_array[:, 1], alpha=0.6, linewidth=0.8)
        
        # Draw target boundaries
        ax.axvline(x=zmin, color='r', linestyle='--', label='Target Grenzen')
        ax.axvline(x=zmax, color='r', linestyle='--')
        
        ax.set_xlabel('z (Å)')
        if projection == 'xz':
            ax.set_ylabel('x (Å)')
            ax.set_title('Ion Trajectories (x-z Projection)')
        elif projection == 'yz':
            ax.set_ylabel('y (Å)')
            ax.set_title('Ion Trajectories (y-z Projection)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        self.draw()
    
    def plot_depth_histogram(self, depths, zmin, zmax):
        """Plot histogram of stopping depths.
        
        Parameters:
            depths: List of stopping depths
            zmin, zmax: Target boundaries
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        if len(depths) > 0:
            ax.hist(depths, bins=50, alpha=0.7, edgecolor='black')
            ax.axvline(x=np.mean(depths), color='r', linestyle='--', 
                      label=f'Mean: {np.mean(depths):.1f} Å')
            ax.axvline(x=zmin, color='gray', linestyle=':', alpha=0.5)
            ax.axvline(x=zmax, color='gray', linestyle=':', alpha=0.5)
        
        ax.set_xlabel('Stopping Depth z (Å)')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Stopping Depths')
        ax.legend()
        ax.grid(True, alpha=0.3)
        self.draw()


class PlotCanvas3D(FigureCanvas):
    """Canvas for 3D matplotlib plots."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = None
        
    def clear(self):
        """Clear all axes."""
        self.fig.clear()
        self.ax = None
        
    def plot_trajectories_3d(self, trajectories, geometry_obj=None):
        """Plot 3D trajectories with optional geometry.
        
        Parameters:
            trajectories: List of trajectory paths
            geometry_obj: Geometry object to visualize
        """
        self.clear()
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Plot trajectories
        if trajectories:
            colors = plt.cm.viridis(np.linspace(0, 1, len(trajectories)))
            
            for i, traj in enumerate(trajectories):
                if traj is not None and len(traj) > 0:
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
        
        vertices = [
            [x_min, y_min, z_min], [x_max, y_min, z_min],
            [x_max, y_max, z_min], [x_min, y_max, z_min],
            [x_min, y_min, z_max], [x_max, y_min, z_max],
            [x_max, y_max, z_max], [x_min, y_max, z_max]
        ]
        
        faces = [
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[2], vertices[3], vertices[7], vertices[6]],
            [vertices[0], vertices[3], vertices[7], vertices[4]],
            [vertices[1], vertices[2], vertices[6], vertices[5]],
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]]
        ]
        
        poly = Poly3DCollection(faces, alpha=0.15, facecolor='cyan', 
                               edgecolor='blue', linewidth=1.5)
        self.ax.add_collection3d(poly)
    
    def _plot_cylinder(self, geo_obj):
        """Plot cylinder geometry."""
        radius = geo_obj.radius
        z_min = geo_obj.z_min
        z_max = geo_obj.z_max
        center_x = geo_obj.center_x
        center_y = geo_obj.center_y
        
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(z_min, z_max, 10)
        Theta, Z = np.meshgrid(theta, z)
        X = radius * np.cos(Theta) + center_x
        Y = radius * np.sin(Theta) + center_y
        
        self.ax.plot_surface(X, Y, Z, alpha=0.15, color='cyan', 
                           edgecolor='blue', linewidth=0.5)
    
    def _plot_sphere(self, geo_obj):
        """Plot sphere geometry."""
        radius = geo_obj.radius
        center = np.asarray(geo_obj.center)
        
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = radius * np.outer(np.cos(u), np.sin(v)) + center[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + center[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
        
        self.ax.plot_surface(x, y, z, alpha=0.15, color='cyan', 
                           edgecolor='blue', linewidth=0.5)
    
    def _plot_planar(self, bounds):
        """Plot planar geometry."""
        (x_min, x_max), (y_min, y_max), (z_min, z_max) = bounds
        
        max_extent = 1000
        x_range = min(max_extent, (x_max - x_min) / 2) if x_max != np.inf else max_extent
        y_range = min(max_extent, (y_max - y_min) / 2) if y_max != np.inf else max_extent
        
        xx, yy = np.meshgrid([-x_range, x_range], [-y_range, y_range])
        
        self.ax.plot_surface(xx, yy, np.full_like(xx, z_min), 
                           alpha=0.2, color='cyan', edgecolor='blue')
        self.ax.plot_surface(xx, yy, np.full_like(xx, z_max),
                           alpha=0.2, color='cyan', edgecolor='blue')
    
    def _plot_multilayer(self, geo_obj):
        """Plot multi-layer geometry."""
        bounds = geo_obj.get_bounds()
        self._plot_box(bounds)
    
    def _set_axes_equal(self):
        """Set equal aspect ratio for 3D plot."""
        if self.ax is None:
            return
            
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
        
    def plot_depth_histogram(self, depths, zmin, zmax):
        """Plot histogram of stopping depths.
        
        Parameters:
            depths: List of stopping depths
            zmin, zmax: Target boundaries
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        if len(depths) > 0:
            ax.hist(depths, bins=50, alpha=0.7, edgecolor='black')
            ax.axvline(x=np.mean(depths), color='r', linestyle='--', 
                      label=f'Mean: {np.mean(depths):.1f} Å')
            ax.axvline(x=zmin, color='g', linestyle=':', linewidth=2)
            ax.axvline(x=zmax, color='g', linestyle=':', linewidth=2)
        
        ax.set_xlabel('Stopping Depth z (Å)')
        ax.set_ylabel('Number of Ions')
        ax.set_title('Distribution of Stopping Depths')
        ax.legend()
        ax.grid(True, alpha=0.3)
        self.draw()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.simulation = None
        self.sim_thread = None
        self.results = None
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle('PyTRIM - Ion Transport Simulation')
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel for parameters and controls
        left_panel = QVBoxLayout()
        
        # Parameter widget
        self.param_widget = ParameterWidget()
        left_panel.addWidget(self.param_widget)
        
        # Control buttons
        control_group = QGroupBox("Control")
        control_layout = QVBoxLayout()
        
        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self.start_simulation)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        control_layout.addWidget(self.export_button)
        
        control_group.setLayout(control_layout)
        left_panel.addWidget(control_group)
        
        # Progress bar
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        progress_group.setLayout(progress_layout)
        left_panel.addWidget(progress_group)
        
        # Performance info
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout()
        
        # Status label
        self.perf_label = QLabel()
        self.perf_label.setWordWrap(True)
        perf_layout.addWidget(self.perf_label)
        
        # Toggle checkbox (only if Cython is available)
        if is_cython_available():
            self.cython_toggle = QCheckBox("Use Cython")
            self.cython_toggle.setChecked(is_using_cython())
            self.cython_toggle.stateChanged.connect(self.toggle_cython)
            self.cython_toggle.setToolTip(
                "Enable/Disable Cython-optimized modules.\n"
                "Cython: ~6.4x faster simulation\n"
                "Python: Slower, but helpful for debugging"
            )
            perf_layout.addWidget(self.cython_toggle)
        else:
            self.cython_toggle = None
            # Show hint to build Cython
            hint_label = QLabel(
                "<small><i>Cython not available.<br>"
                "Run './build_cython.sh'<br>"
                "for 6.4x speedup!</i></small>"
            )
            hint_label.setWordWrap(True)
            perf_layout.addWidget(hint_label)
        
        # Update performance label
        self.update_performance_label()
        
        perf_group.setLayout(perf_layout)
        left_panel.addWidget(perf_group)
        
        left_panel.addStretch()
        main_layout.addLayout(left_panel, 1)
        
        # Right panel for visualization
        right_panel = QVBoxLayout()
        
        # Tab widget for different plots
        self.tab_widget = QTabWidget()
        
        # 3D Trajectory plot tab
        traj3d_widget = QWidget()
        traj3d_layout = QVBoxLayout()
        self.traj3d_canvas = PlotCanvas3D(self, width=8, height=6)
        self.traj3d_toolbar = NavigationToolbar(self.traj3d_canvas, self)
        traj3d_layout.addWidget(self.traj3d_toolbar)
        traj3d_layout.addWidget(self.traj3d_canvas)
        traj3d_widget.setLayout(traj3d_layout)
        self.tab_widget.addTab(traj3d_widget, "3D Trajectories")
        
        # 2D Trajectory plot tab (x-z projection)
        traj2d_xz_widget = QWidget()
        traj2d_xz_layout = QVBoxLayout()
        self.traj2d_xz_canvas = PlotCanvas(self, width=8, height=6)
        self.traj2d_xz_toolbar = NavigationToolbar(self.traj2d_xz_canvas, self)
        traj2d_xz_layout.addWidget(self.traj2d_xz_toolbar)
        traj2d_xz_layout.addWidget(self.traj2d_xz_canvas)
        traj2d_xz_widget.setLayout(traj2d_xz_layout)
        self.tab_widget.addTab(traj2d_xz_widget, "2D Trajectories (x-z)")
        
        # 2D Trajectory plot tab (y-z projection)
        traj2d_yz_widget = QWidget()
        traj2d_yz_layout = QVBoxLayout()
        self.traj2d_yz_canvas = PlotCanvas(self, width=8, height=6)
        self.traj2d_yz_toolbar = NavigationToolbar(self.traj2d_yz_canvas, self)
        traj2d_yz_layout.addWidget(self.traj2d_yz_toolbar)
        traj2d_yz_layout.addWidget(self.traj2d_yz_canvas)
        traj2d_yz_widget.setLayout(traj2d_yz_layout)
        self.tab_widget.addTab(traj2d_yz_widget, "2D Trajectories (y-z)")
        
        # Depth histogram tab
        hist_widget = QWidget()
        hist_layout = QVBoxLayout()
        self.hist_canvas = PlotCanvas(self, width=8, height=6)
        self.hist_toolbar = NavigationToolbar(self.hist_canvas, self)
        hist_layout.addWidget(self.hist_toolbar)
        hist_layout.addWidget(self.hist_canvas)
        hist_widget.setLayout(hist_layout)
        self.tab_widget.addTab(hist_widget, "Stopping Depth Distribution")
        
        # Results tab
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        font = QFont("Courier")
        font.setPointSize(10)
        self.results_text.setFont(font)
        results_layout.addWidget(self.results_text)
        results_widget.setLayout(results_layout)
        self.tab_widget.addTab(results_widget, "Results")
        
        right_panel.addWidget(self.tab_widget)
        main_layout.addLayout(right_panel, 2)
        
    def update_performance_label(self):
        """Update the performance status label."""
        using_cython = is_using_cython()
        if using_cython:
            perf_icon = "⚡"
            perf_text = "Cython aktiviert"
            perf_detail = "~6.4x schneller"
            perf_color = "#2ecc71"  # Green
        else:
            perf_icon = "🐍"
            perf_text = "Python Mode"
            if is_cython_available():
                perf_detail = "Cython available, but disabled"
            else:
                perf_detail = "For more speed: ./build_cython.sh"
            perf_color = "#f39c12"  # Orange
        
        self.perf_label.setText(
            f"{perf_icon} <b>{perf_text}</b><br><small>{perf_detail}</small>"
        )
        self.perf_label.setStyleSheet(f"color: {perf_color}; padding: 5px;")
    
    def toggle_cython(self, state):
        """Toggle between Cython and Python modes."""
        use_cython = (state == Qt.CheckState.Checked.value)
        
        # Show warning about reload
        if hasattr(self, 'results') and self.results is not None:
            reply = QMessageBox.question(
                self,
                "Reload modules?",
                "Switching between Cython and Python requires reloading "
                "the simulation modules. Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                # Revert checkbox
                self.cython_toggle.blockSignals(True)
                self.cython_toggle.setChecked(not use_cython)
                self.cython_toggle.blockSignals(False)
                return
        
        # Try to switch
        success = set_use_cython(use_cython)
        
        if success:
            self.update_performance_label()
            mode = "Cython" if use_cython else "Python"
            QMessageBox.information(
                self,
                "Mode Switched",
                f"Successfully switched to {mode} mode!\n\n"
                f"New simulations will use {mode} modules."
            )
        else:
            # Failed to switch (probably Cython not available)
            self.cython_toggle.blockSignals(True)
            self.cython_toggle.setChecked(False)
            self.cython_toggle.blockSignals(False)
            self.update_performance_label()
            QMessageBox.warning(
                self,
                "Switch Failed",
                "Could not load Cython modules.\n"
                "Run './build_cython.sh' to compile them."
            )
        
    def start_simulation(self):
        """Start the simulation."""
        # Get parameters
        params = self.param_widget.get_parameters()
        
        # Validate direction vector
        dir_vec = np.array([params.dir_x, params.dir_y, params.dir_z])
        norm = np.linalg.norm(dir_vec)
        if norm == 0:
            QMessageBox.warning(self, "Error", "Direction vector cannot be zero!")
            return
        # Normalize
        params.dir_x /= norm
        params.dir_y /= norm
        params.dir_z /= norm
        
        # Create simulation
        self.simulation = TRIMSimulation(params)
        
        # Create and start thread
        self.sim_thread = SimulationThread(self.simulation)
        self.sim_thread.progress.connect(self.update_progress)
        self.sim_thread.finished.connect(self.simulation_finished)
        self.sim_thread.error.connect(self.simulation_error)
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.param_widget.set_enabled(False)
        self.export_button.setEnabled(False)
        self.cython_toggle.setEnabled(False)  # Disable during simulation
        self.progress_bar.setValue(0)
        self.progress_label.setText("Simulation running...")
        self.results_text.clear()
        
        # Start simulation
        self.sim_thread.start()
        
    def stop_simulation(self):
        """Stop the running simulation."""
        if self.sim_thread is not None:
            self.sim_thread.stop()
            self.progress_label.setText("Stopping simulation...")
            
    def update_progress(self, current, total):
        """Update progress bar.
        
        Parameters:
            current: Current ion number
            total: Total number of ions
        """
        progress = int(100 * current / total)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Ion {current} / {total}")
        
    def simulation_finished(self, results):
        """Handle simulation completion.
        
        Parameters:
            results: SimulationResults object
        """
        self.results = results
        
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.param_widget.set_enabled(True)
        self.export_button.setEnabled(True)
        self.cython_toggle.setEnabled(True)  # Re-enable after simulation
        self.progress_bar.setValue(100)
        self.progress_label.setText("Simulation completed!")
        
        # Display results with performance info
        result_text = results.get_summary()
        result_text += "\n" + "=" * 50 + "\n"
        result_text += f"Performance Mode: {'Cython (optimized)' if is_using_cython() else 'Python (fallback)'}\n"
        if results.simulation_time > 0 and results.total_ions > 0:
            ions_per_sec = results.total_ions / results.simulation_time
            result_text += f"Durchsatz: {ions_per_sec:.1f} Ionen/Sekunde\n"
        self.results_text.setText(result_text)
        
        # Plot results
        params = self.param_widget.get_parameters()
        
        # Get geometry object for 3D visualization
        geometry_obj = None
        if hasattr(self.simulation, 'geometry_obj'):
            geometry_obj = self.simulation.geometry_obj
        
        # Plot 3D trajectories with geometry
        self.traj3d_canvas.plot_trajectories_3d(results.trajectories, geometry_obj)
        
        # Plot 2D trajectories (x-z projection)
        self.traj2d_xz_canvas.plot_trajectories(results.trajectories, params.zmin, params.zmax, projection='xz')
        
        # Plot 2D trajectories (y-z projection)
        self.traj2d_yz_canvas.plot_trajectories(results.trajectories, params.zmin, params.zmax, projection='yz')
        
        # Plot depth histogram
        self.hist_canvas.plot_depth_histogram(results.stopped_depths, params.zmin, params.zmax)
        
    def simulation_error(self, error_msg):
        """Handle simulation error.
        
        Parameters:
            error_msg: Error message string
        """
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.param_widget.set_enabled(True)
        self.cython_toggle.setEnabled(True)  # Re-enable after error
        self.progress_label.setText("Error!")
        
        QMessageBox.critical(self, "Simulation Error", 
                           f"Error during simulation:\n{error_msg}")
        
    def export_results(self):
        """Export simulation results to file."""
        if self.results is None:
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("PyTRIM Simulation Results\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.results.get_summary())
                    f.write("\n\n" + "=" * 50 + "\n")
                    f.write("Stopping Depths (Å):\n")
                    for depth in self.results.stopped_depths:
                        f.write(f"{depth:.2f}\n")
                QMessageBox.information(self, "Export Successful", 
                                      f"Results saved to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", 
                                   f"Error during save:\n{str(e)}")


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
