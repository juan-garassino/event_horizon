"""Configuration management for Event Horizon framework."""

from .model_config import (
    ModelConfig,
    PhysicsConfig,
    DiskConfig,
    NumericalConfig,
    VisualizationConfig,
    get_default_config,
    get_preset_config
)
from .presets import ConfigPresets
from .validation import ConfigValidator

# Legacy imports for backward compatibility
from .luminet_config import (
    LuminetConfiguration,
    get_config_preset,
    create_config_from_dict
)

# Clean framework-native aliases
ParticleConfig = ModelConfig
ParticleSystemConfig = PhysicsConfig
RayTracingConfig = NumericalConfig

# Legacy aliases (deprecated)
ConfigurationManager = None
config_manager = None

__all__ = [
    # Primary unified interfaces
    'ModelConfig',
    'PhysicsConfig',
    'DiskConfig', 
    'NumericalConfig',
    'VisualizationConfig',
    'get_default_config',
    'get_preset_config',
    'ConfigPresets',
    'ConfigValidator',
    
    # Clean framework-native aliases
    'ParticleConfig',
    'ParticleSystemConfig',
    'RayTracingConfig',
    
    # Legacy compatibility (deprecated)
    'LuminetConfiguration',
    'get_config_preset',
    'create_config_from_dict'
]