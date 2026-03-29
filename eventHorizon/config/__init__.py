"""Configuration management for Event Horizon framework."""

from .model_config import (
    ModelConfig, PhysicsConfig, DiskConfig, NumericalConfig, VisualizationConfig,
    get_default_config, get_preset_config
)
from .presets import ConfigPresets

# Stub aliases for deleted luminet_config
LuminetConfiguration = ModelConfig
def get_config_preset(preset_name: str):
    return get_preset_config(preset_name)
def create_config_from_dict(config_dict):
    return ModelConfig.from_dict(config_dict)

# Clean framework-native aliases
ParticleConfig = ModelConfig
ParticleSystemConfig = PhysicsConfig
RayTracingConfig = NumericalConfig
ConfigurationManager = None
config_manager = None

__all__ = [
    'ModelConfig', 'PhysicsConfig', 'DiskConfig', 'NumericalConfig', 'VisualizationConfig',
    'get_default_config', 'get_preset_config', 'ConfigPresets',
    'ParticleConfig', 'ParticleSystemConfig', 'RayTracingConfig',
    'LuminetConfiguration', 'get_config_preset', 'create_config_from_dict',
]
