"""Extended PyQt6 GUI for PyTRIM simulation with advanced features.

This enhanced version includes:
- Geometry type selection with dynamic parameters
- Material presets
- Advanced visualizations (heatmaps, energy loss, etc.)
- Multiple export formats (CSV, JSON, VTK, PNG)
"""
import sys
import os
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QProgressBar,
    QTextEdit, QTabWidget, QGridLayout, QDoubleSpinBox, QSpinBox,
    QFileDialog, QMessageBox, QCheckBox, QComboBox, QDialog,
    QDialogButtonBox, QListWidget, QSplitter
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Import all GUI modules
from pytrim_gui import (
    SimulationThread, PlotCanvas, PlotCanvas3D
)
from pytrim.simulation import (
    TRIMSimulation, SimulationParameters,
    is_using_cython, is_cython_available, set_use_cython,
    is_using_parallel, is_parallel_available, set_use_parallel
)
from pytrim import geometry3d
from pytrim.presets import get_preset_manager, MaterialPreset
from pytrim import export
from pytrim.visualizations import (
    HeatmapCanvas, EnergyLossCanvas, RadialDistributionCanvas
)


# Geometry parameter widgets that change based on geometry type
class GeometryParameterWidget(QGroupBox):
    """Dynamic widget for geometry-specific parameters."""
    
    def __init__(self, parent=None):
        super().__init__("Geometry Parameters", parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.param_widgets = {}
        self.current_geometry = None
        
    def set_geometry_type(self, geometry_type):
        """Update displayed parameters for geometry type."""
        # Clear existing widgets
        for widget in self.param_widgets.values():
            widget.setParent(None)
        self.param_widgets.clear()
        
        # Clear layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        self.current_geometry = geometry_type
        row = 0
        
        if geometry_type == "planar":
            self.layout.addWidget(QLabel("(No additional parameters)"), 0, 0, 1, 2)
            
        elif geometry_type == "box":
            # x_min, x_max, y_min, y_max
            self.layout.addWidget(QLabel("x_min (Å):"), row, 0)
            self.param_widgets['x_min'] = QDoubleSpinBox()
            self.param_widgets['x_min'].setRange(-100000, 100000)
            self.param_widgets['x_min'].setValue(-500.0)
            self.layout.addWidget(self.param_widgets['x_min'], row, 1)
            row += 1
            
            self.layout.addWidget(QLabel("x_max (Å):"), row, 0)
            self.param_widgets['x_max'] = QDoubleSpinBox()
            self.param_widgets['x_max'].setRange(-100000, 100000)
            self.param_widgets['x_max'].setValue(500.0)
            self.layout.addWidget(self.param_widgets['x_max'], row, 1)
            row += 1
            
            self.layout.addWidget(QLabel("y_min (Å):"), row, 0)
            self.param_widgets['y_min'] = QDoubleSpinBox()
            self.param_widgets['y_min'].setRange(-100000, 100000)
            self.param_widgets['y_min'].setValue(-500.0)
            self.layout.addWidget(self.param_widgets['y_min'], row, 1)
            row += 1
            
            self.layout.addWidget(QLabel("y_max (Å):"), row, 0)
            self.param_widgets['y_max'] = QDoubleSpinBox()
            self.param_widgets['y_max'].setRange(-100000, 100000)
            self.param_widgets['y_max'].setValue(500.0)
            self.layout.addWidget(self.param_widgets['y_max'], row, 1)
            
        elif geometry_type == "cylinder":
            self.layout.addWidget(QLabel("Radius (Å):"), row, 0)
            self.param_widgets['radius'] = QDoubleSpinBox()
            self.param_widgets['radius'].setRange(1.0, 100000.0)
            self.param_widgets['radius'].setValue(500.0)
            self.layout.addWidget(self.param_widgets['radius'], row, 1)
            row += 1
            
            self.layout.addWidget(QLabel("Axis:"), row, 0)
            self.param_widgets['axis'] = QComboBox()
            self.param_widgets['axis'].addItems(['z', 'x', 'y'])
            self.layout.addWidget(self.param_widgets['axis'], row, 1)
            
        elif geometry_type == "sphere":
            self.layout.addWidget(QLabel("Radius (Å):"), row, 0)
            self.param_widgets['radius'] = QDoubleSpinBox()
            self.param_widgets['radius'].setRange(1.0, 100000.0)
            self.param_widgets['radius'].setValue(500.0)
            self.layout.addWidget(self.param_widgets['radius'], row, 1)
            row += 1
            
            self.layout.addWidget(QLabel("Center x (Å):"), row, 0)
            self.param_widgets['center_x'] = QDoubleSpinBox()
            self.param_widgets['center_x'].setRange(-100000, 100000)
            self.param_widgets['center_x'].setValue(0.0)
            self.layout.addWidget(self.param_widgets['center_x'], row, 1)
            row += 1
            
            self.layout.addWidget(QLabel("Center y (Å):"), row, 0)
            self.param_widgets['center_y'] = QDoubleSpinBox()
            self.param_widgets['center_y'].setRange(-100000, 100000)
            self.param_widgets['center_y'].setValue(0.0)
            self.layout.addWidget(self.param_widgets['center_y'], row, 1)
            row += 1
            
            self.layout.addWidget(QLabel("Center z (Å):"), row, 0)
            self.param_widgets['center_z'] = QDoubleSpinBox()
            self.param_widgets['center_z'].setRange(-100000, 100000)
            self.param_widgets['center_z'].setValue(2000.0)
            self.layout.addWidget(self.param_widgets['center_z'], row, 1)
            
        elif geometry_type == "multilayer":
            self.layout.addWidget(QLabel("Layer Thicknesses (Å):"), row, 0)
            self.param_widgets['layer_thicknesses'] = QLineEdit()
            self.param_widgets['layer_thicknesses'].setText("1000, 500, 2500")
            self.param_widgets['layer_thicknesses'].setPlaceholderText("z.B.: 1000, 500, 2500")
            self.layout.addWidget(self.param_widgets['layer_thicknesses'], row, 1)
    
    def get_geometry_params(self):
        """Get current geometry parameters as dictionary.
        
        Note: zmin and zmax are handled separately by the main form,
        so they are added to the params where needed for the constructors.
        """
        if self.current_geometry == "planar":
            return {}
        elif self.current_geometry == "box":
            # BoxGeometry needs: x_min, x_max, y_min, y_max, z_min, z_max
            # Note: z_min and z_max will be added from params.zmin/zmax in simulation.py
            return {
                'x_min': self.param_widgets['x_min'].value(),
                'x_max': self.param_widgets['x_max'].value(),
                'y_min': self.param_widgets['y_min'].value(),
                'y_max': self.param_widgets['y_max'].value(),
                'needs_z_bounds': True  # Signal that z_min/z_max are needed
            }
        elif self.current_geometry == "cylinder":
            # CylinderGeometry needs: radius, z_min, z_max, center_x=0.0, center_y=0.0
            # Axis selection is ignored for now (always z-axis)
            return {
                'radius': self.param_widgets['radius'].value(),
                'needs_z_bounds': True  # Signal that z_min/z_max are needed
            }
        elif self.current_geometry == "sphere":
            # SphereGeometry needs: radius, center_x=0.0, center_y=0.0, center_z=0.0
            return {
                'radius': self.param_widgets['radius'].value(),
                'center_x': self.param_widgets['center_x'].value(),
                'center_y': self.param_widgets['center_y'].value(),
                'center_z': self.param_widgets['center_z'].value(),
            }
        elif self.current_geometry == "multilayer":
            # MultiLayerGeometry needs: layer_z_positions (list of z boundaries)
            # Convert thicknesses to z positions
            thick_str = self.param_widgets['layer_thicknesses'].text()
            thicknesses = [float(x.strip()) for x in thick_str.split(',')]
            # Calculate z positions from thicknesses
            z_positions = [0.0]
            for thickness in thicknesses:
                z_positions.append(z_positions[-1] + thickness)
            return {'layer_z_positions': z_positions}
        return {}


class PresetDialog(QDialog):
    """Dialog for selecting material presets."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Material Preset")
        self.preset_manager = get_preset_manager()
        self.selected_preset = None
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Preset list
        self.preset_list = QListWidget()
        for name in self.preset_manager.get_preset_names():
            preset = self.preset_manager.get_preset(name)
            item_text = f"{name} - {preset.description}"
            self.preset_list.addItem(item_text)
        self.preset_list.currentRowChanged.connect(self.on_selection_changed)
        self.preset_list.doubleClicked.connect(self.accept)
        layout.addWidget(QLabel("Available Presets:"))
        layout.addWidget(self.preset_list)
        
        # Info display
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        layout.addWidget(QLabel("Details:"))
        layout.addWidget(self.info_text)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.resize(500, 400)
        
        # Select first preset
        if self.preset_list.count() > 0:
            self.preset_list.setCurrentRow(0)
    
    def on_selection_changed(self, index):
        """Update info when selection changes."""
        if index < 0:
            return
        
        preset_names = self.preset_manager.get_preset_names()
        preset_name = preset_names[index]
        preset = self.preset_manager.get_preset(preset_name)
        
        info = f"<b>{preset.name}</b><br>"
        info += f"{preset.description}<br><br>"
        info += f"<b>Projectile:</b> {preset.element1} (Z={preset.z1}, M={preset.m1} amu)<br>"
        info += f"<b>Target:</b> {preset.element2} (Z={preset.z2}, M={preset.m2} amu)<br>"
        info += f"<b>Density:</b> {preset.density:.5f} atoms/Å³<br>"
        info += f"<b>Energy:</b> {preset.energy:.0f} eV<br>"
        info += f"<b>Geometry:</b> {preset.geometry_type}<br>"
        
        self.info_text.setHtml(info)
        self.selected_preset = preset
    
    def get_selected_preset(self):
        """Return selected preset or None."""
        return self.selected_preset


class ExtendedParameterWidget(QGroupBox):
    """Extended parameter widget with geometry and preset support."""
    
    def __init__(self, parent=None):
        super().__init__("Simulation Parameters", parent)
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Preset selector
        preset_layout = QHBoxLayout()
        preset_button = QPushButton("Load Preset...")
        preset_button.clicked.connect(self.load_preset)
        preset_layout.addWidget(preset_button)
        preset_layout.addStretch()
        layout.addLayout(preset_layout)
        
        # Tab widget for organized parameters
        tabs = QTabWidget()
        
        # === Basic Parameters Tab ===
        basic_widget = QWidget()
        basic_layout = QGridLayout()
        row = 0
        
        # Number of ions
        basic_layout.addWidget(QLabel("Number of Ions:"), row, 0)
        self.nion_spin = QSpinBox()
        self.nion_spin.setRange(1, 1000000)
        self.nion_spin.setValue(1000)
        self.nion_spin.setSingleStep(100)
        basic_layout.addWidget(self.nion_spin, row, 1)
        row += 1
        
        # Projectile
        basic_layout.addWidget(QLabel("Projectile Z:"), row, 0)
        self.z1_spin = QSpinBox()
        self.z1_spin.setRange(1, 118)
        self.z1_spin.setValue(5)
        basic_layout.addWidget(self.z1_spin, row, 1)
        row += 1
        
        basic_layout.addWidget(QLabel("Projectile Mass (amu):"), row, 0)
        self.m1_spin = QDoubleSpinBox()
        self.m1_spin.setRange(1.0, 300.0)
        self.m1_spin.setValue(11.009)
        self.m1_spin.setDecimals(3)
        basic_layout.addWidget(self.m1_spin, row, 1)
        row += 1
        
        # Target
        basic_layout.addWidget(QLabel("Target Z:"), row, 0)
        self.z2_spin = QSpinBox()
        self.z2_spin.setRange(1, 118)
        self.z2_spin.setValue(14)
        basic_layout.addWidget(self.z2_spin, row, 1)
        row += 1
        
        basic_layout.addWidget(QLabel("Target Mass (amu):"), row, 0)
        self.m2_spin = QDoubleSpinBox()
        self.m2_spin.setRange(1.0, 300.0)
        self.m2_spin.setValue(28.086)
        self.m2_spin.setDecimals(3)
        basic_layout.addWidget(self.m2_spin, row, 1)
        row += 1
        
        basic_layout.addWidget(QLabel("Density (atoms/Å³):"), row, 0)
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(0.001, 1.0)
        self.density_spin.setValue(0.04994)
        self.density_spin.setDecimals(5)
        self.density_spin.setSingleStep(0.001)
        basic_layout.addWidget(self.density_spin, row, 1)
        row += 1
        
        basic_layout.addWidget(QLabel("Lindhard Correction:"), row, 0)
        self.corr_spin = QDoubleSpinBox()
        self.corr_spin.setRange(0.1, 10.0)
        self.corr_spin.setValue(1.5)
        self.corr_spin.setDecimals(2)
        self.corr_spin.setSingleStep(0.1)
        basic_layout.addWidget(self.corr_spin, row, 1)
        row += 1
        
        basic_layout.addWidget(QLabel("Initial Energy (eV):"), row, 0)
        self.e_init_spin = QDoubleSpinBox()
        self.e_init_spin.setRange(100, 1000000)
        self.e_init_spin.setValue(50000.0)
        self.e_init_spin.setDecimals(0)
        self.e_init_spin.setSingleStep(1000)
        basic_layout.addWidget(self.e_init_spin, row, 1)
        
        basic_layout.setRowStretch(row + 1, 1)
        basic_widget.setLayout(basic_layout)
        tabs.addTab(basic_widget, "Basic Parameters")
        
        # === Geometry Tab ===
        geom_widget = QWidget()
        geom_layout = QVBoxLayout()
        
        # Geometry type selector
        geom_type_layout = QHBoxLayout()
        geom_type_layout.addWidget(QLabel("Geometry Type:"))
        self.geometry_combo = QComboBox()
        self.geometry_combo.addItems(["planar", "box", "cylinder", "sphere", "multilayer"])
        self.geometry_combo.currentTextChanged.connect(self.on_geometry_changed)
        geom_type_layout.addWidget(self.geometry_combo)
        geom_layout.addLayout(geom_type_layout)
        
        # Target boundaries
        bounds_layout = QGridLayout()
        bounds_layout.addWidget(QLabel("Target z_min (Å):"), 0, 0)
        self.zmin_spin = QDoubleSpinBox()
        self.zmin_spin.setRange(-10000, 10000)
        self.zmin_spin.setValue(0.0)
        self.zmin_spin.setDecimals(1)
        bounds_layout.addWidget(self.zmin_spin, 0, 1)
        
        bounds_layout.addWidget(QLabel("Target z_max (Å):"), 1, 0)
        self.zmax_spin = QDoubleSpinBox()
        self.zmax_spin.setRange(-10000, 10000)
        self.zmax_spin.setValue(4000.0)
        self.zmax_spin.setDecimals(1)
        bounds_layout.addWidget(self.zmax_spin, 1, 1)
        geom_layout.addLayout(bounds_layout)
        
        # Dynamic geometry parameters
        self.geometry_params_widget = GeometryParameterWidget()
        geom_layout.addWidget(self.geometry_params_widget)
        
        geom_layout.addStretch()
        geom_widget.setLayout(geom_layout)
        tabs.addTab(geom_widget, "Geometry")
        
        # === Beam Parameters Tab ===
        beam_widget = QWidget()
        beam_layout = QGridLayout()
        row = 0
        
        # Initial position
        beam_layout.addWidget(QLabel("Start Position (Å):"), row, 0)
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
        beam_layout.addLayout(pos_layout, row, 1)
        row += 1
        
        # Initial direction
        beam_layout.addWidget(QLabel("Direction:"), row, 0)
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
        beam_layout.addLayout(dir_layout, row, 1)
        
        beam_layout.setRowStretch(row + 1, 1)
        beam_widget.setLayout(beam_layout)
        tabs.addTab(beam_widget, "Beam")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Initialize geometry widget
        self.on_geometry_changed("planar")
    
    def on_geometry_changed(self, geometry_type):
        """Update geometry parameters when type changes."""
        self.geometry_params_widget.set_geometry_type(geometry_type)
    
    def load_preset(self):
        """Load a material preset."""
        dialog = PresetDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            preset = dialog.get_selected_preset()
            if preset:
                self.apply_preset(preset)
    
    def apply_preset(self, preset: MaterialPreset):
        """Apply preset to parameters."""
        # Basic parameters
        self.z1_spin.setValue(preset.z1)
        self.m1_spin.setValue(preset.m1)
        self.z2_spin.setValue(preset.z2)
        self.m2_spin.setValue(preset.m2)
        self.density_spin.setValue(preset.density)
        self.corr_spin.setValue(preset.corr_lindhard)
        self.e_init_spin.setValue(preset.energy)
        
        # Geometry
        self.zmin_spin.setValue(preset.zmin)
        self.zmax_spin.setValue(preset.zmax)
        self.geometry_combo.setCurrentText(preset.geometry_type)
        
        QMessageBox.information(
            self, "Preset geladen",
            f"Preset '{preset.name}' wurde geladen:\n{preset.description}"
        )
    
    def get_parameters(self):
        """Get simulation parameters."""
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
        
        # Geometry
        params.geometry_type = self.geometry_combo.currentText()
        params.geometry_params = self.geometry_params_widget.get_geometry_params()
        
        return params
    
    def set_enabled(self, enabled):
        """Enable or disable all parameter widgets."""
        for child in self.findChildren((QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QPushButton)):
            child.setEnabled(enabled)


class ExportDialog(QDialog):
    """Dialog for selecting export format and options."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Results")
        self.format = None
        self.filepath = None
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        
        # Format selection
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "CSV (Data Table)",
            "JSON (Structured Data)",
            "VTK (ParaView/3D)",
            "PNG (High-Resolution Plots)",
            "All Formats"
        ])
        format_layout.addWidget(self.format_combo)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.include_trajectories = QCheckBox("Include trajectories")
        self.include_trajectories.setChecked(True)
        options_layout.addWidget(self.include_trajectories)
        
        self.high_dpi = QCheckBox("High Resolution (300 DPI)")
        self.high_dpi.setChecked(True)
        options_layout.addWidget(self.high_dpi)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_options(self):
        """Get selected options."""
        return {
            'format': self.format_combo.currentText(),
            'include_trajectories': self.include_trajectories.isChecked(),
            'dpi': 300 if self.high_dpi.isChecked() else 150
        }


