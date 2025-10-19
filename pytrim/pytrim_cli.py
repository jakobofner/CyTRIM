"""PyTRIM command-line version.

This is the legacy command-line interface. For a modern GUI version,
use pytrim_gui.py instead.
"""
from simulation import TRIMSimulation, SimulationParameters

# Create default parameters
params = SimulationParameters()

# You can modify parameters here if needed
# params.nion = 1000
# params.e_init = 50000.0
# etc.

# Run simulation
print("Starting PyTRIM simulation...")
print(f"Simulating {params.nion} ions...")
print()

simulation = TRIMSimulation(params)
results = simulation.run()

# Print results
print()
print("=" * 60)
print(results.get_summary())
print("=" * 60)
