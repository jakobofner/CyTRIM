# CyTRIM (PyTRIM) - Advanced Edition

Eine professionelle Python-Implementierung von TRIM (Transport of Ions in Matter) mit modernen Features für Forschung und Lehre. Das Programm simuliert den Transport von Ionenstrahlen in komplexe 3D-Geometrien mittels Monte‑Carlo und bietet umfassende Analyse- und Visualisierungsmöglichkeiten.

**Version 2.0 - Advanced Edition:**
- 🎯 **Erweiterte GUI** mit Material-Presets und dynamischer Geometrie-Auswahl
- 📊 **10+ Visualisierungen** inklusive Heatmaps, Energie-Verlust, radiale Verteilung
- 💾 **Multi-Format Export** (CSV, JSON, VTK, PNG) für professionelle Datenanalyse
- ⚡ **6.4x schneller** mit Cython-Optimierung

> **📖 Schnellstart:** Siehe [QUICKSTART.md](QUICKSTART.md) | **🚀 Erweiterte Features:** [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)

## Kern-Features

### Physik & Simulation
- **Monte-Carlo Ion Transport** mit realistischer Physik
- **3D Trajektorien-Verfolgung** mit vollständiger Positions-Historie
- **5 Geometrie-Typen**: Planar, Box, Cylinder, Sphere, MultiLayer
- **ZBL-Potential** für elastische Streuung
- **Lindhard Stopping Power** mit Korrektur-Faktor
- **Recoil-Kaskaden** (in Entwicklung) für Strahlenschäden

### Benutzeroberfläche
- **Moderne PyQt6-GUI** mit 10+ Visualisierungs-Tabs
- **Material-Presets** für Standard-Szenarien (B in Si, As in Si, etc.)
- **Dynamische Geometrie-Auswahl** mit kontextabhängigen Parametern
- **Echtzeit-Fortschritt** mit Performance-Anzeige
- **Interaktive 3D-Plots** mit Rotation und Zoom

### Visualisierung & Analyse
- **3D Trajektorien** mit Geometrie-Rendering
- **2D Projektionen** (x-z, y-z) für detaillierte Analyse
- **Heatmaps** (x-z, y-z, x-y) zur Dichte-Visualisierung
- **Energie-Verlust Plots** mit gemittelten Profilen
- **Radiale Verteilung** vs. Tiefe
- **Stopptiefe-Histogramme** mit Statistiken

### Export & Integration
- **CSV**: Tabellarische Daten für Excel/Python
- **JSON**: Strukturierte Daten für Weiterverarbeitung
- **VTK**: 3D-Visualisierung in ParaView
- **PNG**: Hochauflösende Plots (300 DPI)
- **Trajektorien-Export** als Polylines

### Performance
- **Cython-Optimierung** für bis zu 6.4x Speedup
- **Runtime-Toggle** zwischen Cython und Python
- **Automatischer Fallback** auf Pure Python
- **Performance-Monitoring** im GUI

## Was macht das Programm?

- Simuliert nacheinander viele Primärionen (Monte‑Carlo).
- Bewegt jedes Ion schrittweise bis zum Stillstand (Energie unter Schwelle) oder bis es das Target verlässt.
- Berücksichtigt elektronische Energieverluste nach Lindhard (mit Korrekturfaktor) entlang der freien Weglänge bis zur nächsten Kollision.
- Behandelt elastische Streuung an Targetatomen mit dem ZBL‑Potential und Biersacks „magic formula“ für den Streuwinkel.
- Erfasst die Stopptiefe der Ionen, die im Target zur Ruhe kommen, und berechnet Mittelwert und Standardabweichung.

Einheiten: Positionen in Å, Energien in eV, Dichten in Atome/Å³.

## Wie funktioniert es? (Ablauf)

