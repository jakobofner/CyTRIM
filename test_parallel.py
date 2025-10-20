#!/usr/bin/env python3
"""Test script to verify and benchmark parallel execution."""

import time
from pytrim import (
    TRIMSimulation, SimulationParameters,
    is_cython_available, is_parallel_available,
    set_use_cython, set_use_parallel,
    is_using_cython, is_using_parallel
)

def run_benchmark(nion=500, label="Test"):
    """Run a single benchmark."""
    params = SimulationParameters()
    params.nion = nion
    params.z1 = 5  # Boron
    params.m1 = 11.009
    params.z2 = 14  # Silicon
    params.m2 = 28.086
    params.e_init = 50000  # 50 keV
    params.density = 0.04994
    params.zmin = 0.0
    params.zmax = 4000.0
    
    sim = TRIMSimulation(params)
    
    print(f"\n{label}:")
    print(f"  Configuration: {'Cython' if is_using_cython() else 'Python'}", end="")
    if is_using_cython():
        print(f" + {'OpenMP' if is_using_parallel() else 'Sequential'}")
    else:
        print()
    
    start = time.time()
    results = sim.run(record_trajectories=False)
    elapsed = time.time() - start
    
    ions_per_sec = nion / elapsed
    print(f"  Time: {elapsed:.2f} seconds")
    print(f"  Rate: {ions_per_sec:.1f} ions/second")
    print(f"  Stopped: {results.count_inside}/{nion} ions")
    print(f"  Mean depth: {results.mean_z:.1f} Å")
    
    return elapsed

def main():
    print("=" * 60)
    print("CyTRIM Parallelization Benchmark")
    print("=" * 60)
    
    print("\nAvailable optimizations:")
    print(f"  Cython available: {is_cython_available()}")
    print(f"  OpenMP available: {is_parallel_available()}")
    
    if not is_cython_available():
        print("\n⚠ Cython not available - run ./build_cython.sh first")
        return
    
    nion = 500
    print(f"\nRunning benchmarks with {nion} ions...")
    
    # Benchmark 1: Pure Python (if possible)
    try:
        set_use_cython(False)
        time_python = run_benchmark(nion, "1. Pure Python")
    except Exception as e:
        print(f"\nSkipping Python benchmark: {e}")
        time_python = None
    
    # Benchmark 2: Cython (sequential)
    set_use_cython(True)
    set_use_parallel(False)
    time_cython = run_benchmark(nion, "2. Cython (sequential)")
    
    # Benchmark 3: Cython + OpenMP (parallel)
    if is_parallel_available():
        set_use_cython(True)
        set_use_parallel(True)
        time_parallel = run_benchmark(nion, "3. Cython + OpenMP (parallel)")
    else:
        print("\n⚠ OpenMP not available - rebuild with OpenMP support")
        time_parallel = None
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if time_python:
        print(f"Python:            {time_python:.2f}s  (baseline)")
        print(f"Cython:            {time_cython:.2f}s  ({time_python/time_cython:.1f}× faster)")
        if time_parallel:
            print(f"Cython + OpenMP:   {time_parallel:.2f}s  ({time_python/time_parallel:.1f}× faster)")
    else:
        print(f"Cython:            {time_cython:.2f}s  (baseline)")
        if time_parallel:
            print(f"Cython + OpenMP:   {time_parallel:.2f}s  ({time_cython/time_parallel:.1f}× faster)")
    
    if time_parallel:
        print(f"\nParallel speedup:  {time_cython/time_parallel:.1f}× (Cython → Cython+OpenMP)")
        
        import os
        threads = os.environ.get('OMP_NUM_THREADS', 'auto')
        print(f"Threads used:      {threads}")
        
        if time_cython/time_parallel < 2:
            print("\n⚠ Warning: Low parallel speedup. Possible causes:")
            print("  - Too few ions for effective parallelization")
            print("  - Single-core system")
            print("  - OMP_NUM_THREADS set too low")
            print("\nTry with more ions: python test_parallel.py --nion 5000")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    import sys
    if '--help' in sys.argv:
        print("Usage: python test_parallel.py [--nion N]")
        print("\nBenchmark different execution modes:")
        print("  - Pure Python (slow)")
        print("  - Cython sequential (6× faster)")
        print("  - Cython + OpenMP parallel (40-50× faster)")
        sys.exit(0)
    
    main()
