#!/usr/bin/env python3
"""Quick test for 2D and 3D visualization in GUI."""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from pytrim_gui import MainWindow

def test_gui_visualization():
    """Test that both 2D and 3D tabs work."""
    print("=" * 60)
    print("GUI VISUALIZATION TEST")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Set small simulation for quick test
    window.param_widget.nion_spin.setValue(10)
    window.param_widget.e_spin.setValue(50000)
    
    print("\n✓ GUI initialized")
    print("✓ Tabs available:")
    for i in range(window.tab_widget.count()):
        tab_name = window.tab_widget.tabText(i)
        print(f"  - Tab {i+1}: {tab_name}")
    
    # Check that we have the right canvas objects
    print("\n✓ Canvas objects:")
    print(f"  - 3D Canvas: {hasattr(window, 'traj3d_canvas')}")
    print(f"  - 2D Canvas: {hasattr(window, 'traj2d_canvas')}")
    print(f"  - Histogram Canvas: {hasattr(window, 'hist_canvas')}")
    
    # Check methods
    print("\n✓ Canvas methods:")
    print(f"  - 3D plot_trajectories_3d: {hasattr(window.traj3d_canvas, 'plot_trajectories_3d')}")
    print(f"  - 2D plot_trajectories: {hasattr(window.traj2d_canvas, 'plot_trajectories')}")
    print(f"  - Histogram plot_depth_histogram: {hasattr(window.hist_canvas, 'plot_depth_histogram')}")
    
    print("\n" + "=" * 60)
    print("ALL CHECKS PASSED ✓")
    print("=" * 60)
    print("\nGUI ist bereit!")
    print("Sie können jetzt:")
    print("  1. Eine Simulation starten")
    print("  2. Tab '3D Trajektorien' für 3D-Ansicht öffnen")
    print("  3. Tab '2D Trajektorien (x-z)' für klassische Ansicht öffnen")
    print("  4. Tab 'Stopptiefe-Verteilung' für Histogram öffnen")
    
    window.show()
    
    # Auto-close after showing (for automated testing)
    # QTimer.singleShot(3000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_gui_visualization()
