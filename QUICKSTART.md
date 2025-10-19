# PyTRIM GUI - Schnellstart

## Installation (einmalig)

```bash
# Virtuelle Umgebung erstellen
python3 -m venv .venv

# Abhängigkeiten installieren
.venv/bin/pip install -r requirements.txt

# OPTIONAL aber EMPFOHLEN: Cython-Optimierung für 6.4x schnellere Simulation
./build_cython.sh
```

**Hinweis:** Falls Cython-Kompilation fehlschlägt, funktioniert das Programm trotzdem (mit Pure Python, ca. 6x langsamer).

## Starten der GUI

### Option 1: Startskript (Linux/Mac)
```bash
./run_gui.sh
```

### Option 2: Manuell
```bash
# Virtuelle Umgebung aktivieren
source .venv/bin/activate  # Linux/Mac
# oder
.venv\Scripts\activate     # Windows

# GUI starten
python pytrim_gui.py
```

## Bedienung

1. **Parameter einstellen** (linke Seite)
   - Anzahl Ionen (z.B. 1000 für schnellen Test, 10000 für genauere Statistik)
   - Projektil-Eigenschaften (Z, Masse, Energie)
   - Target-Eigenschaften (Z, Masse, Dichte, Geometrie)
   
2. **Simulation starten**
   - Button "Simulation starten" klicken
   - Fortschritt wird angezeigt
   - Simulation kann mit "Stoppen" abgebrochen werden

3. **Ergebnisse ansehen**
   - **Tab "Trajektorien"**: Visualisierung der Ion-Pfade (erste 10 Ionen)
   - **Tab "Stopptiefe-Verteilung"**: Histogramm aller finalen Positionen
   - **Tab "Ergebnisse"**: Statistische Auswertung

4. **Daten exportieren**
   - Button "Ergebnisse exportieren"
   - Textdatei mit allen Stopptiefen

## Beispiel-Szenarien

### Test (schnell)
- Anzahl Ionen: 100
- Projektil: B (Z=5, M=11), Energie: 50000 eV
- Target: Si (Z=14, M=28.086, Dichte=0.04994)
- Dauer mit Cython: ~0.4 Sekunden
- Dauer ohne Cython: ~3 Sekunden

### Standard-Simulation
- Anzahl Ionen: 1000
- Dauer mit Cython: ~4.5 Sekunden
- Dauer ohne Cython: ~28 Sekunden

### Hohe Genauigkeit
- Anzahl Ionen: 10000
- Dauer mit Cython: ~45 Sekunden
- Dauer ohne Cython: ~4.7 Minuten

## Tipps

- **Trajektorien-Anzeige**: Nur die ersten 10 Ionen werden gezeichnet (Performance)
- **Histogramm**: Zeigt ALLE simulierten Ionen
- **Zoom/Pan**: Nutze die Toolbar unter den Plots
- **Parameter-Voreinstellungen**: Standard-Werte sind für B in Si bei 50 keV optimiert

## Häufige Probleme

**GUI startet nicht**: 
```bash
# Prüfe ob PyQt6 installiert ist
.venv/bin/pip list | grep PyQt6

# Falls nicht, neu installieren
.venv/bin/pip install PyQt6 matplotlib
```

**Simulation sehr langsam**:
```bash
# Prüfe ob Cython aktiv ist
.venv/bin/python -c "from pytrim.simulation import is_using_cython; print('Cython:', is_using_cython())"

# Falls False, kompiliere Cython-Module:
./build_cython.sh

# Performance-Vergleich:
.venv/bin/python compare_performance.py
```

**Cython-Kompilation schlägt fehl**:
- Stelle sicher dass ein C-Compiler installiert ist (gcc auf Linux, Xcode auf Mac, Visual Studio auf Windows)
- Das Programm funktioniert trotzdem mit Pure Python (nur langsamer)
- Alternative: Reduziere Anzahl Ionen für akzeptable Laufzeit

**"Richtungsvektor kann nicht null sein"**:
- Mindestens eine Komponente von (dir_x, dir_y, dir_z) muss != 0 sein
- Wird automatisch normiert
