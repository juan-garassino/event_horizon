"""
Event Horizon - Advanced Black Hole Visualization Framework

A comprehensive framework for simulating and visualizing black hole physics,
combining the best algorithms from bhsim and luminet references with modern
particle-based rendering techniques.
"""

__version__ = "1.0.0"
__author__ = "Event Horizon Development Team"

from .core import VisualizationModel, create_visualization_model, VisualizationResult, ParticleSystem, RayTracingEngine, Isoradial, IsoredshiftModel, IsoGridModel, PartialIsoradialModel, MultiRadiusPartialIsoradialModel, VelocityFieldModel
from .math import UnifiedBlackHoleCalculator, UnifiedGeodesics, Geodesics, FluxCalculations, NumericalMethods, NumericalSolvers, CoordinateSystems, SpacetimeGeometry
from .config import ModelConfig, get_default_config, get_preset_config
from .adapters import UnifiedReferenceAdapter
from .visualization import UnifiedPlotter, create_unified_plotter, IsoradialPlotter, IsoredshiftPlotter, CombinedIsoPlotter

# Legacy aliases for backward compatibility (deprecated)
from .core import LuminetModel, LuminetConfig
from .config import LuminetConfiguration

# Clean framework-native aliases
ParticleModel = VisualizationModel
ParticlePlotter = UnifiedPlotter
ParticleConfig = ModelConfig
ClassicalAdapter = UnifiedReferenceAdapter
ParticleAdapter = UnifiedReferenceAdapter

# Legacy reference-specific aliases (deprecated)
LuminetModel = ParticleModel
LuminetPlotter = ParticlePlotter
LuminetConfiguration = ParticleConfig
BhsimAdapter = ClassicalAdapter
LuminetAdapter = ParticleAdapter

__all__ = [
    # Primary unified interfaces
    'VisualizationModel',
    'create_visualization_model',
    'VisualizationResult',
    'ParticleSystem', 
    'RayTracingEngine',
    'Isoradial',
    'IsoredshiftModel', 
    'IsoGridModel',
    'PartialIsoradialModel',
    'MultiRadiusPartialIsoradialModel',
    'VelocityFieldModel',
    'UnifiedBlackHoleCalculator',
    'UnifiedGeodesics',
    'Geodesics',
    'FluxCalculations',
    'NumericalMethods',
    'NumericalSolvers',
    'CoordinateSystems',
    'SpacetimeGeometry',
    'ModelConfig',
    'get_default_config',
    'get_preset_config',
    'UnifiedReferenceAdapter',
    'UnifiedPlotter',
    'create_unified_plotter',
    'IsoradialPlotter',
    'IsoredshiftPlotter',
    'CombinedIsoPlotter',
    
    # Clean framework-native aliases
    'ParticleModel',
    'ParticlePlotter', 
    'ParticleConfig',
    'ClassicalAdapter',
    'ParticleAdapter',
    
    # Legacy compatibility (deprecated)
    'LuminetModel',
    'LuminetConfiguration',
    'BhsimAdapter',
    'LuminetAdapter',
    'LuminetPlotter'
]