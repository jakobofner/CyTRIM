"""Core simulation class for PyTRIM.

This module provides a clean interface to run TRIM simulations with
configurable parameters.

Automatically uses Cython-optimized modules if available, otherwise
falls back to pure Python implementation.

Supports optional OpenMP parallelization for multi-core speedup.
"""
from math import sqrt
import time
import numpy as np
import os

# Module references that can be switched at runtime
select_recoil = None
scatter = None
estop = None
geometry = None
trajectory = None
simulation_parallel = None

_using_cython = False
_cython_available = False
_force_python = False
_parallel_available = False
_use_parallel = False

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

# Check if parallel module is available
try:
    import cytrim.simulation_parallel
    _parallel_available = True
except ImportError:
    _parallel_available = False

def _load_cython_modules():
    """Load Cython-optimized modules."""
    global select_recoil, scatter, estop, geometry, trajectory, simulation_parallel, _using_cython
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
    
    # Try to load parallel module
    if _parallel_available:
        try:
            from cytrim import simulation_parallel as sp
            simulation_parallel = sp
        except ImportError:
            pass
    
    _using_cython = True

def _load_python_modules():
    """Load pure Python modules."""
    global select_recoil, scatter, estop, geometry, trajectory, simulation_parallel, _using_cython
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
    simulation_parallel = None  # No parallel support in Python mode
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

def set_use_parallel(use_parallel):
    """Enable or disable OpenMP parallelization.
    
    Parameters:
        use_parallel (bool): True to use parallel execution (requires Cython + OpenMP)
        
    Returns:
        bool: True if requested mode is now active, False if not possible
    """
    global _use_parallel
    
    if use_parallel:
        if _parallel_available and _using_cython:
            _use_parallel = True
            print("✓ Enabled OpenMP parallelization")
            return True
        elif not _using_cython:
            print("✗ Parallelization requires Cython - enable Cython first")
            return False
        else:
            print("✗ Parallel module not available - rebuild with OpenMP support")
            return False
    else:
        _use_parallel = False
        print("✓ Disabled parallelization")
        return True

def is_cython_available():
    """Check if Cython modules are available.
    
    Returns:
        bool: True if Cython modules can be imported
    """
    return _cython_available

def is_using_cython():
    """Check if currently using Cython modules.
    
    Returns:
        bool: True if Cython modules are active
    """
    return _using_cython

def is_parallel_available():
    """Check if OpenMP parallelization is available.
    
    Returns:
        bool: True if parallel module can be imported
    """
    return _parallel_available

