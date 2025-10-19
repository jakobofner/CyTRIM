# PyTRIM API-Dokumentation

## Programmatische Nutzung

Falls Sie die Simulation in eigenen Python-Skripten verwenden möchten:

```python
from pytrim.simulation import TRIMSimulation, SimulationParameters

# Parameter erstellen und anpassen
params = SimulationParameters()
params.nion = 1000
params.z1 = 5          # Bor
params.m1 = 11.009
params.z2 = 14         # Silizium
params.m2 = 28.086
params.e_init = 50000  # 50 keV
params.density = 0.04994
params.zmin = 0.0
params.zmax = 4000.0

# Simulation erstellen und ausführen
sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True, max_trajectories=10)

# Ergebnisse auswerten
print(f"Gestoppte Ionen: {results.count_inside} / {results.total_ions}")
print(f"Mittlere Tiefe: {results.mean_z:.2f} Å")
print(f"Standardabweichung: {results.std_z:.2f} Å")
print(f"Laufzeit: {results.simulation_time:.2f} s")

# Zugriff auf Rohdaten
depths = results.stopped_depths  # Liste aller z-Koordinaten
trajectories = results.trajectories  # Liste von Trajektorien (Liste von Positionen)
```

## Klassen

### SimulationParameters

Enthält alle Simulationsparameter:

**Allgemein:**
- `nion` (int): Anzahl zu simulierender Ionen

**Target-Geometrie:**
- `zmin` (float): Minimale z-Koordinate (Å)
- `zmax` (float): Maximale z-Koordinate (Å)

**Projektil:**
- `z1` (int): Ordnungszahl
- `m1` (float): Masse (amu)
- `e_init` (float): Anfangsenergie (eV)
- `x_init`, `y_init`, `z_init` (float): Startposition (Å)
- `dir_x`, `dir_y`, `dir_z` (float): Richtungsvektor (wird normiert)

**Target:**
- `z2` (int): Ordnungszahl
- `m2` (float): Masse (amu)
- `density` (float): Atomare Dichte (Atome/Å³)

**Physik:**
- `corr_lindhard` (float): Korrekturfaktor für Lindhard-Stopping

**Methoden:**
- `get_pos_init()`: Gibt Startposition als numpy-Array zurück
- `get_dir_init()`: Gibt Richtung als numpy-Array zurück

### TRIMSimulation

Hauptklasse für die Simulation.

**Konstruktor:**
```python
sim = TRIMSimulation(params=None)
```
- `params`: SimulationParameters-Objekt (optional, sonst Standard)

**Methoden:**

`run(record_trajectories=False, max_trajectories=10)`
- Führt die Simulation aus
- `record_trajectories`: Trajektorien aufzeichnen (langsamer)
- `max_trajectories`: Maximale Anzahl aufzuzeichnender Trajektorien
- Gibt SimulationResults zurück

`set_progress_callback(callback)`
- Setzt Callback-Funktion für Fortschritt
- Callback erhält `(current, total)` als Parameter

`stop()`
- Stoppt laufende Simulation

### SimulationResults

Enthält Simulationsergebnisse:

**Attribute:**
- `count_inside` (int): Anzahl im Target gestoppter Ionen
- `total_ions` (int): Gesamtzahl simulierter Ionen
- `mean_z` (float): Mittlere Stopptiefe (Å)
- `std_z` (float): Standardabweichung der Stopptiefe (Å)
- `simulation_time` (float): Laufzeit (Sekunden)
- `stopped_depths` (list): Liste aller Stopptiefen (z-Koordinaten)
- `trajectories` (list): Liste von Trajektorien (wenn aufgezeichnet)

**Methoden:**

`get_summary()`
- Gibt Zusammenfassung als String zurück

## Beispiele

### Einfache Simulation

```python
from pytrim.simulation import TRIMSimulation, SimulationParameters

# Standard-Parameter verwenden
sim = TRIMSimulation()
results = sim.run()
print(results.get_summary())
```

### Mit Fortschrittsanzeige

```python
from pytrim.simulation import TRIMSimulation, SimulationParameters

def progress(current, total):
    percent = 100 * current / total
    print(f"\rFortschritt: {percent:.1f}%", end="")

params = SimulationParameters()
params.nion = 1000

sim = TRIMSimulation(params)
sim.set_progress_callback(progress)
results = sim.run()
print("\n" + results.get_summary())
```

