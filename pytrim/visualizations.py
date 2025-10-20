"""Advanced visualization functions for TRIM simulation results.

This module provides additional plot types:
- 2D density heatmaps
- Energy loss vs depth
- Radial distribution
- Contour plots
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.ndimage import gaussian_filter


class HeatmapCanvas(FigureCanvas):
    """Canvas for 2D density heatmaps."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
    
    def clear(self):
        """Clear all axes."""
        self.fig.clear()
    
    def plot_density_heatmap_xz(self, stopped_positions, zmin, zmax,
                                bins=50, smooth_sigma=1.0):
        """Plot 2D density heatmap in x-z plane.
        
        Parameters:
            stopped_positions: List of (x, y, z) positions
            zmin, zmax: Target boundaries
            bins: Number of bins for histogram
            smooth_sigma: Gaussian smoothing sigma
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        if not stopped_positions:
            ax.text(0.5, 0.5, 'Keine Daten verfügbar',
                   ha='center', va='center', transform=ax.transAxes)
            self.draw()
            return
        
        positions = np.array(stopped_positions)
        x = positions[:, 0]
        z = positions[:, 2]
        
        # Create 2D histogram
        h, xedges, zedges = np.histogram2d(x, z, bins=bins)
        
        # Apply Gaussian smoothing
        if smooth_sigma > 0:
            h = gaussian_filter(h, sigma=smooth_sigma)
        
        # Plot heatmap
        extent = [zedges[0], zedges[-1], xedges[0], xedges[-1]]
        im = ax.imshow(h, extent=extent, origin='lower', aspect='auto',
                      cmap='hot', interpolation='bilinear')
        
        # Colorbar
        cbar = self.fig.colorbar(im, ax=ax)
        cbar.set_label('Ion-Dichte', rotation=270, labelpad=20)
        
        # Target boundaries
        ax.axvline(zmin, color='cyan', linestyle='--', alpha=0.5, label='Target')
        ax.axvline(zmax, color='cyan', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Tiefe z (Å)')
        ax.set_ylabel('Laterale Position x (Å)')
        ax.set_title('2D Dichte-Heatmap (x-z Projektion)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_density_heatmap_yz(self, stopped_positions, zmin, zmax,
                                bins=50, smooth_sigma=1.0):
        """Plot 2D density heatmap in y-z plane.
        
        Parameters:
            stopped_positions: List of (x, y, z) positions
            zmin, zmax: Target boundaries
            bins: Number of bins for histogram
            smooth_sigma: Gaussian smoothing sigma
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        if not stopped_positions:
            ax.text(0.5, 0.5, 'Keine Daten verfügbar',
                   ha='center', va='center', transform=ax.transAxes)
            self.draw()
            return
        
        positions = np.array(stopped_positions)
        y = positions[:, 1]
        z = positions[:, 2]
        
        # Create 2D histogram
        h, yedges, zedges = np.histogram2d(y, z, bins=bins)
        
        # Apply Gaussian smoothing
        if smooth_sigma > 0:
            h = gaussian_filter(h, sigma=smooth_sigma)
        
        # Plot heatmap
        extent = [zedges[0], zedges[-1], yedges[0], yedges[-1]]
        im = ax.imshow(h, extent=extent, origin='lower', aspect='auto',
                      cmap='hot', interpolation='bilinear')
        
        # Colorbar
        cbar = self.fig.colorbar(im, ax=ax)
        cbar.set_label('Ion-Dichte', rotation=270, labelpad=20)
        
        # Target boundaries
        ax.axvline(zmin, color='cyan', linestyle='--', alpha=0.5, label='Target')
        ax.axvline(zmax, color='cyan', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Tiefe z (Å)')
        ax.set_ylabel('Laterale Position y (Å)')
        ax.set_title('2D Dichte-Heatmap (y-z Projektion)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_density_heatmap_xy(self, stopped_positions, depth_range=None, bins=50):
        """Plot 2D density heatmap in x-y plane (beam cross-section).
        
        Parameters:
            stopped_positions: List of (x, y, z) positions
            depth_range: Tuple (z_min, z_max) to filter positions, or None for all
            bins: Number of bins for histogram
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        if not stopped_positions:
            ax.text(0.5, 0.5, 'Keine Daten verfügbar',
                   ha='center', va='center', transform=ax.transAxes)
            self.draw()
            return
        
        positions = np.array(stopped_positions)
        
        # Filter by depth if specified
        if depth_range is not None:
            z_min, z_max = depth_range
            mask = (positions[:, 2] >= z_min) & (positions[:, 2] <= z_max)
            positions = positions[mask]
            
            if len(positions) == 0:
                ax.text(0.5, 0.5, f'Keine Ionen in Tiefe {z_min:.0f}-{z_max:.0f} Å',
                       ha='center', va='center', transform=ax.transAxes)
                self.draw()
                return
        
        x = positions[:, 0]
        y = positions[:, 1]
        
        # Create 2D histogram
        h, xedges, yedges = np.histogram2d(x, y, bins=bins)
        h = gaussian_filter(h, sigma=1.0)
        
        # Plot heatmap
        extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
        im = ax.imshow(h, extent=extent, origin='lower', aspect='equal',
                      cmap='hot', interpolation='bilinear')
        
        # Colorbar
        cbar = self.fig.colorbar(im, ax=ax)
        cbar.set_label('Ion-Dichte', rotation=270, labelpad=20)
        
        ax.set_xlabel('y (Å)')
        ax.set_ylabel('x (Å)')
        
        if depth_range:
            ax.set_title(f'Strahl-Querschnitt bei z={depth_range[0]:.0f}-{depth_range[1]:.0f} Å')
        else:
            ax.set_title('Strahl-Querschnitt (x-y Projektion)')
        
        ax.grid(True, alpha=0.3)
        
        # Add circular contours for reference
        if len(positions) > 10:
            r_std = np.std(np.sqrt(x**2 + y**2))
            circle = plt.Circle((0, 0), r_std, fill=False, color='cyan',
                              linestyle='--', alpha=0.5, label=f'σ_r = {r_std:.1f} Å')
            ax.add_patch(circle)
            ax.legend()
        
        self.fig.tight_layout()
        self.draw()


class EnergyLossCanvas(FigureCanvas):
    """Canvas for energy loss visualization."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
    
    def clear(self):
        """Clear all axes."""
        self.fig.clear()
    
    def plot_energy_vs_depth(self, trajectories, zmin, zmax):
        """Plot energy vs depth for trajectories.
        
        Parameters:
            trajectories: List of trajectory arrays [(x, y, z, e), ...]
            zmin, zmax: Target boundaries
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        if not trajectories:
            ax.text(0.5, 0.5, 'Keine Trajektorien verfügbar',
                   ha='center', va='center', transform=ax.transAxes)
            self.draw()
            return
        
        # Plot each trajectory
        for i, traj in enumerate(trajectories):
            traj = np.array(traj)
            z = traj[:, 2]
            e = traj[:, 3]
            
            ax.plot(z, e / 1000, alpha=0.6, linewidth=1)
        
        # Target boundaries
        ax.axvline(zmin, color='red', linestyle='--', alpha=0.5, label='Target Grenzen')
        ax.axvline(zmax, color='red', linestyle='--', alpha=0.5)
        
        ax.set_xlabel('Tiefe z (Å)')
        ax.set_ylabel('Energie (keV)')
        ax.set_title('Energie-Verlust vs. Tiefe')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_stopping_power(self, trajectories, bins=50):
        """Plot average stopping power vs depth.
        
        Parameters:
            trajectories: List of trajectory arrays
            bins: Number of depth bins
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        if not trajectories:
            ax.text(0.5, 0.5, 'Keine Trajektorien verfügbar',
                   ha='center', va='center', transform=ax.transAxes)
            self.draw()
            return
        
        # Calculate dE/dz for each trajectory
        all_z = []
        all_dedz = []
        
        for traj in trajectories:
            traj = np.array(traj)
            if len(traj) < 2:
                continue
                
            z = traj[:, 2]
            e = traj[:, 3]
            
            # Calculate dE/dz
            dz = np.diff(z)
            de = np.diff(e)
            
            # Avoid division by zero
            mask = np.abs(dz) > 1e-10
            if np.any(mask):
                dedz = -de[mask] / dz[mask]  # Negative because energy decreases
                z_mid = (z[:-1][mask] + z[1:][mask]) / 2
                
                all_z.extend(z_mid)
                all_dedz.extend(dedz)
        
        if not all_z:
            ax.text(0.5, 0.5, 'Keine Stopping Power Daten',
                   ha='center', va='center', transform=ax.transAxes)
            self.draw()
            return
        
        # Bin and average
        all_z = np.array(all_z)
        all_dedz = np.array(all_dedz)
        
        # Remove outliers (>99th percentile)
        p99 = np.percentile(all_dedz, 99)
        mask = all_dedz < p99
        all_z = all_z[mask]
        all_dedz = all_dedz[mask]
        
        # Create bins
        z_bins = np.linspace(all_z.min(), all_z.max(), bins)
        bin_indices = np.digitize(all_z, z_bins)
        
        z_avg = []
        dedz_avg = []
        dedz_std = []
        
        for i in range(1, len(z_bins)):
            mask = bin_indices == i
            if np.any(mask):
                z_avg.append(z_bins[i-1] + (z_bins[i] - z_bins[i-1]) / 2)
                dedz_avg.append(np.mean(all_dedz[mask]))
                dedz_std.append(np.std(all_dedz[mask]))
        
        z_avg = np.array(z_avg)
        dedz_avg = np.array(dedz_avg)
        dedz_std = np.array(dedz_std)
        
        # Plot
        ax.plot(z_avg, dedz_avg, 'b-', linewidth=2, label='Mittelwert')
        ax.fill_between(z_avg, dedz_avg - dedz_std, dedz_avg + dedz_std,
                        alpha=0.3, label='±1σ')
        
        ax.set_xlabel('Tiefe z (Å)')
        ax.set_ylabel('Stopping Power dE/dz (eV/Å)')
        ax.set_title('Stopping Power Profil')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()


class RadialDistributionCanvas(FigureCanvas):
    """Canvas for radial distribution analysis."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
    
    def clear(self):
        """Clear all axes."""
        self.fig.clear()
    
    def plot_radial_vs_depth(self, stopped_positions, bins=30):
        """Plot radial distance vs depth.
        
        Parameters:
            stopped_positions: List of (x, y, z) positions
            bins: Number of depth bins
        """
        self.clear()
        ax = self.fig.add_subplot(111)
        
        if not stopped_positions:
            ax.text(0.5, 0.5, 'Keine Daten verfügbar',
                   ha='center', va='center', transform=ax.transAxes)
            self.draw()
            return
        
        positions = np.array(stopped_positions)
        x = positions[:, 0]
        y = positions[:, 1]
        z = positions[:, 2]
        r = np.sqrt(x**2 + y**2)
        
        # Scatter plot
        ax.scatter(z, r, alpha=0.5, s=10, label='Ionen')
        
        # Binned average
        z_bins = np.linspace(z.min(), z.max(), bins)
        bin_indices = np.digitize(z, z_bins)
        
        z_avg = []
        r_avg = []
        r_std = []
        
        for i in range(1, len(z_bins)):
            mask = bin_indices == i
            if np.any(mask):
                z_avg.append(z_bins[i-1] + (z_bins[i] - z_bins[i-1]) / 2)
                r_avg.append(np.mean(r[mask]))
                r_std.append(np.std(r[mask]))
        
        z_avg = np.array(z_avg)
        r_avg = np.array(r_avg)
        r_std = np.array(r_std)
        
        # Plot average with error band
        ax.plot(z_avg, r_avg, 'r-', linewidth=2, label='Mittelwert')
        ax.fill_between(z_avg, r_avg - r_std, r_avg + r_std,
                        alpha=0.3, color='red', label='±1σ')
        
        ax.set_xlabel('Tiefe z (Å)')
        ax.set_ylabel('Radiale Distanz r (Å)')
        ax.set_title('Radiale Streuung vs. Tiefe')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()
