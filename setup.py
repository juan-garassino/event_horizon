"""
Build script for eventHorizon.

The Cython extension is optional — if Cython or a C compiler is not
available, the package still works using the pure NumPy/SciPy fallback.

    pip install -e .               # pure Python (always works)
    pip install -e ".[fast]"       # builds Cython extension if possible
"""

from setuptools import setup, find_packages, Extension
import numpy

# Try to build Cython extension; silently skip if not available
ext_modules = []
try:
    from Cython.Build import cythonize
    ext_modules = cythonize(
        [Extension(
            "eventHorizon.math._fast_geodesics_cy",
            ["eventHorizon/math/_fast_geodesics_cy.pyx"],
            include_dirs=[numpy.get_include()],
        )],
        compiler_directives={
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
            "language_level": 3,
        },
    )
except ImportError:
    pass

setup(
    name="eventHorizon",
    version="1.0.0",
    description="Recreation of Luminet's 1979 black hole visualization",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.22",
        "scipy>=1.9",
        "matplotlib>=3.5",
        "pandas>=1.4",
        "sympy>=1.10",
        "rich>=12.0",
        "pyfiglet>=0.8",
    ],
    extras_require={
        "fast": ["cython>=3.0"],
    },
    ext_modules=ext_modules,
    entry_points={
        "console_scripts": [
            "eventhorizon=main:main",
        ],
    },
)
