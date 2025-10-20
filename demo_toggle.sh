#!/bin/bash
# Quick Demo Script for Cython Toggle Feature

echo "================================================"
echo "  CyTRIM - Cython Toggle Feature Demo"
echo "================================================"
echo ""

# Check if Cython is available
echo "1. Check Cython availability..."
python -c "from pytrim import is_cython_available; print('   ✓ Cython is available' if is_cython_available() else '   ✗ Cython not compiled')"
echo ""

# Run toggle test
echo "2. Run automatic toggle test..."
python test_toggle.py
echo ""

# Show current status
echo "3. Current status:"
python -c "from pytrim import is_using_cython; print('   Mode: ⚡ Cython' if is_using_cython() else '   Mode: 🐍 Python')"
echo ""

# Quick benchmark comparison
echo "4. Quick performance comparison (100 ions):"
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

echo "5. Start GUI (close window to exit)..."
echo "   Tip: Test the toggle in the performance section!"
echo ""
read -p "   Press Enter to start..."

python pytrim_gui.py

echo ""
echo "================================================"
echo "  Demo completed!"
echo "================================================"
