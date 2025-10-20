"""Test trajectory recording with energy."""
import numpy as np
from pytrim.simulation import TRIMSimulation, SimulationParameters

# Simple test
params = SimulationParameters()
params.nion = 5
params.z1 = 5  # B
params.m1 = 11.009
params.z2 = 14  # Si
params.m2 = 28.086
params.density = 0.04994
params.e_init = 50000
params.corr_lindhard = 1.5
params.zmin = 0
params.zmax = 4000

print("Testing trajectory recording with energy...")
sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True, max_trajectories=5)

print(f"\nRecorded {len(results.trajectories)} trajectories")

if results.trajectories:
    for i, traj in enumerate(results.trajectories):
        print(f"\nTrajectory {i+1}:")
        print(f"  Length: {len(traj)} points")
        
        # Check first point
        first = traj[0]
        print(f"  First point: {first}")
        print(f"  Type: {type(first)}")
        print(f"  Length: {len(first)}")
        
        if len(first) == 4:
            x, y, z, e = first
            print(f"  ✓ Has 4 elements: x={x:.1f}, y={y:.1f}, z={z:.1f}, E={e:.1f} eV")
        else:
            print(f"  ✗ ERROR: Expected 4 elements, got {len(first)}")
        
        # Convert to array and check
        traj_arr = np.array(traj)
        print(f"  Array shape: {traj_arr.shape}")
        
        if traj_arr.shape[1] == 4:
            print(f"  ✓ Array has 4 columns (x, y, z, E)")
            print(f"  Initial energy: {traj_arr[0, 3]:.1f} eV")
            print(f"  Final energy: {traj_arr[-1, 3]:.1f} eV")
        else:
            print(f"  ✗ ERROR: Expected 4 columns, got {traj_arr.shape[1]}")

print("\n✓ Test complete!")
