# Cython-Optimierung - Technische Dokumentation

## Übersicht

CyTRIM nutzt Cython um rechenintensive Python-Module in optimierten C-Code zu übersetzen. Dies führt zu einer **6.4x Velocityssteigerung** ohne Änderung der Benutzeroberfläche oder API.

## Performance-Verbesserungen

### Benchmark-Resultse (500 Ionen, B in Si, 50 keV)

| Metrik | Pure Python | Cython | Verbesserung |
|--------|-------------|--------|--------------|
| Gesamtzeit | 14.17 s | 2.21 s | **6.4x** |
| Ionen/Sekunde | 35.3 | 226.0 | **6.4x** |
| Zeit pro Ion | 28.3 ms | 4.4 ms | **6.4x** |

### Skalierung

| Anzahl Ionen | Python | Cython | Zeitersparnis |
|--------------|--------|--------|---------------|
| 100 | ~3 s | ~0.4 s | 2.6 s |
| 1000 | ~28 s | ~4.5 s | 23.5 s |
| 10000 | ~280 s | ~45 s | **235 s** (3.9 min) |

## Optimierte Module

### 1. `cytrim/estop.pyx` - Elektronisches Stopping
**Optimierungen:**
- `cpdef` für öffentliche Funktionen (C-API + Python-Wrapper)
- `cdef double` für alle Variablen
- `sqrt()` aus `libc.math` statt Python `math.sqrt()`
- Inline-Berechnungen statt Python-Operationen

**Speedup:** ~5-6x

### 2. `cytrim/scatter.pyx` - ZBL-Scattering  
**Optimierungen:**
- `cdef inline ... nogil` für interne Funktionen
- Statische Typisierung aller Variablen
- Vermeidung von Python-Objekten in inneren Schleifen
- Direkte Array-Indexierung ohne Bounds-Checking
- C-math-Funktionen (`exp`, `sqrt`)

**Speedup:** ~8-10x (wichtigster Flaschenhals)

### 3. `cytrim/trajectory.pyx` - Trajektorien
**Optimierungen:**
- Typed numpy arrays (`cnp.ndarray[cnp.float64_t, ndim=1]`)
- `cimport` für schnelle Aufrufe anderer Cython-Module
- Vermeidung von Python-Listen in innerer Schleife

**Speedup:** ~6-7x

### 4. `cytrim/select_recoil.pyx` - Kollisionsgeometrie
**Optimierungen:**
- Trigonometrische Funktionen aus `libc.math`
- Vermeidung von Python-Overhead bei Zufallszahlen
- Inline-Berechnungen

**Speedup:** ~4-5x

### 5. `cytrim/geometry.pyx` - Target-Geometrie
**Optimierungen:**
- Einfache `cpdef` mit direktem Array-Zugriff
- Keine Python-Objekte

**Speedup:** ~3-4x

## Compiler-Direktiven

```python
# cython: language_level=3        # Python 3 Syntax
# cython: boundscheck=False       # Keine Array-Grenzen-Prüfung
# cython: wraparound=False        # Kein negative Indexing
# cython: cdivision=True          # C-Division (schneller, kein ZeroDivisionError)
```

## Compiler-Flags

### Linux/macOS
```bash
-O3                # Maximale Optimierung
-ffast-math        # Schnelle Math-Operationen
-march=native      # CPU-spezifische Optimierungen
```

### Windows (MSVC)
```bash
/O2                # Maximale Optimierung
```

## Build-Prozess

### Automatischer Build
```bash
./build_cython.sh
```

### Manueller Build
```bash
# Installation
pip install Cython numpy

# Kompilation
python setup.py build_ext --inplace

# Test
python -c "from pytrim.simulation import is_using_cython; print('Cython:', is_using_cython())"
```

### Ausgabe
```
cytrim/estop.cpython-312-x86_64-linux-gnu.so
cytrim/scatter.cpython-312-x86_64-linux-gnu.so
cytrim/geometry.cpython-312-x86_64-linux-gnu.so
cytrim/select_recoil.cpython-312-x86_64-linux-gnu.so
cytrim/trajectory.cpython-312-x86_64-linux-gnu.so
```

## Architektur

