# CyTRIM (PyTRIM) - Advanced Edition

CyTRIM is a professional Python implementation of TRIM (Transport of Ions in Matter) with modern features for research and teaching. The program simulates the transport of ion beams into complex 3D geometries using Monte Carlo techniques and provides extensive tooling for analysis and visualization.

**Version 2.0 – Advanced Edition**
- 🎯 **Extended GUI** with material presets and dynamic geometry selection
- 📊 **10+ visualizations** including heatmaps, energy loss, and radial distributions
- 💾 **Multi-format export** (CSV, JSON, VTK, PNG) for downstream processing
- ⚡ **Up to 6.4× faster** through Cython acceleration

> **📖 Quick Start:** [QUICKSTART.md](QUICKSTART.md) · **🚀 Advanced Feature Overview:** [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)

## Core Features

### Physics & Simulation
- **Monte Carlo ion transport** with realistic scattering physics
- **3D trajectory tracking** with full position history for each ion
- **Five geometry types:** Planar, Box, Cylinder, Sphere, and MultiLayer targets
- **ZBL potential** for elastic scattering
- **Lindhard stopping power** with configurable correction factor
- **Recoil cascade groundwork** (in progress) for radiation damage studies

### User Interface
- **Modern PyQt6 GUI** with more than ten visualization tabs
- **Material presets** covering common implantation scenarios (B in Si, As in Si, etc.)
- **Dynamic geometry selection** with context-aware parameter forms
- **Real-time progress and performance indicators**
- **Interactive Matplotlib views** with rotation, zoom, and selection

### Visualization & Analysis
- **3D trajectory plots** with target geometry overlays
- **2D projections** (x–z, y–z) for detailed inspection
- **Density heatmaps** (x–z, y–z, x–y) with smoothing options
- **Energy loss trends** including averaged profiles
- **Radial distribution vs. depth** to quantify lateral spread
- **Stopping-depth histograms** with key statistics

### Export & Integration
- **CSV:** tabular data for Excel, pandas, or MATLAB workflows
- **JSON:** structured data for scripting and automation
- **VTK:** polyline exports compatible with ParaView and VTK pipelines
- **PNG:** high-resolution plots (300 DPI) for publications
- **Trajectory exports:** raw coordinate tracks for downstream analysis

### Performance
- **Cython optimization** delivering up to 6.4× speedup vs. pure Python
- **OpenMP parallelization** providing additional 7-8× speedup on multi-core systems (up to 50× total)
- **Runtime toggles** for both Cython and parallel execution
- **Automatic fallback** to pure Python when compiled modules are absent
- **Performance telemetry** surfaced directly in the GUI with live indicators

## What Does the Program Do?

- Simulates many primary ions consecutively (Monte Carlo approach).
- Moves each ion step-by-step until it stops (energy below the cutoff) or leaves the target.
- Applies electronic stopping according to Lindhard with a configurable correction factor along the free path to the next collision.
- Handles elastic scattering on target atoms using the ZBL potential and Biersack's “magic formula” for scattering angles.
- Records the stopping depth of ions that come to rest in the target and computes mean value and standard deviation.

Units: positions in Å, energies in eV, densities in atoms/Å³.

## How It Works (Workflow)

1. **Initialization**
   - `select_recoil.setup(density)`: derive mean free path from the target density.
   - `scatter.setup(z1, m1, z2, m2)`: prepare constants for ZBL scattering (normalization, mass ratios).
   - `estop.setup(corr_lindhard, z1, m1, z2, density)`: pre-compute Lindhard stopping factors.
   - `geometry.setup(zmin, zmax)`: define planar target bounds along z.
   - `trajectory.setup()`: set the energy cutoff `EMIN` (default 5 eV).

2. **Trajectory of a single ion (`trajectory.trajectory`)**
   - Determine free path and collision geometry with `select_recoil.get_recoil_position(pos, dir)`, yielding path length, impact parameter *p*, and recoil direction.
   - Apply electronic energy loss along the path via `estop.eloss(e, free_path)` (Lindhard, ΔE ∝ √E × path length).
   - Update the position and check with `geometry.is_inside_target` whether the ion remains within the target.
   - Perform elastic scattering at the target atom using `scatter.scatter(e, dir, p, dirp)` (ZBL + magic formula), producing the new projectile direction and energy; recoil tracking is currently not propagated further.
   - Repeat until `e ≤ EMIN` or the ion exits the target region.

3. **Statistics**
   - Count ions that stop inside the target and accumulate their stopping depth *z*.
   - Report number of stopped ions, mean stopping depth, standard deviation, and runtime.

