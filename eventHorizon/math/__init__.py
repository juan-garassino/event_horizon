"""Mathematical foundations for black hole physics calculations."""

from .geodesics import UnifiedGeodesics, GeodesicMethod
from .geodesics import Geodesics, KerrGeodesics
from .spacetime_geometry import SpacetimeGeometry
from .fast_geodesics import (
    generate_particles_fast, build_impact_table,
    redshift_vec, flux_observed_vec, flux_intrinsic_vec,
)

# Stub replacements for deleted modules
class FluxCalculations:
    """Stub — use physics.fast_geodesics vectorized functions."""
    pass

class NumericalMethods:
    """Stub — functionality removed."""
    pass

class NumericalSolvers:
    """Stub — functionality removed."""
    pass

class CoordinateSystems:
    """Stub — functionality removed."""
    pass

class RelativisticEffects:
    """Stub — functionality removed."""
    pass

class UnifiedBlackHoleCalculator:
    """Stub — use UnifiedGeodesics instead."""
    pass

def create_unified_calculator(*args, **kwargs):
    return UnifiedBlackHoleCalculator()

# Legacy aliases
ClassicalGeodesics = Geodesics
ClassicalFlux = FluxCalculations
ClassicalSolvers = NumericalSolvers
ParticleMath = CoordinateSystems
ParticleFlux = FluxCalculations
ParticleSolvers = NumericalSolvers
BhsimGeodesics = ClassicalGeodesics
BhsimImpactParameter = ClassicalGeodesics
BhsimFlux = ClassicalFlux
BhsimUtils = ClassicalSolvers
LuminetMath = ParticleMath
LuminetFlux = ParticleFlux
LuminetPeriastronSolver = ParticleSolvers
LuminetImpactParameterCalculator = ParticleSolvers

__all__ = [
    'UnifiedBlackHoleCalculator', 'create_unified_calculator',
    'UnifiedGeodesics', 'GeodesicMethod',
    'Geodesics', 'FluxCalculations', 'NumericalMethods',
    'NumericalSolvers', 'CoordinateSystems', 'SpacetimeGeometry',
    'KerrGeodesics', 'RelativisticEffects',
    'ClassicalGeodesics', 'ClassicalFlux', 'ClassicalSolvers',
    'ParticleMath', 'ParticleFlux', 'ParticleSolvers',
    'BhsimGeodesics', 'BhsimImpactParameter', 'BhsimFlux',
    'BhsimUtils', 'LuminetMath', 'LuminetFlux',
    'LuminetPeriastronSolver', 'LuminetImpactParameterCalculator',
]
