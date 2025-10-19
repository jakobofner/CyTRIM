# GUI-Layout und Performance-Anzeige

## Hauptfenster-Layout

```
┌────────────────────────────────────────────────────────────────┐
│  PyTRIM - Ion Transport Simulation                             │
├─────────────────────┬──────────────────────────────────────────┤
│                     │                                          │
│ PARAMETER           │  VISUALISIERUNG                          │
│ ┌─────────────────┐ │  ┌────────────────────────────────────┐ │
│ │ Anzahl Ionen    │ │  │ Tab: Trajektorien                  │ │
│ │ Target z_min/max│ │  │                                    │ │
│ │ Projektil Z, M  │ │  │  [Trajektorien-Plot]               │ │
│ │ Target Z, M     │ │  │                                    │ │
│ │ Dichte          │ │  │                                    │ │
│ │ Energie         │ │  └────────────────────────────────────┘ │
│ │ Position        │ │                                          │
│ │ Richtung        │ │  Tab: Stopptiefe-Verteilung              │
│ └─────────────────┘ │  Tab: Ergebnisse                         │
│                     │                                          │
│ STEUERUNG           │                                          │
│ ┌─────────────────┐ │                                          │
│ │ [Simulation    ]│ │                                          │
│ │  starten        │ │                                          │
│ │ [Stoppen]       │ │                                          │
│ │ [Exportieren]   │ │                                          │
│ └─────────────────┘ │                                          │
│                     │                                          │
│ FORTSCHRITT         │                                          │
│ ┌─────────────────┐ │                                          │
│ │ [████████░░] 80%│ │                                          │
│ │ Ion 800 / 1000  │ │                                          │
│ └─────────────────┘ │                                          │
│                     │                                          │
│ PERFORMANCE ★       │                                          │
│ ┌─────────────────┐ │                                          │
│ │ ⚡ Cython        │ │  ← MIT CYTHON                            │
│ │    aktiviert    │ │                                          │
│ │ ~6.4x schneller │ │                                          │
│ └─────────────────┘ │                                          │
│   ODER              │                                          │
│ ┌─────────────────┐ │                                          │
│ │ 🐍 Python        │ │  ← OHNE CYTHON                           │
│ │    Fallback     │ │                                          │
│ │ Für mehr Speed: │ │                                          │
│ │ ./build_cython  │ │                                          │
│ └─────────────────┘ │                                          │
└─────────────────────┴──────────────────────────────────────────┘
```

## Performance-Anzeige Details

### Mit Cython (optimiert)
```
┌────────────────────┐
│ Performance        │
├────────────────────┤
│ ⚡ Cython aktiviert │  ← Grüne Schrift
│ ~6.4x schneller    │
└────────────────────┘
```

### Ohne Cython (Fallback)
```
┌────────────────────┐
│ Performance        │
├────────────────────┤
│ 🐍 Python Fallback │  ← Orange Schrift
│ Für mehr Speed:    │
│ ./build_cython.sh  │
└────────────────────┘
```

## Ergebnisse-Tab (mit Performance-Info)

```
Number of ions stopped inside the target: 996 / 1000
Mean penetration depth: 1731.33 A
Standard deviation: 527.95 A
Simulation time: 4.53 seconds
==================================================
Performance-Modus: Cython (optimiert)          ← NEU!
Durchsatz: 220.9 Ionen/Sekunde                  ← NEU!
```

## Visuelles Feedback

### Farb-Kodierung
- **⚡ Grün (#2ecc71)**: Cython aktiv, beste Performance
- **🐍 Orange (#f39c12)**: Python Fallback, Hinweis auf Optimierungspotential

### Icons
- **⚡**: Blitz-Symbol für schnelle Cython-Performance
- **🐍**: Python-Logo für Fallback-Modus

## Status-Prüfung per Kommandozeile

```bash
# Performance-Status prüfen
python check_performance.py

# Ausgabe bei aktivem Cython:
# ============================================================
# CyTRIM Performance Status
# ============================================================
# ✓ Cython ist AKTIVIERT
#   → ~6.4x schnellere Simulation
#   → Optimierte C-Extensions geladen
#   → Status in GUI: ⚡ Cython aktiviert
# ============================================================
```
