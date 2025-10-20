# Cython Toggle Feature

## Übersicht

Die neue Toggle-Funktion ermöglicht es Benutzern, zur Laufzeit zwischen Cython-optimierten und Python-Modulen zu wechseln, ohne die Anwendung neu zu starten.

## Funktionen

### 1. Performance-Status-Anzeige
- **⚡ Cython aktiviert** (Grün): Cython-Module werden verwendet (~6.4x schneller)
- **🐍 Python Modus** (Orange): Python-Module werden verwendet

### 2. Cython-Toggle Checkbox
- Ermöglicht das Umschalten zwischen Cython und Python
- Zeigt Tooltip mit Performance-Informationen
- Wird während laufender Simulationen automatisch deaktiviert

### 3. Dynamisches Modul-Neuladen
- Module werden zur Laufzeit gewechselt
- Warnung bei bestehendem Simulationsergebnis
- Automatische Validierung der Cython-Availablekeit

## Verwendung

### Im GUI
1. Starte die Anwendung: `python pytrim_gui.py`
2. Finde die Performance-Anzeige im linken Panel
3. Aktiviere/Deaktiviere die Checkbox "Cython verwenden"
4. Bestätige die Warnung zum Neuladen der Module
5. Neue Simulationen verwenden nun die gewählten Module

### Programmatisch

```python
from pytrim import is_cython_available, set_use_cython, is_using_cython

# Prüfe, ob Cython available ist
if is_cython_available():
    print("Cython-Module sind kompiliert und available")

# Wechsle zu Cython
success = set_use_cython(True)
if success:
    print("Erfolgreich zu Cython gewechselt")

# Prüfe aktuellen Status
if is_using_cython():
    print("Nutze Cython-Module")
else:
    print("Nutze Python-Module")
```

## Technical Details

### Module System
- **Dynamisches Laden**: Module werden zur Laufzeit aus `cytrim.*` oder `pytrim.*` importiert
- **Globale Referenzen**: Alle Module werden als globale Variablen gespeichert
- **Fallback-Mechanismus**: Automatischer Fallback zu Python bei Cython-Fehlern

### Betroffene Module
- `estop` - Electronic stopping power
- `scatter` - Scattering calculations
- `geometry` - Geometric utilities
- `select_recoil` - Recoil selection
- `trajectory` - Trajectory calculation

### GUI Integration
- Toggle wird während Simulationen deaktiviert
- Status-Label aktualisiert sich automatisch
- Bestätigungsdialog bei bestehendem Result
- Fehlermeldung bei nicht availableem Cython

## Performance

### Benchmark-Resultse (500 Ionen)
- **Cython**: 2.2 Sekunden (~226 Ionen/Sekunde)
- **Python**: 14.2 Sekunden (~35 Ionen/Sekunde)
- **Speedup**: 6.4x

### Wann Cython verwenden?
✅ **Große Simulationen** (>100 Ionen)
✅ **Produktionsläufe** mit vielen Wiederholungen
✅ **Parametersstudien** mit vielen Konfigurationen

### Wann Python verwenden?
✅ **Debugging** mit detaillierten Stack Traces
✅ **Entwicklung** ohne Neucompilierung
✅ **Kleine Tests** (<50 Ionen)

## Troubleshooting

### Cython nicht available
```bash
# Kompiliere Cython-Module
./build_cython.sh

# Prüfe Installation
python -c "from pytrim import is_cython_available; print(is_cython_available())"
```

### Module werden nicht geladen
```bash
# Bereinige Build-Artefakte
./build_cython.sh clean

# Neucompilierung
./build_cython.sh
```

### Toggle funktioniert nicht
1. Prüfe, ob Simulation läuft (Toggle ist dann deaktiviert)
2. Check Cython availability mit `is_cython_available()`
3. Prüfe Konsolen-Output für Fehler

## Implementierungsdetails

### Dateien
- `pytrim/simulation.py`: Dynamisches Modul-System
- `pytrim_gui.py`: GUI-Integration (Toggle, Status-Anzeige)
- `pytrim/__init__.py`: API-Export

### Neue API-Funktionen
```python
# In pytrim/__init__.py exportiert:
is_cython_available() -> bool
is_using_cython() -> bool
set_use_cython(use_cython: bool) -> bool
```

### GUI-Methoden
```python
class MainWindow:
    def update_performance_label(self) -> None
    def toggle_cython(self, state: Qt.CheckState) -> None
```

## Future Extensions

- [ ] Automatische Performance-Messung für Empfehlung
- [ ] Persistente Speicherung der Toggle-Einstellung
- [ ] Batch-Modus für automatische Cython-Auswahl
- [ ] Performance-Vergleichs-Tool

## Changelog

### v1.0 - Initial Implementation
- Dynamisches Modul-System implementiert
- GUI-Toggle mit Checkbox hinzugefügt
- Performance-Status-Anzeige erstellt
- Bestätigungsdialoge für Benutzersicherheit
- Automatische Deaktivierung während Simulationen