## Project Structure

### GUI Version (recommended)
- `pytrim_gui.py`: main application with the standard PyQt6 interface.
- `pytrim/simulation.py`: object-oriented simulation pipeline (`TRIMSimulation`, `SimulationParameters`, `SimulationResults`).

### Core Modules
- `pytrim/trajectory.py`: advances a single ion until it stops or exits the target.
- `pytrim/select_recoil.py`: samples the next collision in an amorphous target (mean free path ∝ density^(-1/3)).
- `pytrim/estop.py`: computes Lindhard-based electronic stopping with correction factor.
- `pytrim/scatter.py`: implements ZBL potential and Biersack’s magic formula for scattering.
- `pytrim/geometry.py`: planar geometry helper (z min / z max constraints).

### Legacy
- `pytrim/pytrim.py`: original command-line reference implementation.

## Installation

### Requirements
- Python ≥ 3.8
- NumPy
- PyQt6 (GUI)
- Matplotlib (visualizations)
- Cython (optional for performance)
- C compiler (optional to build the Cython extensions)

### Quick Installation
```bash
# Clone or download the repository
cd CyTRIM

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Cython Optimization (recommended)
```bash
# After installing dependencies
./build_cython.sh

# Alternatively
pip install Cython
python setup.py build_ext --inplace
```
**Note:** If compilation fails, the application still runs in pure Python (slower but feature complete).

## Running the Application

### GUI Version (recommended)

**Standard GUI**
```bash
./run_gui.sh
```

**Extended GUI with advanced tooling**
```bash
./run_extended_gui.sh
```
The extended GUI provides:
- 📐 Geometry selection (Planar, Box, Cylinder, Sphere, MultiLayer)
- 🧪 Material presets (B in Si, As in Si, etc.)
- 📊 10+ visualization tabs
- 💾 Multi-format export (CSV, JSON, VTK, PNG)

**Manual launch**
```bash
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate    # Windows
python pytrim_gui.py
```

### Cython Toggle Feature
- A “Use Cython” checkbox appears in the performance panel (enabled when compiled modules are available).
- ⚡ **Cython mode** (~6.4× faster) for production runs and large simulations (>100 ions).
- 🐍 **Python mode** for debugging, development, or small test cases (<50 ions).
- Switching happens at runtime—no restart required. See [TOGGLE_FEATURE.md](TOGGLE_FEATURE.md) for details.

### Command-Line Version (legacy)
```bash
python pytrim/pytrim.py
```
The CLI reports the number of ions that stop inside the target alongside mean penetration depth, standard deviation, and runtime.

## Configuring the Simulation

### GUI Parameters
- **Number of ions:** total primaries to simulate.
- **Target geometry:** `z_min`, `z_max` define planar bounds; alternate geometries expose additional fields.
- **Projectile:** atomic number, atomic mass (amu), initial energy (eV), start position (Å), and direction (unit vector).
- **Target material:** atomic number, atomic mass, density (atoms/Å³).
- **Physics:** Lindhard correction factor (typically 1.0–2.0).

### Command-Line Parameters
Defined near the top of `pytrim/pytrim.py`:
- `nion`: number of primary ions.
- `zmin`, `zmax`: planar geometry limits.
- `z1`, `m1`: projectile atomic number and mass.
- `z2`, `m2`: target atomic number and mass.
- `density`: target density.
- `corr_lindhard`: Lindhard correction factor.
- Initial conditions: `e_init` (eV), `pos_init` (Å), `dir_init` (unit vector).
- Advanced: energy cutoff per ion (`EMIN`) in `pytrim/trajectory.py` (default 5 eV).

## Example Scenarios

### Demo Script (showcases every feature)
```bash
python demo_advanced_features.py
```
Demonstrates:
1. Loading material presets.
2. Switching between geometry templates.
3. Exporting results in all formats.
4. Exploring the extended visualization suite.

### GUI Workflow
- Launch the extended GUI (`./run_extended_gui.sh`).
- Click **“Load Preset…”**, choose “B in Si”, confirm.
- Adjust the number of ions (e.g. 5000) and start the simulation.
- Review all result tabs and export data via **“💾 Export…”**.

### Custom Geometry
- Open the **Geometry** tab.
- Pick a geometry (e.g. cylinder) and enter radius, bounds, and axis.
- Configure material parameters in **Basic Parameters** and start the run.

### Sample Code (Python API)
```python
from pytrim.simulation import TRIMSimulation, SimulationParameters
from pytrim.presets import get_preset_manager
from pytrim import export