1) Initialisierung
- `select_recoil.setup(density)`: mittlere freie Weglänge aus der Dichte.
- `scatter.setup(z1, m1, z2, m2)`: Konstanten für ZBL‑Streuung (Normierungen, Massenverhältnis).
- `estop.setup(corr_lindhard, z1, m1, z2, density)`: Faktor für Lindhard‑Stopping bei gegebener Dichte.
- `geometry.setup(zmin, zmax)`: planare Targetgrenzen in z‑Richtung.
- `trajectory.setup()`: Energieschwelle `EMIN` (Standard: 5 eV).

2) Trajektorie eines Ions (`trajectory.trajectory`)
- Bestimme freie Weglänge und Kollisionsgeometrie: `select_recoil.get_recoil_position(pos, dir)` liefert freie Weglänge, Impaktparameter p und Richtung zum Rekoil.
- Elektronischer Energieverlust entlang der freien Weglänge: `estop.eloss(e, free_path)` (Lindhard, ∆E ∝ √E · Weglänge).
- Position aktualisieren; prüfen, ob das Ion noch im Target ist: `geometry.is_inside_target`.
- Elastische Streuung am Targetatom: `scatter.scatter(e, dir, p, dirp)` (ZBL + magic formula) liefert neue Richtung und Energie des Projektils (sowie Rekoilrichtung/-energie, die derzeit nicht weiterverfolgt werden).
- Wiederholen, bis `e ≤ EMIN` oder das Ion das Target verlässt.

3) Statistik
- Zähle Ionen, die innerhalb des Targets stoppen, und akkumulieren deren Stopptiefe z.
- Ausgabe: Anzahl der stoppenden Ionen, mittlere Stopptiefe und Standardabweichung, sowie Laufzeit.

## Projektstruktur

### GUI-Version (empfohlen)
- `pytrim_gui.py`: Hauptprogramm mit moderner PyQt6-Benutzeroberfläche
- `pytrim/simulation.py`: Simulationsklassen (TRIMSimulation, SimulationParameters, SimulationResults)

### Kern-Module
- `pytrim/trajectory.py`: Simuliert die Trajektorie eines einzelnen Ions (Schleife bis Stoppen/Verlassen)
- `pytrim/select_recoil.py`: Wählt die nächste Kollision in einem amorphen Target; mittlere freie Weglänge = Dichte^(-1/3), zufällige Azimutlage
- `pytrim/estop.py`: Elektronischer Energieverlust nach Lindhard mit Korrekturfaktor; ∆E wird am Schrittende abgezogen (abgeschnitten bei e)
- `pytrim/scatter.py`: ZBL‑Potential und Biersacks „magic formula" zur Bestimmung des Streuwinkels; aktualisiert Richtungen und teilt Energie zwischen Projektil und Rekoil auf
- `pytrim/geometry.py`: Einfache planare Geometrie mit Grenzen `zmin`/`zmax`

### Legacy
- `pytrim/pytrim.py`: Original-Kommandozeilen-Skript (Referenz)

## Installation

### Voraussetzungen
- Python ≥ 3.8
- NumPy
- PyQt6 (für GUI)
- Matplotlib (für Visualisierung)
- Cython (optional, für optimierte Performance)
- C-Compiler (optional, für Cython-Kompilation)

### Schnellinstallation

```bash
# Repository klonen oder herunterladen
cd CyTRIM

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv .venv
source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate

# Abhängigkeiten installieren
pip install --upgrade pip
pip install -r requirements.txt
```

### Cython-Optimierung (empfohlen für beste Performance)

**6.4x schnellere Simulation!**

```bash
# Nach der Grundinstallation:
./build_cython.sh

# Oder manuell:
pip install Cython
python setup.py build_ext --inplace
```

**Hinweis:** Falls die Kompilation fehlschlägt, funktioniert das Programm weiterhin mit reinem Python (langsamer, aber vollständig funktionsfähig).

## Ausführen

### GUI-Version (empfohlen)

**Standard-GUI:**
```bash
./run_gui.sh
```

**Erweiterte GUI mit allen Features:**
```bash
./run_extended_gui.sh
```

