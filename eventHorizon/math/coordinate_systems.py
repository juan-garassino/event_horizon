"""
Unified coordinate system calculations for black hole physics.

This module contains coordinate transformations and mathematical functions
for different coordinate systems used in black hole spacetime.
"""
import warnings
from .spacetime_geometry import SpacetimeGeometry

warnings.warn(
    "This is a compatibility alias. Use SpacetimeGeometry directly for new code.",
    DeprecationWarning,
    stacklevel=2
)

# Alias for backward compatibility
CoordinateSystems = SpacetimeGeometry