manager = get_preset_manager()
preset = manager.get_preset("B in Si")

params = SimulationParameters()
params.nion = 1000
params.z1, params.m1 = preset.z1, preset.m1
params.z2, params.m2 = preset.z2, preset.m2
params.density = preset.density
params.e_init = preset.energy
params.corr_lindhard = preset.corr_lindhard
params.zmin, params.zmax = preset.zmin, preset.zmax

params.geometry_type = "cylinder"
params.geometry_params = {"radius": 500, "axis": "z"}

sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True, max_trajectories=20)
print(results.get_summary())

export.export_to_json(results, "results.json")
export.export_to_vtk(results, "results.vtk")
```

### Example Scenario: Nanowire Implantation
```python
params = SimulationParameters()
params.nion = 2000
params.z1, params.m1 = 15, 30.974   # Phosphorus
params.z2, params.m2 = 14, 28.086   # Silicon
params.density = 0.04994
params.corr_lindhard = 1.5

params.geometry_type = "cylinder"
params.geometry_params = {"radius": 50, "axis": "z"}
params.zmin, params.zmax = 0, 3000
params.e_init = 60000
params.z_init = 0
params.dir_z = 1.0

sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True)
print(f"Stopped in wire: {results.stopped}/{results.nion}")
print(f"Radial spread: {results.mean_r:.1f} ± {results.std_r:.1f} Å")
```

### Reference Values
- **Boron in silicon:** Z=5, mass=11.009 amu; target Z=14, mass=28.086 amu; energy 50 keV; density 0.04994 atoms/Å³; expected depth ≈ 2000–2500 Å.
- **Arsenic in silicon:** Z=33, mass=74.922 amu; target Z=14, mass=28.086 amu; energy 100 keV; expected depth smaller due to heavier ion mass.

## Screenshots & Visualization Highlights
1. **Trajectory plot:** up to ten ion paths with target boundaries.
2. **Stopping-depth histogram:** distribution with mean indicator.
3. **Results view:** stopped ion count, mean depth, standard deviation, runtime, and performance metrics.

## Performance

Benchmark (500 ions, B in Si, 50 keV):

| Implementation | Time  | Ions/s | Speedup |
|----------------|-------|--------|---------|
| Pure Python    | 14.2s | 35     | 1.0×    |
| **Cython**     | **2.2s** | **226** | **6.4×** |

Typical runtimes with Cython:
- 100 ions: ~0.4 s
- 1000 ions: ~4.5 s
- 10000 ions: ~45 s

Without Cython (pure Python):
- 100 ions: ~3 s
- 1000 ions: ~28 s
- 10000 ions: ~280 s (~4.7 min)

### Run the Benchmarks
```bash
python benchmark.py 1000
python compare_performance.py   # Python vs Cython comparison
python test_toggle.py           # Validate the runtime toggle feature
```

## Programmatic Control
```python
from pytrim import (
    is_cython_available,
    is_using_cython,
    set_use_cython,
)

if is_cython_available():
    print("Cython modules are available!")

set_use_cython(True)
print("Using Cython:" if is_using_cython() else "Using Python:")
```
See [API.md](API.md) and [TOGGLE_FEATURE.md](TOGGLE_FEATURE.md) for the full API surface.

## Assumptions & Limitations
- Amorphous target; crystal channeling is not modeled.
- Constant mean free path (collision probability independent of ion energy or angle).
- Only primary ions are tracked; recoil cascades are currently not propagated.
- Planar geometry is the baseline; advanced geometries are parameterized shapes.
- Electronic stopping follows Lindhard with a global correction factor.

## References
- J. F. Ziegler, J. P. Biersack, U. Littmark, *The Stopping and Range of Ions in Matter*, Pergamon Press, 1985 (ZBL potential).
- J. Lindhard, M. Scharff, H. E. Schiøtt, *Range Concepts and Heavy Ion Ranges in Solids*, Mat. Fys. Medd. Dan. Vid. Selsk. 33 (1963); see also *Phys. Rev.* 124 (1961) 128.
- SRIM/TRIM: https://www.srim.org/

## License
See `LICENSE` in the repository root.

## Documentation
- [QUICKSTART.md](QUICKSTART.md): quick-start guide for the GUI.
- [API.md](API.md): API usage and examples.
- [CYTHON.md](CYTHON.md): details on the Cython build and optimization.

## Contact & Support
1. Review the documentation (QUICKSTART.md, README.md).
2. Check troubleshooting notes in QUICKSTART.md.
3. Open an issue on GitHub if you need further assistance.
