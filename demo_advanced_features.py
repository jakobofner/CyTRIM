"""Demo script for advanced CyTRIM features.

This script demonstrates:
1. Material presets
2. Different geometry types
3. Export to multiple formats
4. Advanced visualizations (using matplotlib directly)
"""
import numpy as np
from pathlib import Path

# Import CyTRIM modules
from pytrim.simulation import TRIMSimulation, SimulationParameters
from pytrim.presets import get_preset_manager
from pytrim import export
import matplotlib.pyplot as plt


def demo_presets():
    """Demonstrate material presets."""
    print("="*60)
    print("DEMO 1: Material Presets")
    print("="*60)
    
    manager = get_preset_manager()
    
    print("\nVerfügbare Presets:")
    for name in manager.get_preset_names():
        preset = manager.get_preset(name)
        print(f"  - {name}: {preset.description}")
    
    # Load B in Si preset
    print("\nLade 'B in Si' Preset...")
    preset = manager.get_preset("B in Si")
    
    print(f"\nPreset Details:")
    print(f"  Projektil: {preset.element1} (Z={preset.z1}, M={preset.m1} amu)")
    print(f"  Target: {preset.element2} (Z={preset.z2}, M={preset.m2} amu)")
    print(f"  Energie: {preset.energy:.0f} eV")
    print(f"  Dichte: {preset.density:.5f} atoms/Å³")
    
    # Create simulation from preset
    params = SimulationParameters()
    params.nion = 100  # Small for demo
    params.z1 = preset.z1
    params.m1 = preset.m1
    params.z2 = preset.z2
    params.m2 = preset.m2
    params.density = preset.density
    params.e_init = preset.energy
    params.corr_lindhard = preset.corr_lindhard
    params.zmin = preset.zmin
    params.zmax = preset.zmax
    
    print(f"\nStarte Simulation mit {params.nion} Ionen...")
    sim = TRIMSimulation(params)
    results = sim.run(record_trajectories=False)
    
    print(f"\nErgebnisse:")
    print(f"  Gestoppt: {results.count_inside}/{results.total_ions}")
    print(f"  Mittlere Tiefe: {results.mean_z:.1f} ± {results.std_z:.1f} Å")
    print(f"  Laterale Streuung: {results.mean_r:.1f} ± {results.std_r:.1f} Å")
    

def demo_geometries():
    """Demonstrate different geometry types."""
    print("\n" + "="*60)
    print("DEMO 2: Verschiedene Geometrien")
    print("="*60)
    
    geometries = [
        ("planar", {}),
        ("box", {'x_min': -500, 'x_max': 500, 'y_min': -500, 'y_max': 500, 
                 'z_min': 0, 'z_max': 4000}),
        ("cylinder", {'radius': 500, 'z_min': 0, 'z_max': 4000}),
        ("sphere", {'radius': 500, 'center': (0, 0, 2000)}),
    ]
    
    base_params = SimulationParameters()
    base_params.nion = 100
    base_params.z1 = 5  # B
    base_params.m1 = 11.009
    base_params.z2 = 14  # Si
    base_params.m2 = 28.086
    base_params.density = 0.04994
    base_params.e_init = 50000
    base_params.corr_lindhard = 1.5
    base_params.zmin = 0
    base_params.zmax = 4000
    
    for geom_type, geom_params in geometries:
        print(f"\n--- Geometrie: {geom_type.upper()} ---")
        
        # Create new params with same values
        import copy
        params = copy.deepcopy(base_params)
        params.geometry_type = geom_type
        params.geometry_params = geom_params
        
        if geom_params:
            print(f"Parameter: {geom_params}")
        
        sim = TRIMSimulation(params)
        results = sim.run(record_trajectories=False)
        
        print(f"Gestoppt: {results.count_inside}/{results.total_ions}")
        print(f"Mittlere Tiefe: {results.mean_z:.1f} Å")


