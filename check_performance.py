#!/usr/bin/env python
"""Test script to verify performance indicator."""
from pytrim.simulation import is_using_cython

print("=" * 60)
print("CyTRIM Performance Status")
print("=" * 60)

using_cython = is_using_cython()

if using_cython:
    print("✓ Cython ist AKTIVIERT")
    print("  → ~6.4x schnellere Simulation")
    print("  → Optimierte C-Extensions geladen")
    print("  → Status in GUI: ⚡ Cython aktiviert")
else:
    print("⚠ Python Fallback aktiv")
    print("  → Normale Geschwindigkeit")
    print("  → Für bessere Performance:")
    print("    ./build_cython.sh")
    print("  → Status in GUI: 🐍 Python Fallback")

print("=" * 60)
