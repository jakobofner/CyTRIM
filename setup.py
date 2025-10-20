"""Setup script for building Cython extensions."""
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np
import sys

# Compiler flags
extra_compile_args = []
extra_link_args = []
openmp_compile_args = []
openmp_link_args = []

if sys.platform == 'darwin':  # macOS
    extra_compile_args = ['-O3', '-ffast-math']
    openmp_compile_args = ['-O3', '-ffast-math', '-Xpreprocessor', '-fopenmp']
    openmp_link_args = ['-lomp']
elif sys.platform == 'win32':  # Windows
    extra_compile_args = ['/O2']
    openmp_compile_args = ['/O2', '/openmp']
    openmp_link_args = []
else:  # Linux and others
    extra_compile_args = ['-O3', '-ffast-math', '-march=native']
    openmp_compile_args = ['-O3', '-ffast-math', '-march=native', '-fopenmp']
    openmp_link_args = ['-fopenmp']

# Define extensions
extensions = [
    Extension(
        "cytrim.estop",
        ["cytrim/estop.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "cytrim.scatter",
        ["cytrim/scatter.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "cytrim.geometry",
        ["cytrim/geometry.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "cytrim.select_recoil",
        ["cytrim/select_recoil.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "cytrim.trajectory",
        ["cytrim/trajectory.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "cytrim.geometry3d",
        ["cytrim/geometry3d.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
    Extension(
        "cytrim.simulation_parallel",
        ["cytrim/simulation_parallel.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=openmp_compile_args,
        extra_link_args=openmp_link_args,
    ),
]

setup(
    name="CyTRIM",
    version="1.0.0",
    description="Cython-optimized TRIM simulation",
    author="CyTRIM Development Team",
    packages=["pytrim", "cytrim"],
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'embedsignature': True,
        },
        annotate=True,  # Generate HTML annotation files
    ),
    install_requires=[
        'numpy>=1.20.0',
        'PyQt6>=6.4.0',
        'matplotlib>=3.5.0',
    ],
    python_requires='>=3.8',
    zip_safe=False,
)
