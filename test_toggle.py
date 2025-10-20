#!/usr/bin/env python3
"""Test script for Cython toggle feature."""

import sys
from pytrim import is_cython_available, is_using_cython, set_use_cython

def test_toggle():
    """Test the Cython toggle functionality."""
    print("=== Cython Toggle Feature Test ===\n")
    
    # Check if Cython is available
    cython_avail = is_cython_available()
    print(f"1. Cython available: {'✓ Yes' if cython_avail else '✗ No'}")
    
    if not cython_avail:
        print("\n⚠️  Cython modules not available!")
        print("   Run './build_cython.sh' to compile them.\n")
        return False
    
    # Check initial state
    initial_state = is_using_cython()
    print(f"2. Initial status: {'Cython' if initial_state else 'Python'}")
    
    # Test switching to Python
    print("\n3. Switch to Python...")
    success = set_use_cython(False)
    current_state = is_using_cython()
    print(f"   Success: {'✓' if success and not current_state else '✗'}")
    print(f"   Current status: {'Cython' if current_state else 'Python'}")
    
    if current_state:
        print("   ✗ Error: Should be using Python!")
        return False
    
    # Test switching to Cython
    print("\n4. Switch to Cython...")
    success = set_use_cython(True)
    current_state = is_using_cython()
    print(f"   Success: {'✓' if success and current_state else '✗'}")
    print(f"   Current status: {'Cython' if current_state else 'Python'}")
    
    if not current_state:
        print("   ✗ Error: Should be using Cython!")
        return False
    
    # Import test
    print("\n5. Test Module Import...")
    try:
        from pytrim.simulation import TRIMSimulation, SimulationParameters
        print("   ✓ Import successful")
        
        # Create dummy simulation to verify modules work
        params = SimulationParameters()
        sim = TRIMSimulation(params)
        print("   ✓ Simulation object created")
        
    except Exception as e:
        print(f"   ✗ Import error: {e}")
        return False
    
    # Restore initial state
    print(f"\n6. Stelle initialen Status wieder her...")
    set_use_cython(initial_state)
    final_state = is_using_cython()
    print(f"   Status: {'Cython' if final_state else 'Python'}")
    
    if final_state != initial_state:
        print("   ⚠️  Warnung: Konnte initialen Status nicht wiederherstellen")
    
    print("\n=== All Tests Successful! ✓ ===\n")
    return True

if __name__ == "__main__":
    success = test_toggle()
    sys.exit(0 if success else 1)
