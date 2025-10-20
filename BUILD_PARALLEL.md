# Building CyTRIM with OpenMP Parallelization

## Quick Start

```bash
# Clean any previous builds
./build_cython.sh clean

# Build Cython + OpenMP modules
./build_cython.sh

# Verify installation
python3 -c "from pytrim import is_parallel_available; print('Parallel:', is_parallel_available())"
```

Expected output:
```
✓ Parallel: True
```

## What Gets Built

Running `./build_cython.sh` compiles:

1. **Standard Cython modules** (6.4× faster):
   - `cytrim/estop.pyx` - Electronic stopping
   - `cytrim/scatter.pyx` - ZBL scattering
   - `cytrim/geometry.pyx` - Target geometry
   - `cytrim/select_recoil.pyx` - Collision geometry
   - `cytrim/trajectory.pyx` - Trajectory integration
   - `cytrim/geometry3d.pyx` - 3D geometry system

2. **OpenMP parallel module** (additional 4-8× faster):
   - `cytrim/simulation_parallel.pyx` - Multi-core parallelization

## Platform-Specific Requirements

### Linux (Ubuntu/Debian)
```bash
sudo apt install build-essential python3-dev
pip install Cython numpy
./build_cython.sh
```

### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install OpenMP library
brew install libomp

# Install Python dependencies
pip install Cython numpy

# Build
./build_cython.sh
```

### Windows
1. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
2. Install Python packages:
```cmd
pip install Cython numpy
```
3. Build:
```cmd
python setup.py build_ext --inplace
```

## Troubleshooting

### "Parallel: False" after build

**Possible causes:**
1. OpenMP library not found
2. Compilation failed silently

**Solutions:**

**Linux:**
```bash
# Install OpenMP (usually included with GCC)
sudo apt install libgomp1

# Check GCC supports OpenMP
gcc --version
echo '#include <omp.h>' | gcc -fopenmp -xc -E - > /dev/null && echo "OpenMP OK" || echo "OpenMP missing"
```

**macOS:**
```bash
# Install OpenMP library
brew install libomp

# Verify installation
brew list libomp

# Try rebuilding
./build_cython.sh clean
./build_cython.sh
```

**Windows:**
```cmd
REM OpenMP is included with MSVC, ensure you have Visual Studio Build Tools installed
python setup.py build_ext --inplace --verbose
```

### Build errors

**Check compiler output:**
```bash
python setup.py build_ext --inplace --verbose 2>&1 | tee build.log
```

Look for errors related to:
- `simulation_parallel.pyx`
- `-fopenmp` or `/openmp` flags
- Missing `omp.h` header

### Still having issues?

**Fallback to Cython-only mode:**

You can still use CyTRIM with 6.4× speedup (without parallel):
```python
from pytrim import set_use_cython, set_use_parallel

set_use_cython(True)   # ✓ 6.4× faster
set_use_parallel(False)  # Use single-threaded Cython
```

## Verifying Installation

Complete check:
```python
from pytrim import (
    is_cython_available,
    is_using_cython,
    is_parallel_available,
    is_using_parallel
)

print("Configuration:")
print(f"  Cython available: {is_cython_available()}")
print(f"  Cython active: {is_using_cython()}")
print(f"  Parallel available: {is_parallel_available()}")
print(f"  Parallel active: {is_using_parallel()}")

if is_parallel_available():
    print("\n✓ Full installation successful!")
    print("  Expected performance: ~40-50× faster than Python")
elif is_cython_available():
    print("\n⚠ Partial installation")
    print("  Cython working: ~6.4× faster than Python")
    print("  Parallel missing: rebuild with OpenMP support")
else:
    print("\n✗ Cython not available")
    print("  Running in pure Python mode (slow)")
```

## Performance Test

Quick benchmark:
```bash
python test_parallel.py 1000
```

This will:
- Run 1000 ions in sequential and parallel modes
- Show timing comparisons
- Verify results are consistent
- Display speedup achieved

Expected output (8-core system):
```
Mode                           Time (s)     Ions/s       Speedup
----------------------------------------------------------------------
Cython Sequential              4.50         222.2        1.00×
Parallel (2 threads)           2.30         434.8        1.96×
Parallel (4 threads)           1.20         833.3        3.75×
Parallel (8 threads)           0.60         1666.7       7.50×
```

## Next Steps

Once built successfully:

1. **Enable in GUI**: Check "Use OpenMP Parallel" checkbox
2. **Or use API**:
   ```python
   from pytrim import set_use_parallel
   set_use_parallel(True)
   ```
3. **Read documentation**: See [PARALLELIZATION.md](PARALLELIZATION.md) for details

## Summary

- ✅ **Easy**: One command builds everything
- ✅ **Fast**: 40-50× speedup with OpenMP
- ✅ **Fallback**: Still works without OpenMP (Cython only)
- ✅ **Compatible**: Linux, macOS, Windows

**Recommendation**: Always try to build with OpenMP for maximum performance!
