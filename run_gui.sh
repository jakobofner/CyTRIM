#!/bin/bash
# Startskript für PyTRIM GUI

# Prüfe ob virtuelle Umgebung existiert
if [ ! -d ".venv" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv .venv
    
    echo "Installiere Abhängigkeiten..."
    .venv/bin/pip install -q --upgrade pip
    .venv/bin/pip install -q -r requirements.txt
    
    echo "Kompiliere Cython-Module für beste Performance..."
    ./build_cython.sh
fi

# Prüfe ob Cython-Module existieren
if [ ! -f "cytrim/estop.*.so" ] && [ -f "cytrim/estop.pyx" ]; then
    echo "Cython-Module nicht gefunden. Kompiliere..."
    ./build_cython.sh
fi

# Aktiviere Umgebung und starte GUI
echo "Starte PyTRIM GUI..."
.venv/bin/python pytrim_gui.py
