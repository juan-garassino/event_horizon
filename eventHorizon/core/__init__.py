"""Core components for black hole simulation and visualization."""

from .isoradial_model import (
    Isoradial, IsoredshiftModel, IsoGridModel,
    PartialIsoradialModel, MultiRadiusPartialIsoradialModel, VelocityFieldModel,
)
from .particle import Particle, particles_to_dataframe

# Import ModelConfig for aliases
from ..config.model_config import ModelConfig

# Backward-compatible aliases that __init__.py expects
ParticleModel = None  # VisualizationModel was deleted
ParticleConfig = ModelConfig

# Stubs for names that __init__.py imports
VisualizationModel = type('VisualizationModel', (), {})  # stub
VisualizationResult = type('VisualizationResult', (), {})  # stub
create_visualization_model = lambda *a, **k: None
ParticleSystem = type('ParticleSystem', (), {})  # stub
RayTracingEngine = type('RayTracingEngine', (), {})  # stub

# Legacy aliases
LuminetModel = ParticleModel
LuminetConfig = ParticleConfig

__all__ = [
    'Isoradial', 'IsoredshiftModel', 'IsoGridModel',
    'PartialIsoradialModel', 'MultiRadiusPartialIsoradialModel', 'VelocityFieldModel',
    'Particle', 'particles_to_dataframe',
    'VisualizationModel', 'VisualizationResult', 'create_visualization_model',
    'ParticleSystem', 'RayTracingEngine',
    'ParticleModel', 'ParticleConfig',
    'LuminetModel', 'LuminetConfig',
    'ModelConfig',
]
