#!/usr/bin/env python3
"""Debug script to check geometry setup."""

import numpy as np
from pytrim import TRIMSimulation, SimulationParameters

# Test with box geometry
params = SimulationParameters()
params.nion = 1
params.e_init = 50000.0

params.geometry_type = 'box'
params.geometry_params = {
    'x_min': -500,
    'x_max': 500,
    'y_min': -500,
    'y_max': 500,
    'z_min': 0,
    'z_max': 4000
}

sim = TRIMSimulation(params)
sim.setup()

# Check if geometry is set up
print("Geometry object:", sim.geometry_obj)
print("Type:", type(sim.geometry_obj))
print("Bounds:", sim.geometry_obj.get_bounds())

# Test point
test_pos = np.array([0.0, 0.0, 100.0])
print(f"\nTest position {test_pos}:")
print(f"  is_inside_target: {sim.geometry_obj.is_inside_target(test_pos)}")

# Try to get the geometry from the module
try:
    from cytrim import geometry3d
    global_geo = geometry3d.get_global_geometry()
    print(f"\nGlobal geometry: {global_geo}")
    if global_geo:
        print(f"  Type: {type(global_geo)}")
        print(f"  Test: {global_geo.is_inside_target(test_pos)}")
except Exception as e:
    print(f"\nError accessing global geometry: {e}")

# Check what geometry module trajectory is using
try:
    from cytrim import trajectory, geometry
    print(f"\nTrajectory module geometry: {geometry}")
    print(f"  Has is_inside_target: {hasattr(geometry, 'is_inside_target')}")
    
    # Try calling it
    result = geometry.is_inside_target(test_pos)
    print(f"  Result: {result}")
except Exception as e:
    print(f"\nError with trajectory geometry: {e}")
    import traceback
    traceback.print_exc()
