#!/usr/bin/env python3
"""Demo script for 3D geometries in GUI.

This script demonstrates how to quickly test different geometry types.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from pytrim_gui import MainWindow
from pytrim import SimulationParameters

def demo_box_geometry():
    """Demo: Box geometry simulation."""
    print("Starting GUI with Box Geometry demo...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Configure box geometry
    params = SimulationParameters()
    params.nion = 50
    params.e_init = 50000  # 50 keV
    params.geometry_type = 'box'
    params.geometry_params = {
        'x_min': -500,
        'x_max': 500,
        'y_min': -500,
        'y_max': 500,
        'z_min': 0,
        'z_max': 4000
    }
    
    # Update GUI parameters
    window.param_widget.nion_spin.setValue(params.nion)
    window.param_widget.e_spin.setValue(params.e_init)
    
    # Show message
    QMessageBox.information(
        window,
        "3D Box Geometry Demo",
        "Konfiguriert für Box-Geometrie:\n"
        "- 500×500×4000 Å³\n"
        "- 50 keV Bor-Ionen\n"
        "- 50 Ionen\n\n"
        "Klicke 'Simulation starten' um die 3D-Visualisierung zu sehen!"
    )
    
    window.show()
    sys.exit(app.exec())


def demo_cylinder_geometry():
    """Demo: Cylinder geometry simulation."""
    print("Starting GUI with Cylinder Geometry demo...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Configure cylinder geometry
    params = SimulationParameters()
    params.nion = 50
    params.e_init = 50000
    params.geometry_type = 'cylinder'
    params.geometry_params = {
        'radius': 300,
        'z_min': 0,
        'z_max': 4000,
        'center_x': 0,
        'center_y': 0
    }
    
    window.param_widget.nion_spin.setValue(params.nion)
    window.param_widget.e_spin.setValue(params.e_init)
    
    QMessageBox.information(
        window,
        "3D Cylinder Geometry Demo",
        "Konfiguriert für Zylinder-Geometrie:\n"
        "- Radius: 300 Å\n"
        "- Höhe: 4000 Å\n"
        "- 50 keV Bor-Ionen\n\n"
        "Die 3D-Ansicht zeigt den Zylinder transparent!"
    )
    
    window.show()
    sys.exit(app.exec())


def demo_sphere_geometry():
    """Demo: Sphere geometry simulation."""
    print("Starting GUI with Sphere Geometry demo...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Configure sphere geometry
    params = SimulationParameters()
    params.nion = 50
    params.e_init = 30000  # Lower energy for sphere
    params.z_init = -900   # Start above sphere
    params.geometry_type = 'sphere'
    params.geometry_params = {
        'radius': 2000,
        'center_x': 0,
        'center_y': 0,
        'center_z': 1000
    }
    
    window.param_widget.nion_spin.setValue(params.nion)
    window.param_widget.e_spin.setValue(params.e_init)
    window.param_widget.z_init_spin.setValue(params.z_init)
    
    QMessageBox.information(
        window,
        "3D Sphere Geometry Demo",
        "Konfiguriert für Kugel-Geometrie:\n"
        "- Radius: 2000 Å\n"
        "- Zentrum bei (0, 0, 1000)\n"
        "- 30 keV Energie (niedriger)\n"
        "- Start bei z=-900 Å\n\n"
        "Perfekt für 3D-Visualisierung!"
    )
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="3D Geometry Demo for CyTRIM GUI")
    parser.add_argument('--geometry', choices=['box', 'cylinder', 'sphere', 'planar'],
                       default='box', help='Geometry type to demo')
    
    args = parser.parse_args()
    
    if args.geometry == 'box':
        demo_box_geometry()
    elif args.geometry == 'cylinder':
        demo_cylinder_geometry()
    elif args.geometry == 'sphere':
        demo_sphere_geometry()
    else:
        # Default: just start GUI normally
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
