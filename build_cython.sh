#!/bin/bash
# Build script for Cython extensions

echo "Building Cython extensions..."
echo "=============================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/upgrade build dependencies
echo "Installing build dependencies..."
pip install -q --upgrade pip setuptools wheel
pip install -q Cython numpy

# Build Cython extensions
echo "Compiling Cython modules..."
python setup.py build_ext --inplace

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo ""
    echo "Cython modules compiled in cytrim/"
    echo "You can now run the GUI with improved performance:"
    echo "  ./run_gui.sh"
    echo ""
else
    echo ""
    echo "✗ Build failed!"
    echo "The program will still work with pure Python modules."
    echo ""
    exit 1
fi