def demo_export():
    """Demonstrate export to different formats."""
    print("\n" + "="*60)
    print("DEMO 3: Export-Funktionen")
    print("="*60)
    
    # Run a small simulation
    params = SimulationParameters()
    params.nion = 500
    params.z1 = 5
    params.m1 = 11.009
    params.z2 = 14
    params.m2 = 28.086
    params.density = 0.04994
    params.e_init = 50000
    params.corr_lindhard = 1.5
    params.zmin = 0
    params.zmax = 4000
    
    print(f"\nSimuliere {params.nion} Ionen...")
    sim = TRIMSimulation(params)
    results = sim.run(record_trajectories=True, max_trajectories=10)
    
    # Create output directory
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nExportiere Ergebnisse nach '{output_dir}/'...")
    
    # Export to CSV
    print("  - CSV Export...")
    export.export_to_csv(results, output_dir / "demo_results.csv", 
                        include_trajectories=True)
    
    # Export to JSON
    print("  - JSON Export...")
    export.export_to_json(results, output_dir / "demo_results.json",
                         include_trajectories=True)
    
    # Export to VTK
    if hasattr(results, 'stopped_positions') and results.stopped_positions:
        print("  - VTK Export...")
        export.export_to_vtk(results, output_dir / "demo_results.vtk")
    
    # Export trajectories to VTK
    if results.trajectories:
        print("  - VTK Trajektorien Export...")
        export.export_trajectories_to_vtk(results.trajectories, 
                                          output_dir / "demo_trajectories.vtk")
    
    print(f"\n✓ Export abgeschlossen!")
    print(f"  Dateien in: {output_dir.absolute()}")
    
    # List files
    print(f"\nErzeugte Dateien:")
    for f in sorted(output_dir.glob("*")):
        size_kb = f.stat().st_size / 1024
        print(f"  - {f.name:30s} ({size_kb:7.1f} KB)")
    
    return results, params


