#!/bin/bash
# Quick build and test script for CyTRIM with OpenMP

echo "=================================="
echo "CyTRIM OpenMP Build & Test"
echo "=================================="
echo ""

# Clean previous builds
echo "Step 1: Cleaning previous builds..."
./build_cython.sh clean
echo ""

# Build with OpenMP
echo "Step 2: Building Cython + OpenMP modules..."
./build_cython.sh
if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi
echo ""

# Verify Cython
echo "Step 3: Verifying Cython..."
python3 -c "from pytrim import is_cython_available, is_using_cython; print(f'Cython available: {is_cython_available()}'); print(f'Cython active: {is_using_cython()}')"
echo ""

# Verify OpenMP
echo "Step 4: Verifying OpenMP..."
python3 -c "from pytrim import is_parallel_available; print(f'Parallel available: {is_parallel_available()}')"
if [ $? -ne 0 ]; then
    echo "⚠️  OpenMP verification failed, but Cython may still work"
fi
echo ""

# Run quick benchmark
echo "Step 5: Running performance test (100 ions)..."
python3 test_parallel.py 100
echo ""

echo "=================================="
echo "✅ Build and test complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  - Run GUI: ./run_gui.sh"
echo "  - Enable 'Use Cython' checkbox"
echo "  - Enable 'Use OpenMP Parallel' checkbox"
echo "  - Run simulation and enjoy the speedup!"
echo ""
