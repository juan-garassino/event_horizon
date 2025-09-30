"""
Unified numerical methods for black hole calculations.

This module contains numerical utilities including root finding, optimization,
and other computational methods unified from both reference implementations.
"""
import warnings
from .numerical_solvers import NumericalSolvers

warnings.warn(
    "This is a compatibility alias. Use NumericalSolvers directly for new code.",
    DeprecationWarning,
    stacklevel=2
)

# Alias for backward compatibility
NumericalMethods = NumericalSolvers