### Trajektorien visualisieren

```python
import matplotlib.pyplot as plt
import numpy as np
from pytrim.simulation import TRIMSimulation, SimulationParameters

params = SimulationParameters()
params.nion = 100
sim = TRIMSimulation(params)
results = sim.run(record_trajectories=True, max_trajectories=10)

# Trajektorien plotten
fig, ax = plt.subplots()
for traj in results.trajectories:
    if traj:
        traj_array = np.array(traj)
        ax.plot(traj_array[:, 2], traj_array[:, 0], alpha=0.6)

ax.axvline(params.zmin, color='r', linestyle='--')
ax.axvline(params.zmax, color='r', linestyle='--')
ax.set_xlabel('z (Å)')
ax.set_ylabel('x (Å)')
ax.set_title('Ion Trajektorien')
plt.show()
```

### Histogramm der Stopptiefen

```python
import matplotlib.pyplot as plt
from pytrim.simulation import TRIMSimulation, SimulationParameters

params = SimulationParameters()
params.nion = 1000
sim = TRIMSimulation(params)
results = sim.run()

# Histogramm
plt.hist(results.stopped_depths, bins=50, edgecolor='black')
plt.axvline(results.mean_z, color='r', linestyle='--', 
            label=f'Mittelwert: {results.mean_z:.1f} Å')
plt.xlabel('Stopptiefe (Å)')
plt.ylabel('Anzahl Ionen')
plt.title('Verteilung der Stopptiefen')
plt.legend()
plt.show()
```

### Energiescan

```python
import numpy as np
import matplotlib.pyplot as plt
from pytrim.simulation import TRIMSimulation, SimulationParameters

energies = [10000, 20000, 30000, 50000, 75000, 100000]
mean_depths = []
std_depths = []

for energy in energies:
    params = SimulationParameters()
    params.nion = 1000
    params.e_init = energy
    
    sim = TRIMSimulation(params)
    results = sim.run()
    
    mean_depths.append(results.mean_z)
    std_depths.append(results.std_z)
    print(f"{energy/1000:.0f} keV: {results.mean_z:.1f} ± {results.std_z:.1f} Å")

# Plot
plt.errorbar(np.array(energies)/1000, mean_depths, yerr=std_depths, 
             marker='o', capsize=5)
plt.xlabel('Energie (keV)')
plt.ylabel('Mittlere Eindringtiefe (Å)')
plt.title('Eindringtiefe vs. Energie (B in Si)')
plt.grid(True, alpha=0.3)
plt.show()
```

## Erweiterte Konfiguration

### Energieschwelle ändern

Die minimale Energie, bei der Ionen als gestoppt gelten:

```python
import pytrim.trajectory as traj
traj.EMIN = 10.0  # Standard: 5.0 eV
```

**Hinweis:** Dies sollte vor dem ersten `setup()`-Aufruf geschehen.

### Andere Materialien

Typische Dichte-Werte (Atome/Å³):

- Si (kristallin): 0.04994
- Si (amorph): 0.049
- GaAs: 0.044
- SiO₂: 0.066
- Al: 0.0603
- Cu: 0.0845

Ordnungszahlen und Massen häufiger Elemente:

| Element | Z  | M (amu) |
|---------|----|---------| 
| B       | 5  | 10.81   |
| N       | 7  | 14.007  |
| P       | 15 | 30.974  |
| As      | 33 | 74.922  |
| Si      | 14 | 28.086  |
| Ga      | 31 | 69.723  |
| Ar      | 18 | 39.948  |

## Performance-Hinweise

- Simulationszeit skaliert linear mit `nion`
- Trajektorien-Aufzeichnung verlangsamt Simulation (~10-20%)
- Höhere Energien = längere Trajektorien = längere Laufzeit
- Niedrigere Dichte = größere freie Weglänge = längere Laufzeit

Typische Laufzeiten (Intel i5, Python):
- 100 Ionen: ~0.5 s
- 1000 Ionen: ~5 s
- 10000 Ionen: ~50 s
