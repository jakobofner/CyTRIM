"""Core simulation class for PyTRIM.

This module provides a clean interface to run TRIM simulations with
configurable parameters.

Automatically uses Cython-optimized modules if available, otherwise
falls back to pure Python implementation.
"""
from math import sqrt
import time
import numpy as np

# Module references that can be switched at runtime
select_recoil = None
scatter = None
estop = None
geometry = None
trajectory = None

_using_cython = False
_cython_available = False
_force_python = False

# Check if Cython modules are available
try:
    import cytrim.select_recoil
    import cytrim.scatter
    import cytrim.estop
    import cytrim.geometry
    import cytrim.trajectory
    _cython_available = True
except ImportError:
    _cython_available = False

def _load_cython_modules():
    """Load Cython-optimized modules."""
    global select_recoil, scatter, estop, geometry, trajectory, _using_cython
    from cytrim import select_recoil as sr
    from cytrim import scatter as sc
    from cytrim import estop as es
    from cytrim import geometry as geo
    from cytrim import trajectory as traj
    select_recoil = sr
    scatter = sc
    estop = es
    geometry = geo
    trajectory = traj
    _using_cython = True

def _load_python_modules():
    """Load pure Python modules."""
    global select_recoil, scatter, estop, geometry, trajectory, _using_cython
    from . import select_recoil as sr
    from . import scatter as sc
    from . import estop as es
    from . import geometry as geo
    from . import trajectory as traj
    select_recoil = sr
    scatter = sc
    estop = es
    geometry = geo
    trajectory = traj
    _using_cython = False

def set_use_cython(use_cython):
    """Enable or disable Cython modules.
    
    Parameters:
        use_cython (bool): True to use Cython (if available), False for Python
        
    Returns:
        bool: True if requested mode is now active, False if not possible
    """
    global _force_python
    
    if use_cython:
        if _cython_available:
            _force_python = False
            _load_cython_modules()
            print("✓ Switched to Cython-optimized modules")
            return True
        else:
            print("✗ Cython modules not available - staying with Python")
            return False
    else:
        _force_python = True
        _load_python_modules()
        print("✓ Switched to pure Python modules")
        return True

# Initialize with best available option
if _cython_available and not _force_python:
    _load_cython_modules()
    print("Using Cython-optimized modules for faster simulation!")
else:
    _load_python_modules()
    if not _cython_available:
        print("Using pure Python modules (compile Cython for better performance)")
    else:
        print("Using pure Python modules (Cython disabled by user)")


class SimulationParameters:
    """Container for simulation parameters."""
    
    def __init__(self):
        # Number of projectiles to simulate
        self.nion = 1000
        
        # Target geometry (A)
        self.zmin = 0.0
        self.zmax = 4000.0
        
        # Projectile properties
        self.z1 = 5              # atomic number
        self.m1 = 11.009         # mass (amu)
        
        # Target properties
        self.z2 = 14             # atomic number
        self.m2 = 28.086         # mass (amu)
        self.density = 0.04994   # atoms/A^3
        
        # Stopping power correction
        self.corr_lindhard = 1.5
        
        # Initial conditions of the projectile
        self.e_init = 50000.0    # energy (eV)
        self.x_init = 0.0        # position (A)
        self.y_init = 0.0
        self.z_init = 0.0
        self.dir_x = 0.0         # direction (unit vector)
        self.dir_y = 0.0
        self.dir_z = 1.0
        
    def get_pos_init(self):
        """Get initial position as numpy array."""
        return np.array([self.x_init, self.y_init, self.z_init])
    
    def get_dir_init(self):
        """Get initial direction as numpy array."""
        return np.array([self.dir_x, self.dir_y, self.dir_z])


class SimulationResults:
    """Container for simulation results."""
    
    def __init__(self):
        self.count_inside = 0
        self.mean_z = 0.0
        self.std_z = 0.0
        self.simulation_time = 0.0
        self.total_ions = 0
        self.stopped_depths = []  # List of z-coordinates where ions stopped
        self.trajectories = []    # List of trajectories (positions)
        
    def get_summary(self):
        """Get a summary string of the results."""
        summary = []
        summary.append(f"Number of ions stopped inside the target: {self.count_inside} / {self.total_ions}")
        if self.count_inside > 0:
            summary.append(f"Mean penetration depth: {self.mean_z:.2f} A")
            summary.append(f"Standard deviation: {self.std_z:.2f} A")
        summary.append(f"Simulation time: {self.simulation_time:.2f} seconds")
        return "\n".join(summary)


class TRIMSimulation:
    """Main simulation class."""
    
    def __init__(self, params=None):
        """Initialize simulation with given parameters.
        
        Parameters:
            params (SimulationParameters): Simulation parameters
        """
        self.params = params if params is not None else SimulationParameters()
        self.results = SimulationResults()
        self._progress_callback = None
        self._should_stop = False
        
    def set_progress_callback(self, callback):
        """Set callback function for progress updates.
        
        Parameters:
            callback: Function that takes (current, total) as arguments
        """
        self._progress_callback = callback
        
    def stop(self):
        """Request simulation to stop."""
        self._should_stop = True
        
    def setup(self):
        """Setup all modules with current parameters."""
        select_recoil.setup(self.params.density)
        scatter.setup(self.params.z1, self.params.m1, 
                     self.params.z2, self.params.m2)
        estop.setup(self.params.corr_lindhard, self.params.z1, 
                   self.params.m1, self.params.z2, self.params.density)
        geometry.setup(self.params.zmin, self.params.zmax)
        trajectory.setup()
        
    def run(self, record_trajectories=False, max_trajectories=10):
        """Run the simulation.
        
        Parameters:
            record_trajectories (bool): Whether to record trajectory paths
            max_trajectories (int): Maximum number of trajectories to record
            
        Returns:
            SimulationResults: Results of the simulation
        """
        self._should_stop = False
        start_time = time.time()
        
        # Setup modules
        self.setup()
        
        # Initialize results
        self.results = SimulationResults()
        self.results.total_ions = self.params.nion
        
        pos_init = self.params.get_pos_init()
        dir_init = self.params.get_dir_init()
        
        # Run simulation for each ion
        for i in range(self.params.nion):
            if self._should_stop:
                break
                
            pos, dir, e, is_inside, traj = trajectory.trajectory_with_path(
                pos_init, dir_init, self.params.e_init,
                record_path=(record_trajectories and i < max_trajectories)
            )
            
            if is_inside:
                self.results.count_inside += 1
                self.results.mean_z += pos[2]
                self.results.std_z += pos[2]**2
                self.results.stopped_depths.append(pos[2])
                
            if record_trajectories and i < max_trajectories and traj is not None:
                self.results.trajectories.append(traj)
            
            # Progress callback
            if self._progress_callback is not None:
                self._progress_callback(i + 1, self.params.nion)
        
        # Calculate statistics
        if self.results.count_inside > 0:
            self.results.mean_z /= self.results.count_inside
            self.results.std_z = sqrt(
                self.results.std_z / self.results.count_inside - 
                self.results.mean_z**2
            )
        
        end_time = time.time()
        self.results.simulation_time = end_time - start_time
        
        return self.results


def is_using_cython():
    """Check if Cython modules are being used.
    
    Returns:
        bool: True if using Cython, False if using pure Python
    """
    return _using_cython


def is_cython_available():
    """Check if Cython modules are available (even if not currently used).
    
    Returns:
        bool: True if Cython modules can be loaded
    """
    return _cython_available