class ExtendedMainWindow(QMainWindow):
    """Extended main window with all advanced features."""
    
    def __init__(self):
        super().__init__()
        self.simulation = None
        self.sim_thread = None
        self.results = None
        self._init_ui()
        
    def _init_ui(self):
        """Initialize UI."""
        self.setWindowTitle('CyTRIM - Advanced Ion Transport Simulation')
        self.setGeometry(50, 50, 1600, 1000)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # === LEFT PANEL ===
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # Extended parameter widget
        self.param_widget = ExtendedParameterWidget()
        left_layout.addWidget(self.param_widget)
        
        # Controls
        control_group = QGroupBox("Control")
        control_layout = QVBoxLayout()
        
        self.start_button = QPushButton("🚀 Start Simulation")
        self.start_button.clicked.connect(self.start_simulation)
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        self.export_button = QPushButton("💾 Export...")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        control_layout.addWidget(self.export_button)
        
        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("Ready")
        progress_layout.addWidget(self.progress_label)
        progress_group.setLayout(progress_layout)
        left_layout.addWidget(progress_group)
        
        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout()
        self.perf_label = QLabel()
        self.perf_label.setWordWrap(True)
        perf_layout.addWidget(self.perf_label)
        
        if is_cython_available():
            self.cython_toggle = QCheckBox("⚡ Use Cython")
            self.cython_toggle.setChecked(is_using_cython())
            self.cython_toggle.stateChanged.connect(self.toggle_cython)
            perf_layout.addWidget(self.cython_toggle)
        else:
            self.cython_toggle = None
        
        if is_parallel_available():
            self.parallel_toggle = QCheckBox("⚡⚡ Use OpenMP Parallel")
            self.parallel_toggle.setChecked(is_using_parallel())
            self.parallel_toggle.stateChanged.connect(self.toggle_parallel)
            # Parallel requires Cython to be enabled
            if not is_using_cython():
                self.parallel_toggle.setEnabled(False)
                self.parallel_toggle.setToolTip("Requires Cython to be enabled first")
            perf_layout.addWidget(self.parallel_toggle)
        else:
            self.parallel_toggle = None
        
        self.update_performance_label()
        perf_group.setLayout(perf_layout)
        left_layout.addWidget(perf_group)
        
        left_layout.addStretch()
        
        # === RIGHT PANEL ===
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # Tab widget for visualizations
        self.tab_widget = QTabWidget()
        
        # 3D trajectories
        self._add_plot_tab("3D Trajectories", PlotCanvas3D, 'traj3d_canvas')
        
        # 2D projections
        self._add_plot_tab("2D (x-z)", PlotCanvas, 'traj2d_xz_canvas')
        self._add_plot_tab("2D (y-z)", PlotCanvas, 'traj2d_yz_canvas')
        
        # Heatmaps
        self._add_plot_tab("Heatmap (x-z)", HeatmapCanvas, 'heatmap_xz_canvas')
        self._add_plot_tab("Heatmap (y-z)", HeatmapCanvas, 'heatmap_yz_canvas')
        self._add_plot_tab("Heatmap (x-y)", HeatmapCanvas, 'heatmap_xy_canvas')
        
        # Energy loss
        self._add_plot_tab("Energie-Verlust", EnergyLossCanvas, 'energy_canvas')
        
        # Radial distribution
        self._add_plot_tab("Radial Distribution", RadialDistributionCanvas, 'radial_canvas')
        
        # Histogram
        self._add_plot_tab("Stopping Depth Distribution", PlotCanvas, 'hist_canvas')
        
        # Results text
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 10))
        results_layout.addWidget(self.results_text)
        results_widget.setLayout(results_layout)
        self.tab_widget.addTab(results_widget, "📊 Results")
        
        right_layout.addWidget(self.tab_widget)
        
        # Add panels to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
    
    def _add_plot_tab(self, title, canvas_class, attr_name):
        """Helper to add plot tab with toolbar."""
        widget = QWidget()
        layout = QVBoxLayout()
        canvas = canvas_class(self, width=8, height=6)
        setattr(self, attr_name, canvas)
        toolbar = NavigationToolbar(canvas, self)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        self.tab_widget.addTab(widget, title)
    
    def update_performance_label(self):
        """Update the performance status label."""
        using_cython = is_using_cython()
        using_parallel = is_using_parallel()
        
        if using_cython:
            if using_parallel:
                perf_icon = "⚡⚡"
                perf_text = "Cython + OpenMP"
                perf_detail = "~20-30x faster (multi-core)"
                perf_color = "#27ae60"  # Dark green
            else:
                perf_icon = "⚡"
                perf_text = "Cython enabled"
                perf_detail = "~6.4x faster"
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
            
            # Disable parallel if switching to Python
            if not use_cython and self.parallel_toggle is not None:
                self.parallel_toggle.blockSignals(True)
                self.parallel_toggle.setChecked(False)
                self.parallel_toggle.setEnabled(False)
                self.parallel_toggle.blockSignals(False)
                set_use_parallel(False)
            elif use_cython and self.parallel_toggle is not None:
                self.parallel_toggle.setEnabled(True)
            
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
    
    def toggle_parallel(self, state):
        """Toggle OpenMP parallelization."""
        use_parallel = (state == Qt.CheckState.Checked.value)
        
        # Can only use parallel with Cython
        if use_parallel and not is_using_cython():
            self.parallel_toggle.blockSignals(True)
            self.parallel_toggle.setChecked(False)
            self.parallel_toggle.blockSignals(False)
            QMessageBox.warning(
                self,
                "Cython Required",
                "OpenMP parallelization requires Cython to be enabled.\n"
                "Please enable Cython first."
            )
            return
        
        # Try to switch
        success = set_use_parallel(use_parallel)
        
        if success:
            self.update_performance_label()
            mode = "Parallel (OpenMP)" if use_parallel else "Sequential"
            QMessageBox.information(
                self,
                "Parallelization Switched",
                f"Switched to {mode} execution!\n\n"
                f"Expected speedup: {'~20-30x (multi-core)' if use_parallel else '1x (single-core)'}"
            )
        else:
            # Failed to switch
            self.parallel_toggle.blockSignals(True)
            self.parallel_toggle.setChecked(False)
            self.parallel_toggle.blockSignals(False)
            self.update_performance_label()
            QMessageBox.warning(
                self,
                "Switch Failed",
                "Could not enable parallelization.\n"
                "Rebuild with: ./build_cython.sh\n"
                "Make sure OpenMP is available on your system."
            )
            QMessageBox.warning(self, "Error", "Could not enable OpenMP parallelization. Make sure to compile with: ./build_cython.sh")
    
    def start_simulation(self):
        """Start simulation."""
        params = self.param_widget.get_parameters()
        
        # Validate direction
        dir_vec = np.array([params.dir_x, params.dir_y, params.dir_z])
        norm = np.linalg.norm(dir_vec)
        if norm == 0:
            QMessageBox.warning(self, "Error", "Invalid direction vector!")
            return
        params.dir_x /= norm
        params.dir_y /= norm
        params.dir_z /= norm
        
        # Create simulation
        self.simulation = TRIMSimulation(params)
        self.sim_thread = SimulationThread(self.simulation)
        self.sim_thread.progress.connect(self.update_progress)
        self.sim_thread.finished.connect(self.simulation_finished)
        self.sim_thread.error.connect(self.simulation_error)
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.param_widget.set_enabled(False)
        self.export_button.setEnabled(False)
        if self.cython_toggle:
            self.cython_toggle.setEnabled(False)
        if self.parallel_toggle:
            self.parallel_toggle.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Simulation running...")
        
        self.sim_thread.start()
    
    def stop_simulation(self):
        """Stop simulation."""
        if self.sim_thread:
            self.sim_thread.stop()
    
    def update_progress(self, current, total):
        """Update progress bar."""
        progress = int(100 * current / total)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Ion {current} / {total}")
    
    def simulation_finished(self, results):
        """Handle simulation completion."""
        self.results = results
        
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.param_widget.set_enabled(True)
        self.export_button.setEnabled(True)
        if self.cython_toggle:
            self.cython_toggle.setEnabled(True)
        if self.parallel_toggle:
            self.parallel_toggle.setEnabled(True)
        self.progress_bar.setValue(100)
        self.progress_label.setText("Completed!")
        
        # Display results
        self.results_text.setText(results.get_summary())
        
        # Get parameters
        params = self.param_widget.get_parameters()
        geometry_obj = getattr(self.simulation, 'geometry_obj', None)
        
        # Plot all visualizations
        self.traj3d_canvas.plot_trajectories_3d(results.trajectories, geometry_obj)
        self.traj2d_xz_canvas.plot_trajectories(results.trajectories, params.zmin, params.zmax, 'xz')
        self.traj2d_yz_canvas.plot_trajectories(results.trajectories, params.zmin, params.zmax, 'yz')
        
        # Heatmaps
        if hasattr(results, 'stopped_positions') and results.stopped_positions:
            self.heatmap_xz_canvas.plot_density_heatmap_xz(results.stopped_positions, params.zmin, params.zmax)
            self.heatmap_yz_canvas.plot_density_heatmap_yz(results.stopped_positions, params.zmin, params.zmax)
            depth_mid = (params.zmin + params.zmax) / 2
            depth_range = (depth_mid - 200, depth_mid + 200)
            self.heatmap_xy_canvas.plot_density_heatmap_xy(results.stopped_positions, depth_range)
        
        # Energy loss
        if results.trajectories:
            self.energy_canvas.plot_energy_vs_depth(results.trajectories, params.zmin, params.zmax)
        
        # Radial distribution
        if hasattr(results, 'stopped_positions') and results.stopped_positions:
            self.radial_canvas.plot_radial_vs_depth(results.stopped_positions)
        
        # Histogram
        self.hist_canvas.plot_depth_histogram(results.stopped_depths, params.zmin, params.zmax)
    
    def simulation_error(self, error_msg):
        """Handle simulation error."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.param_widget.set_enabled(True)
        if self.cython_toggle:
            self.cython_toggle.setEnabled(True)
        if self.parallel_toggle:
            self.parallel_toggle.setEnabled(True)
        self.progress_label.setText("Error!")
        QMessageBox.critical(self, "Error", f"Simulation failed:\n{error_msg}")
    
    def export_results(self):
        """Export results in selected format."""
        if not self.results:
            return
        
        dialog = ExportDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        options = dialog.get_options()
        format_choice = options['format']
        
        # Get base filename
        base_file, _ = QFileDialog.getSaveFileName(
            self, "Save Export As", "", "All Files (*)"
        )
        
        if not base_file:
            return
        
        try:
            from pathlib import Path
            base_path = Path(base_file)
            exported_files = []
            
            is_all_formats = "All" in format_choice
            
            if "CSV" in format_choice or is_all_formats:
                try:
                    csv_path = base_path.with_suffix('.csv')
                    export.export_to_csv(self.results, csv_path, options['include_trajectories'])
                    exported_files.append(f"CSV: {csv_path.name}")
                except Exception as e:
                    print(f"CSV export failed: {e}")
                    if not is_all_formats:
                        raise
            
            if "JSON" in format_choice or is_all_formats:
                try:
                    json_path = base_path.with_suffix('.json')
                    export.export_to_json(self.results, json_path, options['include_trajectories'])
                    exported_files.append(f"JSON: {json_path.name}")
                except Exception as e:
                    print(f"JSON export failed: {e}")
                    if not is_all_formats:
                        raise
            
            if "VTK" in format_choice or is_all_formats:
                try:
                    if hasattr(self.results, 'stopped_positions') and self.results.stopped_positions:
                        vtk_path = base_path.with_suffix('.vtk')
                        export.export_to_vtk(self.results, vtk_path)
                        exported_files.append(f"VTK: {vtk_path.name}")
                except Exception as e:
                    print(f"VTK export failed: {e}")
                    if not is_all_formats:
                        raise
            
            if "PNG" in format_choice or is_all_formats:
                try:
                    canvases = [
                        ("traj3d", self.traj3d_canvas),
                        ("traj2d_xz", self.traj2d_xz_canvas),
                        ("traj2d_yz", self.traj2d_yz_canvas),
                        ("heatmap_xz", self.heatmap_xz_canvas),
                        ("heatmap_yz", self.heatmap_yz_canvas),
                        ("energy", self.energy_canvas),
                        ("histogram", self.hist_canvas),
                    ]
                    export.export_all_plots(canvases, base_path, options['dpi'])
                    exported_files.append("PNG: All plots")
                except Exception as e:
                    print(f"PNG export failed: {e}")
                    if not is_all_formats:
                        raise
            
            if exported_files:
                files_list = "\n".join(exported_files)
                QMessageBox.information(self, "Export Successful", 
                                      f"Successfully exported:\n{files_list}\n\nLocation: {base_path.parent}")
            else:
                QMessageBox.warning(self, "Export Warning", 
                                  "No files were exported. Check console for errors.")
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Export error details:\n{error_details}")
            QMessageBox.critical(self, "Export Error", f"Error during export:\n{str(e)}")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ExtendedMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
