# Changelog - PyTRIM GUI Version

## Version 1.1.1 - Performance-Statusanzeige

### ✨ Neue Features
- **Performance-Statusanzeige in GUI**
  - Zeigt ob Cython oder Python verwendet wird
  - ⚡ Grüne Anzeige bei aktivem Cython (~6.4x schneller)
  - 🐍 Orange Anzeige bei Python Fallback mit Build-Hinweis
  - Durchsatz-Anzeige in Resultsen (Ionen/Sekunde)
  
### 📦 Neue Dateien
```
check_performance.py          # Performance-Status-Check
GUI_LAYOUT.md                 # Visuelle Dokumentation der GUI
```

### 🎨 GUI-Verbesserungen
- Performance-Box im linken Panel
- Farbcodierung: Grün (Cython) / Orange (Python)
- Performance-Info in Resulttabelle
- Durchsatz-Anzeige nach Simulation

## Version 1.1.0 - Cython-Optimierung

### 🚀 Performance-Verbesserungen
- **Cython-Implementierung** aller rechenintensiven Module
- **6.4x Velocityssteigerung** gegenüber Pure Python
- Automatischer Fallback auf Python wenn Cython nicht available
- Optimierte C-Code-Generierung mit `-O3 -ffast-math -march=native`

### 📦 Neue Dateien
```
cytrim/estop.pyx              # Cython: Elektronisches Stopping
cytrim/scatter.pyx            # Cython: ZBL-Scattering
cytrim/geometry.pyx           # Cython: Target-Geometrie
cytrim/select_recoil.pyx      # Cython: Kollisionsgeometrie
cytrim/trajectory.pyx         # Cython: Trajektorien-Simulation
cytrim/*.pxd                  # Cython Header-Dateien
setup.py                      # Build-Konfiguration
build_cython.sh               # Build-Skript
benchmark.py                  # Performance-Benchmark
compare_performance.py        # Python vs Cython Vergleich
```

### ⚡ Benchmark-Resultse
- Pure Python: 14.2s für 500 Ionen (35 ions/s)
- Cython: 2.2s für 500 Ionen (226 ions/s)
- **Speedup: 6.4x**

### 🔧 Technische Details
- Type annotations für alle kritischen Funktionen
- `nogil` Optimierungen wo möglich
- Inline-Functions für interne Berechnungen
- Boundscheck und Wraparound deaktiviert für maximale Performance
- C-Division statt Python-Division

## Version 1.0.0 - Initiale GUI-Version

## New Features

### 🎨 Moderne PyQt6-Benutzeroberfläche
- **Vollständige GUI** mit intuitiver Bedienung
- **Parameterseingabe** über Eingabefelder statt Code-Bearbeitung
- **Echtzeit-Fortschrittsanzeige** während der Simulation
- **Start/Stop-Buttons** zur Kontrolle der Simulation

### 📊 Visualisierung
- **Trajektorien-Plot**: Visualisierung der ersten 10 Ion-Pfade (x-z-Projection)
- **Stopptiefe-Histogramm**: Verteilung aller finalen Positionen mit Mittelwert
- **Interaktive Plots**: Zoom, Pan, Export über matplotlib-Toolbar
- **Tab-basierte Navigation** zwischen verschiedenen Ansichten

### 🔧 Verbesserte Architektur
- **Simulationsklasse** (`TRIMSimulation`): Wiederverwendbare API
- **Parameters-Objekt** (`SimulationParameterss`): Saubere Parameters-Verwaltung
- **Result-Objekt** (`SimulationResults`): Strukturierte Ausgabe
- **Threading**: GUI bleibt während Simulation reaktiv
- **Modular**: Kann auch programmatisch genutzt werden

### 💾 Datenexport
- **Resultse exportieren**: Statistiken und Stopptiefen als Textdatei
- **Format**: Einfach weiterverarbeitbar (z.B. in Excel, Python, etc.)

## File Structure

### Newly Created Files
```
pytrim_gui.py                 # Haupt-GUI-Anwendung
pytrim/simulation.py          # Simulationsklassen und API
pytrim/__init__.py            # Package-Definition
pytrim/pytrim_cli.py          # Kommandozeilen-Version (neu)
requirements.txt              # Python-Abhängigkeiten
run_gui.sh                    # Startskript (Linux/Mac)
QUICKSTART.md                 # Schnellstartanleitung
API.md                        # API-Dokumentation
```

### Modified Files
```
pytrim/trajectory.py          # Erweitert um trajectory_with_path()
README.md                     # Aktualisiert mit GUI-Anleitung
```

### Unchanged (Core Physics)
```
pytrim/estop.py              # Elektronisches Stopping
pytrim/scatter.py            # ZBL-Scattering
pytrim/select_recoil.py      # Kollisionsgeometrie
pytrim/geometry.py           # Target-Geometrie
pytrim/pytrim.py             # Original-Skript (legacy)
```

## Technical Details

### Dependencies
- **NumPy** >= 1.20.0: Numerische Berechnungen
- **PyQt6** >= 6.4.0: GUI-Framework
- **Matplotlib** >= 3.5.0: Plotting und Visualisierung

### Threading Architecture
- Simulation läuft in separatem QThread
- Progress-Updates über Qt-Signals
- GUI bleibt reaktiv, kann Simulation stoppen

### Plot Integration
- matplotlib FigureCanvas in PyQt6 eingebettet
- NavigationToolbar für Interaktivität
- Automatisches Update nach Simulation

## Migration from Old Version

### For Users
**Alt:**
```bash
# Parameters in pytrim/pytrim.py editieren
python pytrim/pytrim.py
```

**Neu:**
```bash
./run_gui.sh
# Parameters in GUI eingeben
```

### For Developers
**Alt:**
```python
# Parameters hardcodiert in pytrim.py
```

**Neu:**
```python
from pytrim.simulation import TRIMSimulation, SimulationParameterss

params = SimulationParameterss()
params.nion = 1000
params.e_init = 50000
# ... weitere Parameters

sim = TRIMSimulation(params)
results = sim.run()
```

## Bekannte Limitierungen

- Nur erste 10 Trajektorien werden visualisiert (Performance)
- Rekoil-Kaskaden noch nicht implementiert
- Nur planare Target-Geometrie
- Keine Kristall-Channeling-Effekte

## Future Extensions (möglich)

- [ ] Parameters-Presets (z.B. "B in Si", "As in GaAs")
- [ ] Plot-Export als PNG/PDF
- [ ] Batch-Simulationen (Energy-Scan, etc.)
- [ ] 3D-Visualisierung der Trajektorien
- [ ] Rekoil-Kaskaden track
- [ ] Multi-Layer-Targets
- [ ] Parallel-Processing für schnellere Simulation

## Compatibility

- **Python**: >= 3.8 (getestet mit 3.8, 3.9, 3.10, 3.11)
- **OS**: Linux, macOS, Windows
- **Qt**: PyQt6 (Qt 6.x)

## Installation & Startup

Siehe `QUICKSTART.md` für detaillierte Anleitung.

**Kurzversion:**
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./run_gui.sh  # or: .venv/bin/python pytrim_gui.py
```
