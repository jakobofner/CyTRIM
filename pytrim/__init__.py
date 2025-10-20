"""PyTRIM - Python implementation of TRIM.

Transport of Ions in Matter simulation package.
"""
from .simulation import TRIMSimulation, SimulationParameters, SimulationResults
from .simulation import (
    is_using_cython, is_cython_available, set_use_cython,
    is_using_parallel, is_parallel_available, set_use_parallel
)

# Import geometry3d module
try:
    from . import geometry3d
except ImportError:
    geometry3d = None

__version__ = '2.0.0'
__all__ = [
    'TRIMSimulation', 
    'SimulationParameters', 
    'SimulationResults',
    'is_using_cython',
    'is_cython_available',
    'set_use_cython',
    'is_using_parallel',
    'is_parallel_available',
    'set_use_parallel',
    'geometry3d'
]
