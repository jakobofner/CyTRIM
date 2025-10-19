#!/bin/bash
# Quick Demo Script für Cython Toggle Feature

echo "================================================"
echo "  CyTRIM - Cython Toggle Feature Demo"
echo "================================================"
echo ""

# Check if Cython is available
echo "1. Prüfe Cython-Verfügbarkeit..."
python -c "from pytrim import is_cython_available; print('   ✓ Cython ist verfügbar' if is_cython_available() else '   ✗ Cython nicht kompiliert')"
echo ""

# Run toggle test
echo "2. Führe automatischen Toggle-Test aus..."
python test_toggle.py
echo ""

# Show current status
echo "3. Aktueller Status:"
python -c "from pytrim import is_using_cython; print('   Modus: ⚡ Cython' if is_using_cython() else '   Modus: 🐍 Python')"
echo ""

# Quick benchmark comparison
echo "4. Quick Performance-Vergleich (100 Ionen):"
echo ""
echo "   Testing Python mode..."
python -c "
import time
from pytrim import set_use_cython, TRIMSimulation, SimulationParameters

set_use_cython(False)
params = SimulationParameters(n_ions=100)
sim = TRIMSimulation(params)

t1 = time.time()
results = sim.run()
t_python = time.time() - t1

print(f'   🐍 Python: {t_python:.2f}s ({100/t_python:.1f} ions/s)')

set_use_cython(True)
sim2 = TRIMSimulation(params)

t2 = time.time()
results2 = sim2.run()
t_cython = time.time() - t2

print(f'   ⚡ Cython: {t_cython:.2f}s ({100/t_cython:.1f} ions/s)')
print(f'   Speedup: {t_python/t_cython:.1f}x')
"
echo ""

echo "5. GUI starten (schließen Sie das Fenster zum Beenden)..."
echo "   Tipp: Testen Sie den Toggle im Performance-Bereich!"
echo ""
read -p "   Drücke Enter zum Starten..."

python pytrim_gui.py

echo ""
echo "================================================"
echo "  Demo abgeschlossen!"
echo "================================================"