Die erweiterte GUI bietet:
- 📐 Geometrie-Auswahl (Planar, Box, Cylinder, Sphere, MultiLayer)
- 🧪 Material-Presets (B in Si, As in Si, etc.)
- 📊 10+ Visualisierungs-Tabs (Heatmaps, Energie-Verlust, etc.)
- 💾 Multi-Format Export (CSV, JSON, VTK, PNG)

**Oder manuell:**
```bash
# Virtuelle Umgebung aktivieren
source .venv/bin/activate  # Linux/Mac
# oder
.venv\Scripts\activate     # Windows

# GUI starten
python pytrim_gui.py
```

Die GUI öffnet sich mit folgenden Bereichen:
- **Links:** Parametereingabe für alle Simulationsparameter
- **Rechts (Tabs):**
  - **Trajektorien:** Visualisierung der Ion-Pfade (x-z-Projektion)
  - **Stopptiefe-Verteilung:** Histogramm der finalen z-Positionen
  - **Ergebnisse:** Statistische Auswertung (Mittelwert, Standardabweichung, etc.)

**Bedienung:**
1. Parameter nach Bedarf anpassen
2. Performance-Status prüfen (⚡ Cython oder 🐍 Python)
3. Optional: Cython-Toggle verwenden um zwischen Modi zu wechseln
4. "Simulation starten" klicken
5. Fortschritt in Echtzeit verfolgen
6. Ergebnisse in Tabs anschauen (inkl. Performance-Info)
7. Optional: "Ergebnisse exportieren" für Textdatei mit Daten

### Cython-Toggle Feature

**Zur Laufzeit zwischen Cython und Python wechseln:**

- Im Performance-Bereich der GUI finden Sie eine Checkbox "Cython verwenden"
- ⚡ **Cython-Modus** (Grün): ~6.4x schneller, ideal für große Simulationen
- 🐍 **Python-Modus** (Orange): Langsamer, aber besser für Debugging

**Wann welchen Modus verwenden?**
- **Cython** ✓ für: Produktionsläufe, große Simulationen (>100 Ionen), Parameterstudien
- **Python** ✓ für: Debugging, Entwicklung, kleine Tests (<50 Ionen)

Das Umschalten lädt die Module zur Laufzeit neu - keine Neustart erforderlich!

Weitere Details: Siehe [TOGGLE_FEATURE.md](TOGGLE_FEATURE.md)

### Kommandozeilen-Version (Legacy)

Vom Repository‑Wurzelverzeichnis:

```bash
python pytrim/pytrim.py
```

Die Konsole zeigt am Ende u. a. die Anzahl der im Target stoppenden Ionen sowie die mittlere Eindringtiefe und deren Standardabweichung an.

## Konfiguration der Simulation

### GUI-Version
Alle Parameter können bequem über die Benutzeroberfläche eingestellt werden:

**Allgemein:**
- Anzahl Ionen: Wie viele Primärionen simuliert werden sollen

**Target-Geometrie:**
- z_min, z_max: Planare Grenzen des Targets in Å

**Projektil:**
- Z: Ordnungszahl (Atomnummer)
- Masse: Atommasse in amu
- Anfangsenergie: Kinetische Energie in eV
- Startposition: x, y, z Koordinaten in Å
- Richtung: Einheitsvektor (wird automatisch normiert)

**Target-Material:**
- Z: Ordnungszahl des Targetatoms
- Masse: Atommasse in amu
- Dichte: Atomare Dichte in Atome/Å³

**Physik:**
- Lindhard Korrektur: Korrekturfaktor für elektronisches Stopping (typisch 1.0-2.0)

### Kommandozeilen-Version
Die Parameter sind im Kopf von `pytrim/pytrim.py` definiert:
- `nion`: Anzahl zu simulierender Primärionen
- `zmin`, `zmax`: Geometriegrenzen in Å
- `z1`, `m1`: Ordnungszahl und Masse des Projektils
- `z2`, `m2`: Ordnungszahl und Masse des Targets
- `density`: Targetdichte (Atome/Å³)
- `corr_lindhard`: Korrekturfaktor zur Lindhard‑Formel
- Anfangsbedingungen: `e_init` (eV), `pos_init` (Å), `dir_init` (Einheitsvektor)