def demo_visualizations(results, params):
    """Demonstrate advanced visualizations."""
    print("\n" + "="*60)
    print("DEMO 4: Erweiterte Visualisierungen")
    print("="*60)
    
    if not results.trajectories:
        print("Keine Trajektorien verfügbar für Demo.")
        return
    
    print("\nErzeuge Plots...")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(15, 10))
    
    # 1. Energy vs Depth
    print("  - Energie vs. Tiefe...")
    ax1 = fig.add_subplot(2, 3, 1)
    for traj in results.trajectories[:5]:  # First 5
        traj_arr = np.array(traj)
        z = traj_arr[:, 2]
        e = traj_arr[:, 3] / 1000  # keV
        ax1.plot(z, e, alpha=0.6, linewidth=1)
    ax1.axvline(params.zmin, color='red', linestyle='--', alpha=0.5)
    ax1.axvline(params.zmax, color='red', linestyle='--', alpha=0.5)
    ax1.set_xlabel('Tiefe (Å)')
    ax1.set_ylabel('Energie (keV)')
    ax1.set_title('Energie-Verlust')
    ax1.grid(True, alpha=0.3)
    
    # 2. Depth histogram
    print("  - Stopptiefe-Verteilung...")
    ax2 = fig.add_subplot(2, 3, 2)
    if results.stopped_depths:
        ax2.hist(results.stopped_depths, bins=30, alpha=0.7, edgecolor='black')
        ax2.axvline(results.mean_z, color='red', linestyle='--', 
                   label=f'Mean: {results.mean_z:.1f} Å')
        ax2.axvline(results.mean_z - results.std_z, color='orange', 
                   linestyle=':', alpha=0.7)
        ax2.axvline(results.mean_z + results.std_z, color='orange', 
                   linestyle=':', alpha=0.7, label=f'±σ: {results.std_z:.1f} Å')
    ax2.set_xlabel('Stopptiefe (Å)')
    ax2.set_ylabel('Anzahl')
    ax2.set_title('Stopptiefe-Verteilung')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 2D Heatmap (x-z)
    print("  - Heatmap (x-z)...")
    ax3 = fig.add_subplot(2, 3, 3)
    if hasattr(results, 'stopped_positions') and results.stopped_positions:
        positions = np.array(results.stopped_positions)
        x = positions[:, 0]
        z = positions[:, 2]
        h, xedges, zedges = np.histogram2d(x, z, bins=30)
        extent = [zedges[0], zedges[-1], xedges[0], xedges[-1]]
        im = ax3.imshow(h, extent=extent, origin='lower', aspect='auto',
                       cmap='hot', interpolation='bilinear')
        plt.colorbar(im, ax=ax3, label='Dichte')
        ax3.axvline(params.zmin, color='cyan', linestyle='--', alpha=0.5)
        ax3.axvline(params.zmax, color='cyan', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Tiefe z (Å)')
    ax3.set_ylabel('Position x (Å)')
    ax3.set_title('2D Dichte-Heatmap (x-z)')
    
    # 4. Radial distribution
    print("  - Radiale Verteilung...")
    ax4 = fig.add_subplot(2, 3, 4)
    if hasattr(results, 'stopped_positions') and results.stopped_positions:
        positions = np.array(results.stopped_positions)
        x = positions[:, 0]
        y = positions[:, 1]
        z = positions[:, 2]
        r = np.sqrt(x**2 + y**2)
        ax4.scatter(z, r, alpha=0.3, s=5)
        ax4.set_xlabel('Tiefe z (Å)')
        ax4.set_ylabel('Radiale Distanz r (Å)')
        ax4.set_title('Radiale Streuung')
        ax4.grid(True, alpha=0.3)
    
    # 5. x-y cross section
    print("  - Strahlquerschnitt (x-y)...")
    ax5 = fig.add_subplot(2, 3, 5)
    if hasattr(results, 'stopped_positions') and results.stopped_positions:
        positions = np.array(results.stopped_positions)
        x = positions[:, 0]
        y = positions[:, 1]
        h, xedges, yedges = np.histogram2d(x, y, bins=25)
        extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
        im = ax5.imshow(h, extent=extent, origin='lower', aspect='equal',
                       cmap='hot', interpolation='bilinear')
        plt.colorbar(im, ax=ax5, label='Dichte')
        # Add circle for std
        r_std = np.std(np.sqrt(x**2 + y**2))
        circle = plt.Circle((0, 0), r_std, fill=False, color='cyan',
                          linestyle='--', alpha=0.7)
        ax5.add_patch(circle)
    ax5.set_xlabel('y (Å)')
    ax5.set_ylabel('x (Å)')
    ax5.set_title('Strahlquerschnitt (x-y)')
    
    # 6. Statistics text
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis('off')
    stats_text = results.get_summary()
    ax6.text(0.1, 0.9, stats_text, transform=ax6.transAxes,
            fontfamily='monospace', fontsize=8,
            verticalalignment='top')
    
    plt.tight_layout()
    
    # Save figure
    output_file = Path("demo_output") / "demo_visualizations.png"
    print(f"\nSpeichere Plot: {output_file}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print("✓ Plot gespeichert!")
    
    # Show plot
    print("\nZeige Plot...")
    plt.show()


def main():
    """Run all demos."""
    print("\n" + "🚀" * 30)
    print("CyTRIM - Advanced Features Demo")
    print("🚀" * 30)
    
    # Demo 1: Presets
    demo_presets()
    
    # Demo 2: Geometries
    demo_geometries()
    
    # Demo 3: Export
    results, params = demo_export()
    
    # Demo 4: Visualizations
    demo_visualizations(results, params)
    
    print("\n" + "="*60)
    print("✓ Alle Demos abgeschlossen!")
    print("="*60)
    print("\nNächste Schritte:")
    print("  1. Öffne die erweiterte GUI: ./run_extended_gui.sh")
    print("  2. Lade ein Preset: 'Preset laden...' Button")
    print("  3. Wähle Geometrie: Geometrie-Tab")
    print("  4. Exportiere Ergebnisse: '💾 Exportieren...' Button")
    print("\nDokumentation:")
    print("  - README.md")
    print("  - ADVANCED_FEATURES.md")
    print("  - GEOMETRY3D.md")


if __name__ == '__main__':
    main()
