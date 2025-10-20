# Cython Toggle Feature

## Overview

The toggle feature lets users switch between Cython-optimized and pure Python modules at runtime without restarting the application.

## Funktionen

### 1. Performance status display
- **⚡ Cython enabled** (green): Cython modules are active (~6.4× faster)
- **🐍 Python mode** (orange): Python modules are active

### 2. Cython toggle checkbox
- Switches between Cython and Python modules
- Shows a tooltip with performance information
- Automatically disabled while simulations are running

### 3. Dynamic module reload
- Swaps modules at runtime
- Warns if a simulation result is already present
- Automatically validates Cython availability

## Verwendung

### In the GUI
1. Start the application with `python pytrim_gui.py`
2. Locate the performance indicator on the left panel
3. Enable or disable the "Use Cython" checkbox
4. Confirm the warning about reloading modules
5. New simulations will run with the selected modules

### Programmatisch

```python
from pytrim import is_cython_available, set_use_cython, is_using_cython

# Check whether Cython modules are available
if is_cython_available():
    print("Cython modules are compiled and available")

# Switch to Cython
success = set_use_cython(True)
if success:
    print("Successfully switched to Cython")

# Check the current mode
if is_using_cython():
    print("Using Cython modules")
else:
    print("Using Python modules")
```

## Technical Details

### Module system
- **Dynamic loading**: Modules are imported at runtime from `cytrim.*` or `pytrim.*`
- **Global references**: Modules are stored as global variables
- **Fallback mechanism**: Automatic fallback to Python if Cython raises errors

### Affected modules
- `estop` – electronic stopping power
- `scatter` – scattering calculations
- `geometry` – geometric utilities
- `select_recoil` – recoil selection
- `trajectory` – trajectory calculation

### GUI integration
- Toggle is disabled while simulations run
- Status label updates automatically
- Confirmation dialog appears when a result is already present
- Error message surfaces when Cython is unavailable

## Performance

### Benchmark results (500 ions)
- **Cython**: 2.2 seconds (~226 ions per second)
- **Python**: 14.2 seconds (~35 ions per second)
- **Speedup**: 6.4×

### When to prefer Cython
✅ **Large simulations** (>100 ions)
✅ **Production runs** with many iterations
✅ **Parameter sweeps** with numerous configurations

### When to prefer Python
✅ **Debugging** with detailed stack traces
✅ **Development** without recompilation
✅ **Small tests** (<50 ions)

## Troubleshooting

### Cython unavailable
```bash
# Compile the Cython modules
./build_cython.sh

# Verify the installation
python -c "from pytrim import is_cython_available; print(is_cython_available())"
```

### Modules fail to load
```bash
# Remove build artifacts
./build_cython.sh clean

# Recompile modules
./build_cython.sh
```

### Toggle does not respond
1. Ensure no simulation is running (the toggle is disabled while active)
2. Inspect Cython availability with `is_cython_available()`
3. Check the console output for errors

## Implementierungsdetails

### Files
- `pytrim/simulation.py`: dynamic module system
- `pytrim_gui.py`: GUI integration (toggle, status display)
- `pytrim/__init__.py`: API exports

### New API helpers
```python
# Exported in pytrim/__init__.py:
is_cython_available() -> bool
is_using_cython() -> bool
set_use_cython(use_cython: bool) -> bool
```

### GUI methods
```python
class MainWindow:
    def update_performance_label(self) -> None
    def toggle_cython(self, state: Qt.CheckState) -> None
```

## Future Extensions

- [ ] Automatic performance measurements for recommendations
- [ ] Persistent storage of the toggle preference
- [ ] Batch mode for automatic Cython selection
- [ ] Performance comparison tool

## Changelog

### v1.0 – Initial implementation
- Implemented dynamic module system
- Added GUI toggle with checkbox
- Built performance status indicator
- Added confirmation dialogs for safety
- Automatically disable toggle while simulations run