def is_using_parallel():
    """Check if currently using parallelization.
    
    Returns:
        bool: True if parallel execution is enabled
    """
    return _use_parallel

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
        
        # Target geometry (A) - Simple planar geometry (backward compatible)
        self.zmin = 0.0
        self.zmax = 4000.0
        
        # Advanced 3D geometry settings
        self.geometry_type = 'planar'  # 'planar', 'box', 'cylinder', 'sphere', 'multilayer'
        self.geometry_params = {}  # Additional parameters for complex geometries
        # Examples:
        # For 'box': {'x_min': -500, 'x_max': 500, 'y_min': -500, 'y_max': 500, 'z_min': 0, 'z_max': 4000}
        # For 'cylinder': {'radius': 300, 'z_min': 0, 'z_max': 1000, 'center_x': 0, 'center_y': 0}
        # For 'sphere': {'radius': 500, 'center_x': 0, 'center_y': 0, 'center_z': 500}
        # For 'multilayer': {'layer_z_positions': [0, 100, 300, 500]}
        
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
        
        # 3D distribution data
        self.stopped_positions = []  # List of (x, y, z) tuples for stopped ions
        self.mean_x = 0.0
        self.mean_y = 0.0
        self.std_x = 0.0
        self.std_y = 0.0
        self.mean_r = 0.0  # Radial mean (distance from z-axis)
        self.std_r = 0.0   # Radial standard deviation
    
    # Properties for backward compatibility with export functions
    @property
    def nion(self):
        """Alias for total_ions (backward compatibility)."""
        return self.total_ions
    
    @property
    def stopped(self):
        """Number of ions stopped inside target."""
        return self.count_inside
    
    @property
    def backscattered(self):
        """Number of backscattered ions (not tracked yet)."""
        return 0
    
    @property
    def transmitted(self):
        """Number of transmitted ions."""
        return self.total_ions - self.count_inside
    
    @property
    def mean_depth(self):
        """Alias for mean_z (backward compatibility)."""
        return self.mean_z
    
    @property
    def std_depth(self):
        """Alias for std_z (backward compatibility)."""
        return self.std_z
        
    def get_summary(self):
        """Get a summary string of the results."""
        summary = []
        summary.append(f"Number of ions stopped inside the target: {self.count_inside} / {self.total_ions}")
        if self.count_inside > 0:
            summary.append(f"\n3D Distribution Statistics:")
            summary.append(f"  Mean position (x, y, z): ({self.mean_x:.2f}, {self.mean_y:.2f}, {self.mean_z:.2f}) A")
            summary.append(f"  Std deviation (x, y, z): ({self.std_x:.2f}, {self.std_y:.2f}, {self.std_z:.2f}) A")
            summary.append(f"  Radial spread (mean ± std): {self.mean_r:.2f} ± {self.std_r:.2f} A")
            summary.append(f"\nLegacy (z-only) Statistics:")
            summary.append(f"  Mean penetration depth: {self.mean_z:.2f} A")
            summary.append(f"  Standard deviation: {self.std_z:.2f} A")
        summary.append(f"\nSimulation time: {self.simulation_time:.2f} seconds")
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
        
    def _create_geometry(self):
        """Create geometry object based on parameters."""
        try:
            # Try to use geometry3d module (new system)
            if _using_cython:
                from cytrim import geometry3d
            else:
                from . import geometry3d
            
            # Create geometry based on type
            if self.params.geometry_type == 'planar':
                # Use simple planar geometry (backward compatible)
                return geometry3d.create_geometry('planar',
                    z_min=self.params.zmin, z_max=self.params.zmax)
            else:
                # Use advanced geometry with custom parameters
                # Add z_min and z_max if needed by the geometry type
                params_dict = self.params.geometry_params.copy()
                if params_dict.pop('needs_z_bounds', False):
                    params_dict['z_min'] = self.params.zmin
                    params_dict['z_max'] = self.params.zmax
                return geometry3d.create_geometry(
                    self.params.geometry_type, **params_dict)
        except ImportError:
            # Fallback: use old geometry module with simple planar setup
            print("Warning: geometry3d not available, using legacy planar geometry")
            geometry.setup(self.params.zmin, self.params.zmax)
            return None
    
    def setup(self):
        """Setup all modules with current parameters."""
        select_recoil.setup(self.params.density)
        scatter.setup(self.params.z1, self.params.m1, 
                     self.params.z2, self.params.m2)
        estop.setup(self.params.corr_lindhard, self.params.z1, 
                   self.params.m1, self.params.z2, self.params.density)
        
        # Setup geometry (new or legacy)
        self.geometry_obj = self._create_geometry()
        if self.geometry_obj is None:
            # Legacy mode: geometry.setup() already called in _create_geometry
            pass
        else:
            # New mode: setup geometry3d module with object
            try:
                if _using_cython:
                    from cytrim import geometry3d
                else:
                    from . import geometry3d
                geometry3d.setup_geometry(self.geometry_obj)
            except ImportError:
                pass
        
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
        
        # Use parallel execution if enabled and available
        if _use_parallel and simulation_parallel is not None and self.params.geometry_type == 'planar':
            # Parallel mode only supports planar geometry (for now)
            # Advanced geometries need full module setup in each worker process
            
            # Get number of threads from environment or use default
            num_threads = int(os.environ.get('OMP_NUM_THREADS', 0))
            
            # Prepare geometry information for worker processes
            geometry_info = ('planar', {'z_min': self.params.zmin, 'z_max': self.params.zmax})
            
            # Run parallel simulation with progress callback and geometry info
            stopped_positions, stopped_depths, trajectories, count_inside = \
                simulation_parallel.run_parallel_simulation(
                    pos_init, dir_init, self.params.e_init,
                    self.params.nion, record_trajectories, max_trajectories,
                    num_threads, self._progress_callback, geometry_info
                )
            
            # Store results and skip sequential execution
            self.results.count_inside = count_inside
            self.results.stopped_positions = stopped_positions
            self.results.stopped_depths = stopped_depths
            if trajectories is not None:
                self.results.trajectories = trajectories
            
            # Calculate statistics from collected results
            if count_inside > 0:
                n = count_inside
                for x, y, z in stopped_positions:
                    self.results.mean_x += x
                    self.results.mean_y += y
                    self.results.mean_z += z
                    self.results.std_x += x**2
                    self.results.std_y += y**2
                    self.results.std_z += z**2
                    r = sqrt(x**2 + y**2)
                    self.results.mean_r += r
                    self.results.std_r += r**2
            
            # Calculate simulation time before returning
            end_time = time.time()
            self.results.simulation_time = end_time - start_time
            
            return self.results  # Return early to skip sequential code
        
        # If parallel not used or geometry not planar, show info message
        if _use_parallel and simulation_parallel is not None and self.params.geometry_type != 'planar':
            print(f"ℹ️ Info: Parallel mode only supports planar geometry.")
            print(f"  Running '{self.params.geometry_type}' geometry in sequential mode.")
        
        # Sequential execution (original code or fallback)
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
                
                # Store full 3D position for advanced analysis
                self.results.stopped_positions.append((pos[0], pos[1], pos[2]))
                
                # Accumulate for 3D statistics
                self.results.mean_x += pos[0]
                self.results.mean_y += pos[1]
                self.results.std_x += pos[0]**2
                self.results.std_y += pos[1]**2
                
                # Radial distance from z-axis
                r = sqrt(pos[0]**2 + pos[1]**2)
                self.results.mean_r += r
                self.results.std_r += r**2
                
            if record_trajectories and i < max_trajectories and traj is not None:
                self.results.trajectories.append(traj)
            
            # Progress callback
            if self._progress_callback is not None:
                self._progress_callback(i + 1, self.params.nion)
        
        # Calculate statistics
        if self.results.count_inside > 0:
            n = self.results.count_inside
            
            # Z statistics (backward compatible)
            self.results.mean_z /= n
            self.results.std_z = sqrt(self.results.std_z / n - self.results.mean_z**2)
            
            # X, Y statistics
            self.results.mean_x /= n
            self.results.mean_y /= n
            self.results.std_x = sqrt(self.results.std_x / n - self.results.mean_x**2)
            self.results.std_y = sqrt(self.results.std_y / n - self.results.mean_y**2)
            
            # Radial statistics
            self.results.mean_r /= n
            self.results.std_r = sqrt(self.results.std_r / n - self.results.mean_r**2)
        
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
