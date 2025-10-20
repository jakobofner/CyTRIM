# 3D Geometry Features - CyTRIM

## Übersicht

CyTRIM unterstützt jetzt vollständige **3D-Simulationen** mit verschiedenen Geometrietypen und echter 3D-Visualisierung!

## Verfügbare Geometrien

### 1. **Planar** (Standard, abwärtskompatibel)
Einfache planare Geometrie, unbegrenzt in x-y Richtung.

```python
params.geometry_type = 'planar'
params.zmin = 0
params.zmax = 4000
```

### 2. **Box** (Rechteckiges Target)
3D-Box mit definierten Grenzen in allen Richtungen.

```python
params.geometry_type = 'box'
params.geometry_params = {
    'x_min': -500, 'x_max': 500,
    'y_min': -500, 'y_max': 500,
    'z_min': 0, 'z_max': 4000
}
```

**Anwendung:** Rechteckige Chips, strukturierte Targets

### 3. **Cylinder** (Zylindrisches Target)
Zylinder mit Achse entlang z-Richtung.

```python
params.geometry_type = 'cylinder'
params.geometry_params = {
    'radius': 300,
    'z_min': 0,
    'z_max': 4000,
    'center_x': 0,
    'center_y': 0
}
```

**Anwendung:** Nanowires, Säulen, zylindrische Proben

### 4. **Sphere** (Kugelförmiges Target)
Sphärisches Target.

```python
params.geometry_type = 'sphere'
params.geometry_params = {
    'radius': 2000,
    'center_x': 0,
    'center_y': 0,
    'center_z': 1000
}
```

**Anwendung:** Nanopartikel, Kugeln, radiale Symmetrie

### 5. **MultiLayer** (Mehrschicht-System)
Gestapelte Schichten mit verschiedenen z-Positionen.

```python
params.geometry_type = 'multilayer'
params.geometry_params = {
    'layer_z_positions': [0, 100, 300, 500],
    'x_min': -500, 'x_max': 500,
    'y_min': -500, 'y_max': 500
}
```

**Anwendung:** Schichtsysteme, Dünnfilm-Stacks

## GUI-Verwendung

### Starten des GUI
```bash
./run_gui.sh
# oder
python pytrim_gui.py
```

### 3D-Visualisierung
1. Parameter eingeben
2. **"Simulation starten"** klicken
3. Tab **"3D Trajektorien"** öffnen
4. Sehen Sie:
   - Farbige 3D-Trajektorien
   - Transparente Geometrie-Grenzen
   - Interaktive Rotation mit Maus

### Navigation in 3D
- **Linke Maustaste + Ziehen:** Rotieren
- **Rechte Maustaste + Ziehen:** Zoomen
- **Mittlere Maustaste + Ziehen:** Verschieben
- **Toolbar:** Reset, Zoom, Speichern

## Programmgesteuerte Verwendung

### Beispiel: Box-Geometrie
```python
from pytrim import TRIMSimulation, SimulationParameters

params = SimulationParameters()
params.nion = 100
params.e_init = 50000  # 50 keV

# Box-Geometrie konfigurieren
params.geometry_type = 'box'
params.geometry_params = {
    'x_min': -500, 'x_max': 500,
    'y_min': -500, 'y_max': 500,
    'z_min': 0, 'z_max': 4000
}

# Simulation ausführen
sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True)

# 3D-Statistiken anzeigen
print(results.get_summary())
print(f"3D Position: ({results.mean_x:.1f}, {results.mean_y:.1f}, {results.mean_z:.1f}) Å")
print(f"Radial spread: {results.mean_r:.1f} ± {results.std_r:.1f} Å")
```

### Beispiel: Zylinder mit radialer Analyse
```python
params = SimulationParameters()
params.geometry_type = 'cylinder'
params.geometry_params = {
    'radius': 300,
    'z_min': 0,
    'z_max': 1000
}

sim = TRIMSimulation(params)
results = sim.run()

# Prüfe, ob Ionen im Zylinder bleiben
import numpy as np
radii = [np.sqrt(pos[0]**2 + pos[1]**2) for pos in results.stopped_positions]
print(f"Max. Radius: {max(radii):.2f} Å (Zylinder-Radius: 300 Å)")
```

## Ergebnisse und Statistiken

### 3D-Verteilungsanalyse
Die `SimulationResults` enthalten jetzt:

```python
results.stopped_positions  # Liste von (x, y, z) Tupeln
results.mean_x, mean_y, mean_z  # Mittelwerte
results.std_x, std_y, std_z     # Standardabweichungen
results.mean_r, std_r           # Radiale Statistik
```

