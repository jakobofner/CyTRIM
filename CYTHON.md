# Cython Optimization - Technical Reference

## Overview

CyTRIM uses Cython to translate compute-intensive Python modules into optimized C extensions. This delivers a 6.4x speed increase without changing the user interface or the public API.

## Performance Gains

### Benchmark results (500 ions, B in Si, 50 keV)

| Metric | Pure Python | Cython | Improvement |
|--------|-------------|--------|-------------|
| Total runtime | 14.17 s | 2.21 s | **6.4x** |
| Ions per second | 35.3 | 226.0 | **6.4x** |
| Time per ion | 28.3 ms | 4.4 ms | **6.4x** |

### Scaling

| Ions | Python | Cython | Time saved |
|------|--------|--------|------------|
| 100 | ~3 s | ~0.4 s | 2.6 s |
| 1000 | ~28 s | ~4.5 s | 23.5 s |
| 10000 | ~280 s | ~45 s | **235 s** (3.9 min) |

## Optimized Modules

### 1. `cytrim/estop.pyx` - electronic stopping
**Optimizations**
- `cpdef` for public functions (C API plus Python wrapper)
- `cdef double` for every variable
- `sqrt()` from `libc.math` instead of `math.sqrt()`
- Inlined arithmetic instead of Python operations

**Speedup:** ~5-6x

### 2. `cytrim/scatter.pyx` - ZBL scattering  
**Optimizations**
- `cdef inline ... nogil` for internal helpers
- Static typing for all variables
- Avoid Python object usage inside tight loops
- Direct array indexing with bounds checking disabled
- C math functions (`exp`, `sqrt`)

**Speedup:** ~8-10x (largest bottleneck)

### 3. `cytrim/trajectory.pyx` - trajectories
**Optimizations**
- Typed NumPy arrays (`cnp.ndarray[cnp.float64_t, ndim=1]`)
- `cimport` for fast calls into other Cython modules
- Avoid Python lists inside inner loops

**Speedup:** ~6-7x

### 4. `cytrim/select_recoil.pyx` - collision geometry
**Optimizations**
- Trigonometric functions from `libc.math`
- Avoid Python overhead for random numbers
- Inline calculations

**Speedup:** ~4-5x

### 5. `cytrim/geometry.pyx` - target geometry
**Optimizations**
- Lightweight `cpdef` functions with direct array access
- No Python object allocation

**Speedup:** ~3-4x

## Compiler Directives

```python
# cython: language_level=3        # Python 3 syntax
# cython: boundscheck=False       # Disable array bounds checks
# cython: wraparound=False        # Disable negative indexing semantics
# cython: cdivision=True          # Use C division (faster, no ZeroDivisionError)
```

## Compiler Flags

### Linux/macOS
```bash
-O3                # highest optimization level
-ffast-math        # faster math operations
-march=native      # CPU-specific tuning
```

### Windows (MSVC)
```bash
/O2                # highest optimization level
```

## Build Process

### Automatic build
```bash
./build_cython.sh
```

### Manual build
```bash
# Install prerequisites
pip install Cython numpy

# Compile in place
python setup.py build_ext --inplace

# Smoke test
python -c "from pytrim.simulation import is_using_cython; print('Cython:', is_using_cython())"
```

### Output artifacts
```
cytrim/estop.cpython-312-x86_64-linux-gnu.so
cytrim/scatter.cpython-312-x86_64-linux-gnu.so
cytrim/geometry.cpython-312-x86_64-linux-gnu.so
cytrim/select_recoil.cpython-312-x86_64-linux-gnu.so
cytrim/trajectory.cpython-312-x86_64-linux-gnu.so
```

## Architecture

### Import mechanism
```python
# In pytrim/simulation.py
try:
   from cytrim import select_recoil  # attempt Cython backend
    from cytrim import scatter
    # ...
    _using_cython = True
except ImportError:
   from . import select_recoil        # fallback to Python
    from . import scatter
    # ...
    _using_cython = False
```

### Benefits
- Automatic fallback to pure Python
- No duplicated code for consumers
- Transparent usage
- Identical API for both backends

## Debugging

### Inspect Cython annotations
```bash
# Generates .html files that highlight Python overhead
python setup.py build_ext --inplace

# Open e.g. cytrim/scatter.html in your browser
# Yellow lines = Python overhead
# White lines = pure C code
```

### Performance profiling
```bash
# Using cProfile
python -m cProfile -s cumtime benchmark.py 1000

# Using line_profiler (supports .pyx files)
kernprof -l -v benchmark.py
```

## Common Issues

### "ModuleNotFoundError: No module named 'cytrim.estop'"
Root cause: Cython modules were not compiled.

Fix:
```bash
./build_cython.sh
```

### Build error: "error: Microsoft Visual C++ 14.0 or greater is required"
Root cause: missing C compiler on Windows.

Fix:
- Install the Visual Studio Build Tools
- Or run in pure Python mode (automatic fallback)

### Build error: "gcc: command not found"
Root cause: missing C compiler on Linux.

Fix:
```bash
sudo apt install build-essential python3-dev  # Debian/Ubuntu
sudo yum install gcc python3-devel            # RedHat/CentOS
```

### "ImportError: numpy._core.multiarray failed to import"
Root cause: NumPy version mismatch.

Fix:
```bash
pip install --upgrade numpy
python setup.py build_ext --inplace
```

## Future Work

### Additional optimization opportunities

1. **OpenMP parallelization**
   - Parallelize the per-ion loop
   - Potential: additional 4-8x speedup

2. **Memory views instead of NumPy arrays**
   - Faster array access inside tight loops
   - Potential: 10-20% improvement

3. **Custom random number generator**
   - Replace Python `random` with a C-level RNG
   - Potential: 5-10% improvement

4. **GPU acceleration (CUDA/OpenCL)**
   - Massive parallelization for large simulations
   - Potential: 100-1000x for large workloads

## Comparison with Other Technologies

| Technology | Speedup | Effort | Portability |
|------------|---------|--------|-------------|
| Pure Python | 1.0x | - | Excellent |
| **Cython** | **6.4x** | Medium | Good |
| Numba JIT | 3-5x | Low | Good |
| PyPy | 2-4x | Very low | Medium |
| C++ (pybind11) | 8-15x | High | Medium |
| CUDA/OpenCL | 100-1000x | Very high | Low |

**Why Cython?**
- Strong balance between performance and engineering effort
- Full control over optimization strategy
- Seamless integration with existing Python code
- Supports automatic fallback
- Broad platform coverage

## Benchmarking Tools

### Quick test
```bash
python benchmark.py 1000
```

### Comparison
```bash
python compare_performance.py
```

### Detailed profiling with cProfile
```bash
python -m cProfile -o profile.stats benchmark.py 1000
python -m pstats profile.stats
# In the pstats prompt:
stats 20
```

## Summary

Cython acceleration for CyTRIM delivers:
- 6.4x faster execution than pure Python
- Identical API and user interface
- Automatic fallback when builds fail
- Lightweight build pipeline
- No GUI changes required
- Transparent integration for users

Recommendation: whenever a C compiler is available, run CyTRIM with Cython enabled.
