#!/usr/bin/env python
"""Compare Python vs Cython performance."""
import time
import os
import glob
import shutil

def run_benchmark(use_cython=True, n_ions=100):
    """Run benchmark with or without Cython."""
    # Move Cython .so files if we want pure Python
    so_files = glob.glob("cytrim/*.so")
    backup_dir = "cytrim/.backup_so"
    
    if not use_cython and so_files:
        print("Temporarily disabling Cython modules...")
        os.makedirs(backup_dir, exist_ok=True)
        for f in so_files:
            shutil.move(f, backup_dir)
    
    # Clear import cache
    import sys
    modules_to_remove = [k for k in sys.modules.keys() if k.startswith('pytrim') or k.startswith('cytrim')]
    for mod in modules_to_remove:
        del sys.modules[mod]
    
    # Import fresh
    from pytrim.simulation import TRIMSimulation, SimulationParameters, is_using_cython
    
    print(f"\n{'='*60}")
    print(f"Benchmark: {'Cython' if use_cython else 'Pure Python'}")
    print(f"Number of ions: {n_ions}")
    print(f"Using Cython: {is_using_cython()}")
    print(f"{'='*60}\n")
    
    params = SimulationParameters()
    params.nion = n_ions
    
    sim = TRIMSimulation(params)
    
    start = time.time()
    results = sim.run()
    end = time.time()
    
    elapsed = end - start
    
    print(f"\nResults:")
    print(f"  Stopped inside: {results.count_inside}/{results.total_ions}")
    print(f"  Mean depth: {results.mean_z:.1f} Å")
    print(f"  Simulation time: {elapsed:.3f} seconds")
    print(f"  Performance: {n_ions/elapsed:.1f} ions/second")
    print(f"  Time per ion: {elapsed/n_ions*1000:.2f} ms")
    
    # Restore Cython files
    if not use_cython and so_files:
        print("\nRestoring Cython modules...")
        for f in os.listdir(backup_dir):
            shutil.move(os.path.join(backup_dir, f), "cytrim/")
        os.rmdir(backup_dir)
    
    return elapsed

if __name__ == '__main__':
    n_ions = 500  # Smaller number for comparison
    
    print("\n" + "="*60)
    print("PyTRIM Performance Comparison")
    print("="*60)
    
    # Run Python version
    time_python = run_benchmark(use_cython=False, n_ions=n_ions)
    
    # Run Cython version
    time_cython = run_benchmark(use_cython=True, n_ions=n_ions)
    
    # Summary
    speedup = time_python / time_cython
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Pure Python: {time_python:.3f} seconds")
    print(f"Cython:      {time_cython:.3f} seconds")
    print(f"Speedup:     {speedup:.2f}x faster with Cython!")
    print(f"{'='*60}\n")
