# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True

"""OpenMP-parallelized TRIM simulation using Cython."""

import numpy as np
cimport numpy as cnp
from cython.parallel import prange
cimport cython
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# Import Cython-optimized trajectory module
try:
    from cytrim import trajectory as traj_module
except ImportError:
    from pytrim import trajectory as traj_module

cnp.import_array()


def _run_ion_batch(args):
    """Run a single ion simulation (worker function for multiprocessing).
    
    Each worker process needs to set up its own geometry state.
    """
    pos_init, dir_init, e_init, geometry_setup_info = args
    
    # Import modules in worker process
    try:
        from cytrim import trajectory as traj_module
        from cytrim import geometry, select_recoil, scatter, estop
        using_cython = True
    except ImportError:
        from pytrim import trajectory as traj_module
        from pytrim import geometry, select_recoil, scatter, estop
        using_cython = False
    
    # Setup geometry in this worker process
    if geometry_setup_info is not None:
        geom_type, geom_params = geometry_setup_info
        
        if geom_type == 'planar':
            # Simple planar geometry
            geometry.setup(geom_params['z_min'], geom_params['z_max'])
        else:
            # Advanced 3D geometry
            try:
                if using_cython:
                    from cytrim import geometry3d
                else:
                    from pytrim import geometry3d
                
                geom_obj = geometry3d.create_geometry(geom_type, **geom_params)
                geometry3d.setup_geometry(geom_obj)
            except (ImportError, AttributeError):
                # Fallback to planar
                geometry.setup(geom_params.get('z_min', -10.0), geom_params.get('z_max', 0.0))
    
    # Run trajectory
    pos_stop, dir_stop, e_stop, inside = traj_module.trajectory(
        pos_init.copy(), dir_init.copy(), e_init
    )
    return (pos_stop, pos_stop[2], inside)


def run_parallel_simulation(
    object pos_init,
    object dir_init,
    double e_init,
    int nion,
    bint record_trajectories=False,
    int max_trajectories=100,
    int num_threads=0,
    object progress_callback=None,
    object geometry_info=None
):
    """Run parallel ion simulation using multiprocessing.
    
    Uses ProcessPoolExecutor for true parallelism (bypasses Python GIL).
    Automatically falls back to sequential for small workloads to avoid overhead.
    
    Args:
        progress_callback: Optional callback function(current, total) for progress updates
        geometry_info: Tuple of (geometry_type, geometry_params) for worker processes
    """
    if num_threads <= 0:
        num_threads = multiprocessing.cpu_count()
    
    stopped_positions = []
    stopped_depths = []
    trajectories = []
    count_inside = 0
    
    pos_arr = np.asarray(pos_init, dtype=np.float64)
    dir_arr = np.asarray(dir_init, dtype=np.float64)
    
    # Determine if parallelization is worth it
    # ProcessPoolExecutor has overhead (~50-100ms), so only use for larger workloads
    MIN_IONS_FOR_PARALLEL = 200  # Below this, overhead > benefit
    use_parallel = nion >= MIN_IONS_FOR_PARALLEL
    
    # Record trajectories for first few ions if requested
    if record_trajectories and max_trajectories > 0:
        for i in range(min(max_trajectories, nion)):
            pos_stop, dir_stop, e_stop, inside, traj_path = traj_module.trajectory_with_path(
                pos_arr.copy(), dir_arr.copy(), e_init, record_path=True
            )
            stopped_positions.append(pos_stop)
            stopped_depths.append(pos_stop[2])  # depth is z-coordinate
            trajectories.append(traj_path)
            if inside:
                count_inside += 1
            
            # Progress update
            if progress_callback is not None:
                progress_callback(i + 1, nion)
    
    # Run remaining ions using process pool for TRUE parallelism
    start_ion = len(trajectories)
    remaining = nion - start_ion
    
    if remaining > 0:
        if use_parallel and remaining >= MIN_IONS_FOR_PARALLEL:
            # Use ProcessPoolExecutor for true parallelism (bypasses GIL)
            # Pass geometry info to each worker process
            args_list = [(pos_arr, dir_arr, e_init, geometry_info) for _ in range(remaining)]
            
            with ProcessPoolExecutor(max_workers=num_threads) as executor:
                # Submit all tasks at once for maximum parallelism
                futures = {executor.submit(_run_ion_batch, args): idx 
                          for idx, args in enumerate(args_list)}
                
                # Collect results as they complete
                completed_count = 0
                for future in as_completed(futures):
                    try:
                        pos_stop, depth, inside = future.result()
                        stopped_positions.append(pos_stop)
                        stopped_depths.append(depth)
                        if inside:
                            count_inside += 1
                        
                        completed_count += 1
                        # Progress update every 10 ions or at end
                        if progress_callback is not None and (completed_count % 10 == 0 or completed_count == remaining):
                            progress_callback(start_ion + completed_count, nion)
                    except Exception as e:
                        print(f"Error in parallel ion: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Final progress update
                if progress_callback is not None:
                    progress_callback(nion, nion)
        else:
            # Sequential fallback for small workloads (avoids ProcessPool overhead)
            for i in range(remaining):
                pos_stop, dir_stop, e_stop, inside = traj_module.trajectory(
                    pos_arr.copy(), dir_arr.copy(), e_init
                )
                stopped_positions.append(pos_stop)
                stopped_depths.append(pos_stop[2])
                if inside:
                    count_inside += 1
                
                # Progress update
                if progress_callback is not None:
                    progress_callback(start_ion + i + 1, nion)
    
    return stopped_positions, stopped_depths, trajectories, count_inside