**Erweiterte Einstellungen:**
- Energieschwelle zum Abbruch pro Ion (`EMIN`) in `pytrim/trajectory.py` (Standard 5 eV)

## Beispiel-Szenarien

### Demo-Skript (Alle Features zeigen)

```bash
python demo_advanced_features.py
```

Demonstriert:
1. Material-Presets laden
2. Verschiedene Geometrien simulieren
3. Export in alle Formate
4. Erweiterte Visualisierungen

### GUI Workflow

**Schnellstart mit Preset:**
1. Erweiterte GUI starten: `./run_extended_gui.sh`
2. **"Preset laden..."** klicken
3. "B in Si" auswählen → OK
4. Ionen-Anzahl anpassen (z.B. 5000)
5. **"🚀 Simulation starten"**
6. Nach Abschluss alle Tabs durchsehen
7. **"💾 Exportieren..."** für Daten-Export

**Custom Geometrie:**
1. **Geometrie-Tab** öffnen
2. Typ wählen: z.B. "cylinder"
3. Parameter eingeben: Radius = 500 Å
4. **Basis-Parameter Tab**: Material einstellen
5. Simulation starten

### Beispiel-Code (Python-API)

```python
from pytrim.simulation import TRIMSimulation, SimulationParameters
from pytrim.presets import get_preset_manager
from pytrim import export

# Methode 1: Preset verwenden
manager = get_preset_manager()
preset = manager.get_preset("B in Si")

params = SimulationParameters()
params.nion = 1000
params.z1 = preset.z1
params.m1 = preset.m1
params.z2 = preset.z2
params.m2 = preset.m2
params.density = preset.density
params.e_init = preset.energy
params.corr_lindhard = preset.corr_lindhard
params.zmin = preset.zmin
params.zmax = preset.zmax

# Methode 2: Custom Geometrie
params.geometry_type = "cylinder"
params.geometry_params = {'radius': 500, 'axis': 'z'}

# Simulation durchführen
sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True, max_trajectories=20)

# Ergebnisse anzeigen
print(results.get_summary())

# Exportieren
export.export_to_json(results, "results.json")
export.export_to_vtk(results, "results.vtk")
```

### Beispiel-Szenario: Nanowire

**Ziel**: Phosphor-Implantation in Silizium-Nanowire

```python
params = SimulationParameters()
params.nion = 2000

# Material (P in Si)
params.z1, params.m1 = 15, 30.974  # P
params.z2, params.m2 = 14, 28.086  # Si
params.density = 0.04994
params.corr_lindhard = 1.5

# Geometrie (Zylindrischer Nanowire)
params.geometry_type = "cylinder"
params.geometry_params = {'radius': 50, 'axis': 'z'}
params.zmin, params.zmax = 0, 3000

# Strahl
params.e_init = 60000  # 60 keV
params.z_init = 0
params.dir_z = 1.0

# Simulieren
sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True)

# Analyse: Wie viele Ionen treffen den Nanowire?
print(f"Im Wire gestoppt: {results.stopped}/{results.nion}")
print(f"Radiale Streuung: {results.mean_r:.1f} ± {results.std_r:.1f} Å")
```

### Standard: Bor in Silizium
- Projektil: B (Z=5, M=11.009 amu)
- Target: Si (Z=14, M=28.086 amu)
- Energie: 50 keV
- Dichte: 0.04994 Atome/Å³ (kristallines Si)
- Erwartete Eindringtiefe: ~2000-2500 Å

### Hochenergie: Arsen in Silizium
- Projektil: As (Z=33, M=74.922 amu)
- Target: Si (Z=14, M=28.086 amu)
- Energie: 100 keV
- Erwartete Eindringtiefe: geringer als bei Bor (schwereres Ion)

## Screenshots & Visualisierung

