# Changelog - PyTRIM GUI Version

## Version 1.1.0 - Cython-Optimierung

### 🚀 Performance-Verbesserungen
- **Cython-Implementierung** aller rechenintensiven Module
- **6.4x Geschwindigkeitssteigerung** gegenüber Pure Python
- Automatischer Fallback auf Python wenn Cython nicht verfügbar
- Optimierte C-Code-Generierung mit `-O3 -ffast-math -march=native`

### 📦 Neue Dateien
```
cytrim/estop.pyx              # Cython: Elektronisches Stopping
cytrim/scatter.pyx            # Cython: ZBL-Streuung
cytrim/geometry.pyx           # Cython: Target-Geometrie
cytrim/select_recoil.pyx      # Cython: Kollisionsgeometrie
cytrim/trajectory.pyx         # Cython: Trajektorien-Simulation
cytrim/*.pxd                  # Cython Header-Dateien
setup.py                      # Build-Konfiguration
build_cython.sh               # Build-Skript
benchmark.py                  # Performance-Benchmark
compare_performance.py        # Python vs Cython Vergleich
```

### ⚡ Benchmark-Ergebnisse
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

## Neue Features

### 🎨 Moderne PyQt6-Benutzeroberfläche
- **Vollständige GUI** mit intuitiver Bedienung
- **Parametereingabe** über Eingabefelder statt Code-Bearbeitung
- **Echtzeit-Fortschrittsanzeige** während der Simulation
- **Start/Stop-Buttons** zur Kontrolle der Simulation

### 📊 Visualisierung
- **Trajektorien-Plot**: Visualisierung der ersten 10 Ion-Pfade (x-z-Projektion)
- **Stopptiefe-Histogramm**: Verteilung aller finalen Positionen mit Mittelwert
- **Interaktive Plots**: Zoom, Pan, Export über matplotlib-Toolbar
- **Tab-basierte Navigation** zwischen verschiedenen Ansichten

### 🔧 Verbesserte Architektur
- **Simulationsklasse** (`TRIMSimulation`): Wiederverwendbare API
- **Parameter-Objekt** (`SimulationParameters`): Saubere Parameter-Verwaltung
- **Ergebnis-Objekt** (`SimulationResults`): Strukturierte Ausgabe
- **Threading**: GUI bleibt während Simulation reaktiv
- **Modular**: Kann auch programmatisch genutzt werden

### 💾 Datenexport
- **Ergebnisse exportieren**: Statistiken und Stopptiefen als Textdatei
- **Format**: Einfach weiterverarbeitbar (z.B. in Excel, Python, etc.)

## Dateistruktur

### Neu erstellte Dateien
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

### Geänderte Dateien
```
pytrim/trajectory.py          # Erweitert um trajectory_with_path()
README.md                     # Aktualisiert mit GUI-Anleitung
```

### Unverändert (Kern-Physik)
```
pytrim/estop.py              # Elektronisches Stopping
pytrim/scatter.py            # ZBL-Streuung
pytrim/select_recoil.py      # Kollisionsgeometrie
pytrim/geometry.py           # Target-Geometrie
pytrim/pytrim.py             # Original-Skript (legacy)
```

## Technische Details

### Abhängigkeiten
- **NumPy** >= 1.20.0: Numerische Berechnungen
- **PyQt6** >= 6.4.0: GUI-Framework
- **Matplotlib** >= 3.5.0: Plotting und Visualisierung

### Threading-Architektur
- Simulation läuft in separatem QThread
- Progress-Updates über Qt-Signals
- GUI bleibt reaktiv, kann Simulation stoppen

### Plot-Integration
- matplotlib FigureCanvas in PyQt6 eingebettet
- NavigationToolbar für Interaktivität
- Automatisches Update nach Simulation

## Migration von alter Version

### Für Nutzer
**Alt:**
```bash
# Parameter in pytrim/pytrim.py editieren
python pytrim/pytrim.py
```

**Neu:**
```bash
./run_gui.sh
# Parameter in GUI eingeben
```

### Für Entwickler
**Alt:**
```python
# Parameter hardcodiert in pytrim.py
```

**Neu:**
```python
from pytrim.simulation import TRIMSimulation, SimulationParameters

params = SimulationParameters()
params.nion = 1000
params.e_init = 50000
# ... weitere Parameter

sim = TRIMSimulation(params)
results = sim.run()
```

## Bekannte Limitierungen

- Nur erste 10 Trajektorien werden visualisiert (Performance)
- Rekoil-Kaskaden noch nicht implementiert
- Nur planare Target-Geometrie
- Keine Kristall-Channeling-Effekte

## Zukünftige Erweiterungen (möglich)

- [ ] Parameter-Presets (z.B. "B in Si", "As in GaAs")
- [ ] Plot-Export als PNG/PDF
- [ ] Batch-Simulationen (Energie-Scan, etc.)
- [ ] 3D-Visualisierung der Trajektorien
- [ ] Rekoil-Kaskaden verfolgen
- [ ] Multi-Layer-Targets
- [ ] Parallel-Processing für schnellere Simulation

## Kompatibilität

- **Python**: >= 3.8 (getestet mit 3.8, 3.9, 3.10, 3.11)
- **OS**: Linux, macOS, Windows
- **Qt**: PyQt6 (Qt 6.x)

## Installation & Start

Siehe `QUICKSTART.md` für detaillierte Anleitung.

**Kurzversion:**
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./run_gui.sh  # oder: .venv/bin/python pytrim_gui.py
```