### Import-Mechanismus
```python
# In pytrim/simulation.py
try:
    from cytrim import select_recoil  # Versuche Cython
    from cytrim import scatter
    # ...
    _using_cython = True
except ImportError:
    from . import select_recoil        # Fallback Python
    from . import scatter
    # ...
    _using_cython = False
```

### Vorteile
- ✅ Automatischer Fallback auf Python
- ✅ Keine Code-Duplikation für Nutzer
- ✅ Transparente Nutzung
- ✅ Gleiche API für beide Versionen

## Debugging

### Cython-Annotationen ansehen
```bash
# Generiert .html Dateien mit Performance-Hinweisen
python setup.py build_ext --inplace

# Öffne z.B. cytrim/scatter.html im Browser
# Gelbe Zeilen = Python-Overhead
# Weiße Zeilen = Pure C-Code
```

### Performance-Profiling
```bash
# Mit cProfile
python -m cProfile -s cumtime benchmark.py 1000

# Mit line_profiler (für .pyx Dateien)
kernprof -l -v benchmark.py
```

## Häufige Probleme

### "ModuleNotFoundError: No module named 'cytrim.estop'"
**Ursache:** Cython-Module nicht kompiliert

**Lösung:**
```bash
./build_cython.sh
```

### Build schlägt fehl: "error: Microsoft Visual C++ 14.0 or greater is required"
**Ursache:** Kein C-Compiler (Windows)

**Lösung:**
- Installiere Visual Studio Build Tools
- ODER nutze Pure Python (automatischer Fallback)

### Build schlägt fehl: "gcc: command not found"
**Ursache:** Kein C-Compiler (Linux)

**Lösung:**
```bash
sudo apt install build-essential python3-dev  # Debian/Ubuntu
sudo yum install gcc python3-devel            # RedHat/CentOS
```

### "ImportError: numpy._core.multiarray failed to import"
**Ursache:** Numpy-Versionsinkompatibilität

**Lösung:**
```bash
pip install --upgrade numpy
python setup.py build_ext --inplace
```

## Weiterentwicklung

### Weitere Optimierungsmöglichkeiten

1. **OpenMP-Parallelisierung**
   - Parallelisierung der Ionen-Schleife
   - Potential: 4-8x zusätzlicher Speedup

2. **Memory Views statt NumPy Arrays**
   - Noch schnellerer Array-Zugriff
   - Potential: 10-20% Verbesserung

3. **Custom Random Number Generator**
   - C-RNG statt Python `random`
   - Potential: 5-10% Verbesserung

4. **GPU-Beschleunigung (CUDA/OpenCL)**
   - Massive Parallelisierung
   - Potential: 100-1000x für große Simulationen

## Vergleich mit anderen Technologien

| Technologie | Speedup | Aufwand | Portabilität |
|-------------|---------|---------|--------------|
| Pure Python | 1.0x | - | ✅ Sehr gut |
| **Cython** | **6.4x** | ⭐ Mittel | ✅ Gut |
| Numba JIT | 3-5x | ⭐⭐ Niedrig | ✅ Gut |
| PyPy | 2-4x | ⭐⭐⭐ Sehr niedrig | ⚠️ Mittel |
| C++ (pybind11) | 8-15x | ⭐ Hoch | ⚠️ Mittel |
| CUDA/OpenCL | 100-1000x | ⭐ Sehr hoch | ❌ Niedrig |

**Warum Cython?**
- ✅ Guter Kompromiss aus Performance und Aufwand
- ✅ Volle Kontrolle über Optimierungen
- ✅ Einfache Integration in bestehendes Python
- ✅ Automatischer Fallback möglich
- ✅ Breite Plattform-Unterstützung

## Benchmarking-Tools

### Einfacher Test
```bash
python benchmark.py 1000
```

### Vergleich
```bash
python compare_performance.py
```

### Detailliert mit cProfile
```bash
python -m cProfile -o profile.stats benchmark.py 1000
python -m pstats profile.stats
# Im pstats-Prompt:
stats 20
```

## Zusammenfassung

**Cython-Optimierung für CyTRIM:**
- ✅ **6.4x schneller** als Pure Python
- ✅ Gleiche API und Benutzeroberfläche
- ✅ Automatischer Fallback bei Build-Problemen
- ✅ Einfaches Build-System
- ✅ Keine Änderungen am GUI-Code nötig
- ✅ Transparente Integration

**Empfehlung:** Immer Cython verwenden wenn C-Compiler available!