Die GUI zeigt:
1. **Trajektorien-Plot:** Bis zu 10 Ion-Pfade als farbige Linien mit Targetgrenzen
2. **Histogramm:** Verteilung der Stopptiefen aller Ionen mit Mittelwert-Linie
3. **Ergebnistabelle:** Anzahl gestoppter Ionen, Mittelwert, Standardabweichung, Laufzeit

## Performance

### Cython vs. Pure Python

Benchmark mit 500 Ionen (B in Si, 50 keV):

| Implementation | Zeit | Ionen/Sekunde | Speedup |
|----------------|------|---------------|---------|
| Pure Python    | 14.2s | 35 ions/s    | 1.0x    |
| **Cython**     | **2.2s** | **226 ions/s** | **6.4x** |

**Typische Simulationszeiten (mit Cython):**
- 100 Ionen: ~0.4 s
- 1000 Ionen: ~4.5 s
- 10000 Ionen: ~45 s

**Ohne Cython (Pure Python):**
- 100 Ionen: ~3 s
- 1000 Ionen: ~28 s
- 10000 Ionen: ~280 s (4.7 min)

### Performance-Test ausführen

```bash
# Einfacher Benchmark
python benchmark.py 1000

# Vergleich Python vs Cython
python compare_performance.py

# Test des Cython-Toggle Features
python test_toggle.py
```

### Programmatische Steuerung

Das Cython-Toggle Feature kann auch programmatisch verwendet werden:

```python
from pytrim import (
    is_cython_available,
    is_using_cython, 
    set_use_cython,
    TRIMSimulation,
    SimulationParameters
)

# Prüfe Cython-Verfügbarkeit
if is_cython_available():
    print("Cython-Module verfügbar!")
    
# Wechsle zu Cython für Performance
set_use_cython(True)

# Führe Simulation aus
params = SimulationParameters(n_ions=1000)
sim = TRIMSimulation(params)
results = sim.run()

# Prüfe verwendeten Modus
mode = "Cython" if is_using_cython() else "Python"
print(f"Simulation lief mit: {mode}")
```

Weitere Details: [API.md](API.md) und [TOGGLE_FEATURE.md](TOGGLE_FEATURE.md)

## Annahmen und Grenzen

- Amorphes Target; keine Kristallkanalisation.
- Konstante mittlere freie Weglänge (einfaches Modell; keine Energie‑/Winkelabhängigkeit der Kollisionswahrscheinlichkeit).
- Nur Primärionen werden verfolgt; Rekoilkaskaden werden nicht weiter simuliert.
- Einfache planare Geometrie in z‑Richtung.
- Elektronisches Stopping: Lindhard‑Modell mit globalem Korrekturfaktor.

## Referenzen

- J. F. Ziegler, J. P. Biersack, U. Littmark: The Stopping and Range of Ions in Matter, Pergamon Press, 1985 (ZBL‑Potential).
- J. Lindhard, M. Scharff, H. E. Schiøtt: Range Concepts and Heavy Ion Ranges in Solids, Mat. Fys. Medd. Dan. Vid. Selsk. 33 (1963). Siehe auch Phys. Rev. 124 (1961) 128 für das Stopping‑Modell.
- SRIM/TRIM: https://www.srim.org/

## Lizenz

Siehe `LICENSE` im Repository‑Wurzelverzeichnis.

## Dokumentation

- **[QUICKSTART.md](QUICKSTART.md)**: Schnellstartanleitung für die GUI
- **[API.md](API.md)**: API-Dokumentation für programmatische Nutzung
- **[CYTHON.md](CYTHON.md)**: Technische Details zur Cython-Optimierung
- **[CHANGELOG.md](CHANGELOG.md)**: Übersicht über alle Änderungen und neue Features

## Kontakt & Support

Bei Fragen oder Problemen:
1. Siehe Dokumentation (QUICKSTART.md, README.md)
2. Prüfe bekannte Probleme in QUICKSTART.md
3. Erstelle ein Issue auf GitHub
