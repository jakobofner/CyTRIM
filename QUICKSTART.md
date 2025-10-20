# PyTRIM GUI - Quick Start

## One-Time Installation

```bash
# Create a virtual environment
python3 -m venv .venv

# Install dependencies
.venv/bin/pip install -r requirements.txt

# Optional but recommended: build Cython modules for ~6.4× faster runs
./build_cython.sh
```

**Note:** If the Cython build fails, the application still runs in pure Python (roughly 6× slower).

## Launching the GUI

### Option 1: Launch script (Linux/macOS)
```bash
./run_gui.sh
```

### Option 2: Manual launch
```bash
# Activate the virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Start the GUI
python pytrim_gui.py
```

## Using the Interface

1. **Adjust simulation parameters** (left column)
   - Number of ions (e.g. 1000 for a quick run, 10000 for better statistics)
   - Projectile properties (Z, mass, energy)
   - Target properties (Z, mass, density, geometry)

2. **Check the performance status** (left panel)
   - ⚡ **Cython enabled:** ~6.4× faster execution
   - 🐍 **Python fallback:** standard speed when Cython is unavailable

3. Click **“Start Simulation”**

4. **Review the result tabs**
   - **Trajectories:** first 10 ion paths with target boundaries
   - **Stopping-depth distribution:** histogram of final depths
   - **Results:** summary statistics (mean, standard deviation, performance info)

5. **Optional:** export the results to a text report via “Export Results”

## Example Scenarios

### Quick smoke test
- Ions: 100
- Projectile: B (Z=5, M=11), energy 50,000 eV
- Target: Si (Z=14, M=28.086, density 0.04994)
- Runtime with Cython: ~0.4 s
- Runtime without Cython: ~3 s

### Standard production run
- Ions: 1000
- Runtime with Cython: ~4.5 s
- Runtime without Cython: ~28 s

### High-accuracy run
- Ions: 10000
- Runtime with Cython: ~45 s
- Runtime without Cython: ~4.7 min

## Tips

- **Trajectory view:** only the first 10 ions are rendered for performance
- **Histogram tab:** includes every simulated ion
- **Zoom and pan:** use the Matplotlib toolbar below each plot
- **Default parameter set:** tuned for B in Si at 50 keV

## Common Issues

**GUI will not start**
```bash
# Check whether PyQt6 is installed
.venv/bin/pip list | grep PyQt6

# Reinstall if missing
.venv/bin/pip install PyQt6 matplotlib
```

**Simulation feels slow**
```bash
# Verify whether Cython is active
.venv/bin/python -c "from pytrim.simulation import is_using_cython; print('Cython:', is_using_cython())"

# Build Cython modules if needed
./build_cython.sh

# Compare performance
.venv/bin/python compare_performance.py
```

**Cython build fails**
- Ensure a C compiler is available (gcc on Linux, Xcode command-line tools on macOS, MSVC/Build Tools on Windows)
- The application still works in pure Python (just slower)
- As a workaround, reduce the number of ions for shorter runs

**“Direction vector cannot be zero”**
- At least one component of `(dir_x, dir_y, dir_z)` must be non-zero
- The vector is normalized automatically
