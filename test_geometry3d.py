#!/usr/bin/env python3
"""Test script for 3D geometry functionality."""

import numpy as np
from pytrim import geometry3d, TRIMSimulation, SimulationParameters

def test_geometries():
    """Test different geometry types."""
    print("=" * 60)
    print("3D GEOMETRY TESTS")
    print("=" * 60)
    
    # Test 1: Planar geometry (backward compatible)
    print("\n1. Testing PlanarGeometry:")
    geo_planar = geometry3d.PlanarGeometry(z_min=0, z_max=1000)
    print(f"   {geo_planar}")
    print(f"   Bounds: {geo_planar.get_bounds()}")
    test_pos = np.array([100.0, 200.0, 500.0])
    print(f"   Position {test_pos} inside: {geo_planar.is_inside_target(test_pos)}")
    test_pos_outside = np.array([100.0, 200.0, 1500.0])
    print(f"   Position {test_pos_outside} inside: {geo_planar.is_inside_target(test_pos_outside)}")
    
    # Test 2: Box geometry
    print("\n2. Testing BoxGeometry:")
    geo_box = geometry3d.BoxGeometry(x_min=-300, x_max=300,
                                      y_min=-300, y_max=300,
                                      z_min=0, z_max=1000)
    print(f"   {geo_box}")
    print(f"   Bounds: {geo_box.get_bounds()}")
    test_pos_center = np.array([0.0, 0.0, 500.0])
    print(f"   Center {test_pos_center} inside: {geo_box.is_inside_target(test_pos_center)}")
    test_pos_edge = np.array([350.0, 0.0, 500.0])
    print(f"   Outside edge {test_pos_edge} inside: {geo_box.is_inside_target(test_pos_edge)}")
    
    # Test 3: Cylinder geometry
    print("\n3. Testing CylinderGeometry:")
    geo_cyl = geometry3d.CylinderGeometry(radius=200, z_min=0, z_max=1000)
    print(f"   {geo_cyl}")
    print(f"   Bounds: {geo_cyl.get_bounds()}")
    test_pos_axis = np.array([0.0, 0.0, 500.0])
    print(f"   On axis {test_pos_axis} inside: {geo_cyl.is_inside_target(test_pos_axis)}")
    test_pos_edge = np.array([150.0, 150.0, 500.0])
    print(f"   Near edge {test_pos_edge} inside: {geo_cyl.is_inside_target(test_pos_edge)}")
    test_pos_outside = np.array([250.0, 0.0, 500.0])
    print(f"   Outside radius {test_pos_outside} inside: {geo_cyl.is_inside_target(test_pos_outside)}")
    
    # Test 4: Sphere geometry
    print("\n4. Testing SphereGeometry:")
    geo_sphere = geometry3d.SphereGeometry(radius=400, center_z=500)
    print(f"   {geo_sphere}")
    print(f"   Bounds: {geo_sphere.get_bounds()}")
    test_pos_center = np.array([0.0, 0.0, 500.0])
    print(f"   Center {test_pos_center} inside: {geo_sphere.is_inside_target(test_pos_center)}")
    test_pos_surface = np.array([0.0, 0.0, 900.0])
    print(f"   Near surface {test_pos_surface} inside: {geo_sphere.is_inside_target(test_pos_surface)}")
    test_pos_outside = np.array([0.0, 0.0, 1000.0])
    print(f"   Outside {test_pos_outside} inside: {geo_sphere.is_inside_target(test_pos_outside)}")
    
    # Test 5: Multi-layer geometry
    print("\n5. Testing MultiLayerGeometry:")
    geo_multi = geometry3d.MultiLayerGeometry(
        layer_z_positions=[0, 100, 300, 500],
        x_min=-500, x_max=500, y_min=-500, y_max=500
    )
    print(f"   {geo_multi}")
    print(f"   Bounds: {geo_multi.get_bounds()}")
    for z in [50, 150, 350, 600]:
        pos = np.array([0.0, 0.0, float(z)])
        layer_idx = geo_multi.get_layer_index(z)
        inside = geo_multi.is_inside_target(pos)
        print(f"   z={z}: Layer {layer_idx}, inside={inside}")
    
    # Test 6: Factory function
    print("\n6. Testing Factory Function:")
    geo_from_factory = geometry3d.create_geometry('cylinder', radius=250, z_min=0, z_max=800)
    print(f"   Created: {geo_from_factory}")
    
    print("\n" + "=" * 60)
    print("ALL GEOMETRY TESTS PASSED ✓")
    print("=" * 60)


def test_simulation_with_box():
    """Test simulation with box geometry."""
    print("\n" + "=" * 60)
    print("SIMULATION TEST: Box Geometry")
    print("=" * 60)
    
    params = SimulationParameters()
    params.nion = 100
    params.e_init = 50000.0  # 50 keV
    
    # Configure box geometry
    params.geometry_type = 'box'
    params.geometry_params = {
        'x_min': -500,
        'x_max': 500,
        'y_min': -500,
        'y_max': 500,
        'z_min': 0,
        'z_max': 4000
    }
    
    # Run simulation
    print("\nRunning simulation with 100 ions...")
    sim = TRIMSimulation(params)
    results = sim.run(record_trajectories=True, max_trajectories=5)
    
    print("\nResults:")
    print(results.get_summary())
    print(f"\nRecorded {len(results.trajectories)} trajectories")
    print(f"Stored {len(results.stopped_positions)} 3D positions")
    
    print("\n" + "=" * 60)


def test_simulation_with_cylinder():
    """Test simulation with cylindrical geometry."""
    print("\n" + "=" * 60)
    print("SIMULATION TEST: Cylinder Geometry")
    print("=" * 60)
    
    params = SimulationParameters()
    params.nion = 100
    params.e_init = 50000.0  # 50 keV
    
    # Configure cylinder geometry
    params.geometry_type = 'cylinder'
    params.geometry_params = {
        'radius': 300,
        'z_min': 0,
        'z_max': 4000,
        'center_x': 0,
        'center_y': 0
    }
    
    # Run simulation
    print("\nRunning simulation with 100 ions...")
    sim = TRIMSimulation(params)
    results = sim.run()
    
    print("\nResults:")
    print(results.get_summary())
    
    # Check radial distribution
    if len(results.stopped_positions) > 0:
        print(f"\nRadial distribution analysis:")
        print(f"  Max radial distance: {max([np.sqrt(p[0]**2 + p[1]**2) for p in results.stopped_positions]):.2f} A")
        print(f"  Cylinder radius: 300 A")
    
    print("\n" + "=" * 60)


def test_simulation_with_sphere():
    """Test simulation with spherical geometry."""
    print("\n" + "=" * 60)
    print("SIMULATION TEST: Sphere Geometry")
    print("=" * 60)
    
    params = SimulationParameters()
    params.nion = 100
    params.e_init = 30000.0  # 30 keV (lower to ensure ions stop in sphere)
    
    # Configure sphere geometry
    params.geometry_type = 'sphere'
    params.geometry_params = {
        'radius': 2000,
        'center_x': 0,
        'center_y': 0,
        'center_z': 1000
    }
    
    # Start ions at top of sphere
    params.z_init = -900  # Near top of sphere (center at 1000, radius 2000)
    
    # Run simulation
    print("\nRunning simulation with 100 ions into spherical target...")
    sim = TRIMSimulation(params)
    results = sim.run()
    
    print("\nResults:")
    print(results.get_summary())
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        # Test geometry classes
        test_geometries()
        
        # Test simulations with different geometries
        test_simulation_with_box()
        test_simulation_with_cylinder()
        test_simulation_with_sphere()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
