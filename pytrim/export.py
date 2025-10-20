"""Export functions for simulation results.

This module provides various export formats for TRIM simulation results:
- CSV: Tabular data for spreadsheet analysis
- JSON: Complete structured data
- VTK: 3D visualization in ParaView
- PNG: High-resolution plots
"""
import json
import csv
import numpy as np
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def export_to_csv(results, filepath: Path, include_trajectories: bool = True):
    """Export simulation results to CSV format.
    
    Parameters:
        results: SimulationResults object
        filepath: Output CSV file path
        include_trajectories: Include individual trajectory data
    """
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header information
        writer.writerow(['# CyTRIM Simulation Results'])
        writer.writerow(['# Total ions', results.nion])
        writer.writerow(['# Stopped ions', results.stopped])
        writer.writerow(['# Backscattered ions', results.backscattered])
        writer.writerow(['# Transmitted ions', results.transmitted])
        writer.writerow([])
        
        # Statistics
        writer.writerow(['# Statistics'])
        writer.writerow(['Mean depth (Å)', results.mean_depth])
        writer.writerow(['Std depth (Å)', results.std_depth])
        writer.writerow(['Mean x (Å)', results.mean_x])
        writer.writerow(['Std x (Å)', results.std_x])
        writer.writerow(['Mean y (Å)', results.mean_y])
        writer.writerow(['Std y (Å)', results.std_y])
        writer.writerow(['Mean radial (Å)', results.mean_r])
        writer.writerow(['Std radial (Å)', results.std_r])
        writer.writerow([])
        
        # Stopped ion positions
        writer.writerow(['# Stopped Ion Positions'])
        writer.writerow(['x (Å)', 'y (Å)', 'z (Å)', 'r (Å)'])
        
        if hasattr(results, 'stopped_positions') and results.stopped_positions:
            for pos in results.stopped_positions:
                x, y, z = pos
                r = np.sqrt(x**2 + y**2)
                writer.writerow([x, y, z, r])
        
        # Trajectory data (optional)
        if include_trajectories and hasattr(results, 'trajectories') and results.trajectories:
            writer.writerow([])
            writer.writerow(['# Trajectory Data'])
            writer.writerow(['Trajectory ID', 'Step', 'x (Å)', 'y (Å)', 'z (Å)', 'Energy (eV)'])
            
            for traj_id, traj in enumerate(results.trajectories):
                for step, (x, y, z, e) in enumerate(traj):
                    writer.writerow([traj_id, step, x, y, z, e])


def export_to_json(results, filepath: Path, include_trajectories: bool = True):
    """Export simulation results to JSON format.
    
    Parameters:
        results: SimulationResults object
        filepath: Output JSON file path
        include_trajectories: Include trajectory data
    """
    data = {
        'simulation': {
            'total_ions': int(results.nion),
            'stopped': int(results.stopped),
            'backscattered': int(results.backscattered),
            'transmitted': int(results.transmitted),
        },
        'statistics': {
            'mean_depth': float(results.mean_depth),
            'std_depth': float(results.std_depth),
            'mean_x': float(results.mean_x),
            'std_x': float(results.std_x),
            'mean_y': float(results.mean_y),
            'std_y': float(results.std_y),
            'mean_radial': float(results.mean_r),
            'std_radial': float(results.std_r),
        },
    }
    
    # Stopped positions
    if hasattr(results, 'stopped_positions') and results.stopped_positions:
        data['stopped_positions'] = [
            {'x': float(x), 'y': float(y), 'z': float(z)}
            for x, y, z in results.stopped_positions
        ]
    
    # Trajectories (optional)
    if include_trajectories and hasattr(results, 'trajectories') and results.trajectories:
        data['trajectories'] = [
            [
                {'x': float(x), 'y': float(y), 'z': float(z), 'energy': float(e)}
                for x, y, z, e in traj
            ]
            for traj in results.trajectories
        ]
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def export_to_vtk(results, filepath: Path):
    """Export simulation results to VTK format for ParaView.
    
    This creates a VTK PolyData file with stopped ion positions.
    
    Parameters:
        results: SimulationResults object
        filepath: Output VTK file path
    """
    if not hasattr(results, 'stopped_positions') or not results.stopped_positions:
        raise ValueError("No stopped positions to export")
    
    positions = np.array(results.stopped_positions)
    n_points = len(positions)
    
    with open(filepath, 'w') as f:
        # VTK header
        f.write("# vtk DataFile Version 3.0\n")
        f.write("CyTRIM Ion Implantation Results\n")
        f.write("ASCII\n")
        f.write("DATASET POLYDATA\n")
        
        # Points
        f.write(f"POINTS {n_points} float\n")
        for x, y, z in positions:
            f.write(f"{x} {y} {z}\n")
        
        # Vertices
        f.write(f"\nVERTICES {n_points} {n_points * 2}\n")
        for i in range(n_points):
            f.write(f"1 {i}\n")
        
        # Point data - radial distance
        f.write(f"\nPOINT_DATA {n_points}\n")
        f.write("SCALARS radial_distance float 1\n")
        f.write("LOOKUP_TABLE default\n")
        for x, y, z in positions:
            r = np.sqrt(x**2 + y**2)
            f.write(f"{r}\n")
        
        # Depth
        f.write("\nSCALARS depth float 1\n")
        f.write("LOOKUP_TABLE default\n")
        for x, y, z in positions:
            f.write(f"{z}\n")


def export_trajectories_to_vtk(trajectories, filepath: Path):
    """Export trajectories to VTK format as polylines.
    
    Parameters:
        trajectories: List of trajectory arrays
        filepath: Output VTK file path
    """
    if not trajectories:
        raise ValueError("No trajectories to export")
    
    # Collect all points and build line connectivity
    all_points = []
    lines = []
    point_offset = 0
    
    for traj in trajectories:
        n_points = len(traj)
        # Extract x, y, z
        traj_points = [(x, y, z) for x, y, z, e in traj]
        all_points.extend(traj_points)
        
        # Line connectivity: n_points, point_indices...
        line = [n_points] + list(range(point_offset, point_offset + n_points))
        lines.append(line)
        point_offset += n_points
    
    total_points = len(all_points)
    n_lines = len(lines)
    total_line_data = sum(len(line) for line in lines)
    
    with open(filepath, 'w') as f:
        # VTK header
        f.write("# vtk DataFile Version 3.0\n")
        f.write("CyTRIM Ion Trajectories\n")
        f.write("ASCII\n")
        f.write("DATASET POLYDATA\n")
        
        # Points
        f.write(f"POINTS {total_points} float\n")
        for x, y, z in all_points:
            f.write(f"{x} {y} {z}\n")
        
        # Lines
        f.write(f"\nLINES {n_lines} {total_line_data}\n")
        for line in lines:
            f.write(' '.join(map(str, line)) + '\n')


def export_figure_to_png(figure: Figure, filepath: Path, dpi: int = 300):
    """Export matplotlib figure to high-resolution PNG.
    
    Parameters:
        figure: Matplotlib Figure object
        filepath: Output PNG file path
        dpi: Resolution in dots per inch (default 300 for publication quality)
    """
    figure.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white')


def export_all_plots(canvas_list, base_filepath: Path, dpi: int = 300):
    """Export all plot canvases to PNG files.
    
    Parameters:
        canvas_list: List of (name, FigureCanvas) tuples
        base_filepath: Base path for output files (without extension)
        dpi: Resolution in dots per inch
    """
    for name, canvas in canvas_list:
        output_path = base_filepath.parent / f"{base_filepath.stem}_{name}.png"
        export_figure_to_png(canvas.fig, output_path, dpi)
