#!/usr/bin/env python
"""Benchmark script to compare Python vs Cython performance."""
import time
import sys
from pytrim.simulation import TRIMSimulation, SimulationParameters, is_using_cython

def benchmark(n_ions=1000):
    """Run benchmark with given number of ions."""
    params = SimulationParameters()
    params.nion = n_ions
    
    sim = TRIMSimulation(params)
    
    print(f"Running benchmark with {n_ions} ions...")
    print(f"Using {'Cython' if is_using_cython() else 'Python'} modules")
    print("-" * 50)
    
    start = time.time()
    results = sim.run()
    end = time.time()
    
    print(results.get_summary())
    print("-" * 50)
    
    ions_per_second = n_ions / (end - start)
    print(f"Performance: {ions_per_second:.1f} ions/second")
    print(f"Time per ion: {(end - start) / n_ions * 1000:.2f} ms")
    
    return end - start

if __name__ == '__main__':
    n = 1000
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    
    benchmark(n)