### Ausgabe-Beispiel
```
Number of ions stopped inside the target: 25 / 100

3D Distribution Statistics:
  Mean position (x, y, z): (3.47, -0.30, 1922.07) A
  Std deviation (x, y, z): (252.16, 245.86, 521.73) A
  Radial spread (mean ± std): 324.86 ± 136.08 A

Legacy (z-only) Statistics:
  Mean penetration depth: 1922.07 A
  Standard deviation: 521.73 A

Simulation time: 0.89 seconds
```

## Demo-Skripte

### Quick-Start Demos
```bash
# Box-Geometrie Demo
python demo_3d_gui.py --geometry box

# Zylinder-Geometrie Demo
python demo_3d_gui.py --geometry cylinder

# Kugel-Geometrie Demo
python demo_3d_gui.py --geometry sphere
```

### Test-Suite
```bash
# Teste alle Geometrien
python test_geometry3d.py
```

## Performance

### Cython-Optimierung
Alle Geometrien sind Cython-optimiert:
```bash
# Kompiliere für beste Performance
./build_cython.sh
```

**Performance-Vergleich:**
- Box-Check: ~10 ns (Cython) vs ~100 ns (Python)
- Cylinder-Check: ~15 ns (Cython) vs ~150 ns (Python)
- Sphere-Check: ~20 ns (Cython) vs ~200 ns (Python)

### Tipps für große Simulationen
1. Verwende Cython (6.4x schneller)
2. Box > Cylinder > Sphere (Rechenzeit)
3. Reduziere Trajektorien-Aufzeichnung für große N

## Visualisierungs-Tipps

### Optimale Ansichten
- **Box:** Isometrische Ansicht (45°)
- **Cylinder:** Von oben oder Seite
- **Sphere:** Beliebiger Winkel

### Export
- Toolbar → **"Save"** für PNG/PDF
- Hochauflösende Plots möglich

## Erweiterte Features

### Custom Geometrien
Erstelle eigene Geometrie-Klassen:

```python
from pytrim.geometry3d import Geometry3D

class MyGeometry(Geometry3D):
    def is_inside_target(self, pos):
        # Deine Logik hier
        return True
    
    def get_bounds(self):
        return ((x_min, x_max), (y_min, y_max), (z_min, z_max))
```

### Geometrie-Kombination
Kombiniere Geometrien (z.B. Box mit Loch):

```python
class BoxWithHole(Geometry3D):
    def __init__(self, outer_box, inner_cylinder):
        self.box = outer_box
        self.cylinder = inner_cylinder
    
    def is_inside_target(self, pos):
        return self.box.is_inside_target(pos) and \
               not self.cylinder.is_inside_target(pos)
```

## Troubleshooting

### Problem: Keine Ionen stoppen
- **Lösung:** Energie zu hoch oder Target zu klein
- Reduziere `e_init` oder erhöhe Geometrie-Dimensionen

### Problem: 3D-Plot leer
- **Lösung:** Keine Trajektorien aufgezeichnet
- Stelle sicher: `record_trajectories=True`

### Problem: Geometrie nicht sichtbar
- **Lösung:** Zoom/Skalierung
- Nutze Toolbar "Home" Button zum Reset

### Problem: Langsame Visualisierung
- **Lösung:** Zu viele Trajektorien
- Reduziere `max_trajectories` (Standard: 10)

## Bekannte Limitierungen

1. **Recoil-Kaskaden:** Noch nicht implementiert (nur Primärionen)
2. **Kristallstruktur:** Amorph (keine Channeling-Effekte)
3. **Multilayer-Materialien:** Gleiche Material-Eigenschaften für alle Schichten

## Zukünftige Features

- [ ] Verschiedene Materialien pro Schicht
- [ ] Recoil-Tracking in 3D
- [ ] Schädigungsprofil-Visualisierung
- [ ] Exportieren von 3D-Daten (VTK, etc.)
- [ ] Animations-Export

## Zitierung

Wenn Sie CyTRIM mit 3D-Features in Ihrer Forschung verwenden:

```
CyTRIM - 3D Ion Transport Simulation
https://github.com/jakobofner/CyTRIM
```

## Support

Bei Fragen oder Problemen:
1. Siehe README.md und QUICKSTART.md
2. Teste mit `test_geometry3d.py`
3. Erstelle ein Issue auf GitHub

---

**Viel Erfolg mit 3D-Simulationen!** 🎉
