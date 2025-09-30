"""Core components for black hole simulation and visualization."""

from .base_model import BaseModel
from .visualization_model import VisualizationModel, VisualizationResult, create_visualization_model
from .particle_system import ParticleSystem, Particle
from .ray_tracing import RayTracingEngine, RayTracingConfig
from .isoradial_model import Isoradial, IsoredshiftModel, IsoGridModel, PartialIsoradialModel, MultiRadiusPartialIsoradialModel, VelocityFieldModel
from .physics_engine import PhysicsEngine
from .renderer import ParticleRenderer

# Import ModelConfig for aliases
from ..config.model_config import ModelConfig

# Clean framework-native aliases
ParticleModel = VisualizationModel
ParticleConfig = ModelConfig

# Legacy imports for backward compatibility
from .luminet_model import LuminetModel, LuminetConfig

__all__ = [
    # Primary unified interfaces
    'BaseModel',
    'VisualizationModel',
    'VisualizationResult',
    'create_visualization_model',
    'ParticleSystem',
    'Particle', 
    'RayTracingEngine',
    'RayTracingConfig',
    'Isoradial',
    'IsoredshiftModel',
    'IsoGridModel',
    'PartialIsoradialModel',
    'MultiRadiusPartialIsoradialModel',
    'VelocityFieldModel',
    'PhysicsEngine',
    'ParticleRenderer',
    
    # Clean framework-native aliases
    'ParticleModel',
    'ParticleConfig',
    
    # Legacy compatibility (deprecated)
    'LuminetModel',
    'LuminetConfig'
]