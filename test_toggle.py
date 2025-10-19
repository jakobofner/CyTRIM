#!/usr/bin/env python3
"""Test script for Cython toggle feature."""

import sys
from pytrim import is_cython_available, is_using_cython, set_use_cython

def test_toggle():
    """Test the Cython toggle functionality."""
    print("=== Cython Toggle Feature Test ===\n")
    
    # Check if Cython is available
    cython_avail = is_cython_available()
    print(f"1. Cython verfügbar: {'✓ Ja' if cython_avail else '✗ Nein'}")
    
    if not cython_avail:
        print("\n⚠️  Cython-Module nicht verfügbar!")
        print("   Führe './build_cython.sh' aus um sie zu kompilieren.\n")
        return False
    
    # Check initial state
    initial_state = is_using_cython()
    print(f"2. Initialer Status: {'Cython' if initial_state else 'Python'}")
    
    # Test switching to Python
    print("\n3. Wechsel zu Python...")
    success = set_use_cython(False)
    current_state = is_using_cython()
    print(f"   Erfolg: {'✓' if success and not current_state else '✗'}")
    print(f"   Aktueller Status: {'Cython' if current_state else 'Python'}")
    
    if current_state:
        print("   ✗ Fehler: Sollte Python verwenden!")
        return False
    
    # Test switching to Cython
    print("\n4. Wechsel zu Cython...")
    success = set_use_cython(True)
    current_state = is_using_cython()
    print(f"   Erfolg: {'✓' if success and current_state else '✗'}")
    print(f"   Aktueller Status: {'Cython' if current_state else 'Python'}")
    
    if not current_state:
        print("   ✗ Fehler: Sollte Cython verwenden!")
        return False
    
    # Import test
    print("\n5. Test Module-Import...")
    try:
        from pytrim.simulation import TRIMSimulation, SimulationParameters
        print("   ✓ Import erfolgreich")
        
        # Create dummy simulation to verify modules work
        params = SimulationParameters()
        sim = TRIMSimulation(params)
        print("   ✓ Simulation-Objekt erstellt")
        
    except Exception as e:
        print(f"   ✗ Fehler beim Import: {e}")
        return False
    
    # Restore initial state
    print(f"\n6. Stelle initialen Status wieder her...")
    set_use_cython(initial_state)
    final_state = is_using_cython()
    print(f"   Status: {'Cython' if final_state else 'Python'}")
    
    if final_state != initial_state:
        print("   ⚠️  Warnung: Konnte initialen Status nicht wiederherstellen")
    
    print("\n=== Alle Tests erfolgreich! ✓ ===\n")
    return True

if __name__ == "__main__":
    success = test_toggle()
    sys.exit(0 if success else 1)
