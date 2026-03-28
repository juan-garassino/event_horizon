"""Mathematical foundations for black hole physics calculations."""

from .unified_interface import UnifiedBlackHoleCalculator, create_unified_calculator
from .geodesics import UnifiedGeodesics, GeodesicMethod
from .geodesics import Geodesics, KerrGeodesics
from .flux_calculations import FluxCalculations
from .numerical_methods import NumericalMethods
from .numerical_solvers import NumericalSolvers
from .coordinate_systems import CoordinateSystems
from .spacetime_geometry import SpacetimeGeometry
# KerrGeodesics is now an alias in geodesics.py
from .relativistic_effects import RelativisticEffects

# Clean framework-native aliases
ClassicalGeodesics = Geodesics
ClassicalFlux = FluxCalculations
ClassicalSolvers = NumericalSolvers
ParticleMath = CoordinateSystems
ParticleFlux = FluxCalculations
ParticleSolvers = NumericalSolvers

# Legacy reference-specific aliases (deprecated)
BhsimGeodesics = ClassicalGeodesics
BhsimImpactParameter = ClassicalGeodesics
BhsimFlux = ClassicalFlux
BhsimUtils = ClassicalSolvers
LuminetMath = ParticleMath
LuminetFlux = ParticleFlux
LuminetPeriastronSolver = ParticleSolvers
LuminetImpactParameterCalculator = ParticleSolvers

__all__ = [
    # Primary unified interfaces
    'UnifiedBlackHoleCalculator',
    'create_unified_calculator',
    'UnifiedGeodesics',
 
    'GeodesicMethod',
    
    # Core unified modules
    'Geodesics',
    'FluxCalculations',
    'NumericalMethods',
    'NumericalSolvers',
    'CoordinateSystems',
    'SpacetimeGeometry',
    'KerrGeodesics',
    'RelativisticEffects',
    
    # Clean framework-native aliases
    'ClassicalGeodesics',
    'ClassicalFlux',
    'ClassicalSolvers',
    'ParticleMath',
    'ParticleFlux',
    'ParticleSolvers',
    
    # Legacy compatibility (deprecated)
    'BhsimGeodesics',
    'BhsimImpactParameter',
    'BhsimFlux',
    'BhsimUtils',
    'LuminetMath',
    'LuminetFlux',
    'LuminetPeriastronSolver',
    'LuminetImpactParameterCalculator'
]