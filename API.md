# PyTRIM API Reference

## Programmatic Usage

To embed the simulation in your own Python scripts:

```python
from pytrim.simulation import TRIMSimulation, SimulationParameters

# Create and customize parameters
params = SimulationParameters()
params.nion = 1000
params.z1 = 5          # Boron
params.m1 = 11.009
params.z2 = 14         # Silicon
params.m2 = 28.086
params.e_init = 50000  # 50 keV
params.density = 0.04994
params.zmin = 0.0
params.zmax = 4000.0

# Run the simulation
sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True, max_trajectories=10)

# Inspect results
print(f"Stopped ions: {results.count_inside} / {results.total_ions}")
print(f"Mean depth: {results.mean_z:.2f} Å")
print(f"Standard deviation: {results.std_z:.2f} Å")
print(f"Runtime: {results.simulation_time:.2f} s")

# Access raw data
depths = results.stopped_depths       # All stopping depths (z coordinates)
trajectories = results.trajectories   # Recorded trajectories (lists of positions)
```

## Classes

### `SimulationParameters`

Container for all simulation inputs.

**General**
- `nion` (int): number of primary ions to track

**Target geometry**
- `zmin` (float): lower z boundary (Å)
- `zmax` (float): upper z boundary (Å)

**Projectile**
- `z1` (int): atomic number
- `m1` (float): atomic mass (amu)
- `e_init` (float): initial kinetic energy (eV)
- `x_init`, `y_init`, `z_init` (float): starting position (Å)
- `dir_x`, `dir_y`, `dir_z` (float): direction vector (normalized automatically)

**Target**
- `z2` (int): atomic number
- `m2` (float): atomic mass (amu)
- `density` (float): atomic density (atoms/Å³)

**Physics**
- `corr_lindhard` (float): correction factor applied to Lindhard stopping

**Methods**
- `get_pos_init()`: returns the start position as a NumPy array
- `get_dir_init()`: returns the normalized direction vector as a NumPy array

### `TRIMSimulation`

Main entry point for running simulations.

**Constructor**
```python
sim = TRIMSimulation(params=None)
```
- `params`: optional `SimulationParameters` instance. Defaults to a built-in configuration.

**Methods**

`run(record_trajectories=False, max_trajectories=10)`
- Executes the simulation
- `record_trajectories`: whether to store individual trajectories (slower)
- `max_trajectories`: maximum number of trajectories to store
- Returns a `SimulationResults` object

`set_progress_callback(callback)`
- Registers a callback that receives `(current, total)` after each ion

`stop()`
- Stops an active simulation loop

### `SimulationResults`

Holds the outcome of a simulation run.

**Attributes**
- `count_inside` (int): number of ions that stopped inside the target
- `total_ions` (int): total number of simulated ions
- `mean_z` (float): mean stopping depth (Å)
- `std_z` (float): standard deviation of the stopping depth (Å)
- `simulation_time` (float): runtime in seconds
- `stopped_depths` (list[float]): individual stopping depths (Å)
- `trajectories` (list[list[tuple]]): recorded trajectories when enabled

**Methods**

`get_summary()`
- Returns a formatted summary string

## Examples

### Minimal simulation

```python
from pytrim.simulation import TRIMSimulation

sim = TRIMSimulation()
results = sim.run()
print(results.get_summary())
```

### With a progress callback

```python
from pytrim.simulation import TRIMSimulation, SimulationParameters

def progress(current, total):
    percent = 100 * current / total
    print(f"\rProgress: {percent:.1f}%", end="")

params = SimulationParameters()
params.nion = 1000

sim = TRIMSimulation(params)
sim.set_progress_callback(progress)
results = sim.run()
print("\n" + results.get_summary())
```

### Visualizing trajectories

```python
import matplotlib.pyplot as plt
import numpy as np
from pytrim.simulation import TRIMSimulation, SimulationParameters

params = SimulationParameters()
params.nion = 100

sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True, max_trajectories=10)

fig, ax = plt.subplots()
for traj in results.trajectories:
    if traj:
        data = np.array(traj)
        ax.plot(data[:, 2], data[:, 0], alpha=0.6)

ax.axvline(params.zmin, color="r", linestyle="--")
ax.axvline(params.zmax, color="r", linestyle="--")
ax.set_xlabel("z (Å)")
ax.set_ylabel("x (Å)")
ax.set_title("Ion trajectories")
plt.show()
```

### Stopping-depth histogram

```python
import matplotlib.pyplot as plt
from pytrim.simulation import TRIMSimulation, SimulationParameters

params = SimulationParameters()
params.nion = 1000

sim = TRIMSimulation(params)
results = sim.run()

plt.hist(results.stopped_depths, bins=50, edgecolor="black")
plt.axvline(results.mean_z, color="r", linestyle="--",
            label=f"Mean: {results.mean_z:.1f} Å")
plt.xlabel("Stopping depth (Å)")
plt.ylabel("Ion count")
plt.title("Distribution of stopping depths")
plt.legend()
plt.show()
```

### Energy scan

```python
import numpy as np
import matplotlib.pyplot as plt
from pytrim.simulation import TRIMSimulation, SimulationParameters

energies = [10000, 20000, 30000, 50000, 75000, 100000]
mean_depths = []
std_depths = []

for energy in energies:
    params = SimulationParameters()
    params.nion = 1000
    params.e_init = energy

    sim = TRIMSimulation(params)
    results = sim.run()

    mean_depths.append(results.mean_z)
    std_depths.append(results.std_z)
    print(f"{energy/1000:.0f} keV: {results.mean_z:.1f} ± {results.std_z:.1f} Å")

plt.errorbar(np.array(energies) / 1000, mean_depths, yerr=std_depths,
             marker="o", capsize=5)
plt.xlabel("Energy (keV)")
plt.ylabel("Mean penetration depth (Å)")
plt.title("Penetration depth vs. energy (B in Si)")
plt.grid(True, alpha=0.3)
plt.show()
```

## Advanced Configuration

### Adjusting the energy cutoff

The minimum energy at which ions are considered stopped:

```python
import pytrim.trajectory as traj
traj.EMIN = 10.0  # default is 5.0 eV
```

**Note:** Set this before the first call to `setup()`.

### Material reference values

Typical atomic densities (atoms/Å³):

- Si (crystalline): 0.04994
- Si (amorphous): 0.049
- GaAs: 0.044
- SiO₂: 0.066
- Al: 0.0603
- Cu: 0.0845

Common atomic numbers and masses:

| Element | Z  | Mass (amu) |
|---------|----|-------------|
| B       | 5  | 10.81       |
| N       | 7  | 14.007      |
| P       | 15 | 30.974      |
| As      | 33 | 74.922      |
| Si      | 14 | 28.086      |
| Ga      | 31 | 69.723      |
| Ar      | 18 | 39.948      |

## Performance Notes

- Runtime scales linearly with `nion`
- Recording trajectories adds roughly 10–20% overhead
- Higher energies → longer paths → longer runtimes
- Lower densities → longer free paths → longer runtimes

Typical runtimes (Intel i5, Python build):
- 100 ions: ~0.5 s
- 1000 ions: ~5 s
- 10000 ions: ~50 s
