# CyTRIM – Advanced Features (v2.0)

This document summarizes the advanced capabilities of CyTRIM for professional ion-implantation simulations. All UI texts and outputs are in English. Trajectories are recorded as (x, y, z, E) tuples.

---

## 1. Dynamic geometry selection

Supported geometry types:
- Planar (default): infinite planar surface, defined by z_min and z_max
- Box: rectangular target volume, parameters: x_min, x_max, y_min, y_max
- Cylinder: cylindrical target, parameters: radius, axis (x, y, or z)
- Sphere: spherical target, parameters: radius, center (x, y, z)
- MultiLayer: layered stack, parameter: layer_thicknesses (list of Ångström thicknesses)

Using the GUI:
1) Open the Geometry tab
2) Choose a geometry from the dropdown
3) Fill in the shown parameters
4) Run the simulation

Example (cylindrical nanowire):
- Geometry type: cylinder
- Radius: 50 Å
- Axis: z

---

## 2. Material presets

Built-in presets ready to use:
- B in Si (PMOS)
- As in Si (NMOS S/D)
- P in Si (NMOS)
- BF2 in Si (shallow junctions)
- Ga in GaN (III–V)
- He in W (plasma-facing)
- Ar in Cu (surface modification)
- N in Ti (TiN formation)

Load a preset:
1) Click “Load preset…”
2) Select a preset
3) Confirm with OK
4) All parameters are applied automatically

Custom presets are stored in:
- ~/.cytrim/presets/

Minimal JSON example:
{
  "name": "My custom preset",
  "description": "Describe here",
  "z1": 15,
  "m1": 30.974,
  "element1": "P",
  "z2": 14,
  "m2": 28.086,
  "element2": "Si",
  "density": 0.04994,
  "energy": 60000.0,
  "corr_lindhard": 1.5,
  "zmin": 0.0,
  "zmax": 3500.0,
  "geometry_type": "planar"
}

---

## 3. Export options

- CSV: tabular data (summary, stop positions, optional trajectories)
- JSON: full structured data for further processing
- VTK: ParaView-compatible 3D visualization (points, lines, scalars)
- PNG: high-resolution plots (300 DPI), one file per plot

Generated PNGs (examples):
- results_traj3d.png – 3D trajectories
- results_traj2d_xz.png – 2D x–z projection
- results_traj2d_yz.png – 2D y–z projection
- results_heatmap_xz.png – x–z heatmap
- results_heatmap_yz.png – y–z heatmap
- results_energy.png – energy loss vs depth
- results_histogram.png – stopping-depth histogram

Export from the GUI:
1) Finish a simulation
2) Click “Export…”
3) Pick a format (or “All formats”)
4) Options: include trajectories, high-resolution (300 DPI)
5) Choose filename and OK

---

## 4. Advanced visualizations

- Heatmap (x–z): 2D ion-density vs depth (Gaussian smoothing optional)
- Heatmap (y–z): same as x–z for the y plane
- Heatmap (x–y): beam cross-section at median depth, radial symmetry cues
- Energy loss: E vs depth for trajectories (mean ± std overlay)
- Radial distribution: r vs z, lateral scattering vs depth
- Stopping depth histogram: final z positions with Gaussian fit (stopped/pass-through/backscattered)

Reading tips:
- Bright heatmap regions indicate high concentration
- Width indicates lateral scattering
- Energy loss plot shows deceleration profile

---

## 5. Scientific extensions

Recoil cascades (foundation):
- Primary ion displaces a target atom
- Recoils may trigger further displacements (generations)

Key parameters:
- displacement_energy (eV), max_cascade_depth, min_recoil_energy (eV)

Derived quantities:
- Vacancies, interstitials, Frenkel pairs, DPA
- Damage profile: defect density vs depth

Planned: multilayer materials
- Per-layer material properties
- Correct layer transitions and interface effects

Planned: crystal channeling
- Reduced stopping along crystal axes (FCC/BCC/Diamond)
- Critical angle, dechanneling, deeper ranges

---

## 6. Performance

Cython acceleration:
- Automatically used when available (⚡ icon); Python fallback (🐍 icon)
- Typical speedups: Scatter ~6–8×, Geometry ~5×, Trajectory ~7× overall ~6×

Runtime toggle:
- “Use Cython” checkbox; modules hot-reloaded without restart

Recommended settings:
- Quick tests: 100–1000 ions, Cython ON
- Production: 10k–100k ions, Cython ON
- Debug: 10–100 ions, Cython OFF

---

## 7. Example workflows

Example 1: Standard B in Si
- Preset: B in Si, Ions: 5000, Geometry: planar
- Export: JSON + PNG
- Result: mean depth ~1250 Å, std ~420 Å, ~85% stopped

Example 2: Nanowire (cylinder)
- Preset: P in Si, Radius: 50 Å, Axis: z, Ions: 2000
- Use x–y heatmap for beam profile; radial distribution for confinement

Example 3: Energy sweep
- energies = [20, 40, 60, 80, 100] keV
- Analyze mean stopping depth vs energy (z ∝ E^n, n ≈ 0.5–0.7 for Si)

---

## 8. Tips

Performance:
- Use Cython for large runs, scale ion count gradually
- Avoid recording trajectories for >10k ions unless required

Visualization:
- Heatmaps for density, 3D for qualitative overview
- Energy loss for stopping-power validation; radial distribution for scattering

Data analysis (Python):
- Load JSON, compute statistics, and plot histograms using NumPy/Matplotlib

---

## 9. Troubleshooting

GUI doesn’t start:
- Check Python ≥ 3.8
- pip install -r requirements.txt
- Run: python pytrim_gui_extended.py

Cython unavailable:
- ./build_cython.sh or python setup.py build_ext --inplace

Export fails:
- Try a different directory, check disk space and permissions

Slow simulation:
- Ensure Cython is ON, reduce ions for testing, simplify geometry

---

## 10. Roadmap

- Live updates during simulation (real-time trajectories and histograms; pause/resume)
- Animation export (GIF/MP4)
- GPU acceleration (CUDA/CuPy) with CPU fallback
- Extended physics (channeling, temperature, dose dependence)

---

References:
- Ziegler et al., SRIM (2010)
- Robinson & Torrens, PRB 9, 5008 (1974)
- Gibbons, Proceedings of the IEEE (1972)
- Sze & Ng, Physics of Semiconductor Devices (2007)
- Feldman et al., Materials Analysis by Ion Channeling (1982)

Support:
- Docs: README.md, GEOMETRY3D.md, ADVANCED_FEATURES.md
- Examples: demo_*.py
- Tests: test_*.py

Version: 2.0 Extended  |  License: see LICENSE
