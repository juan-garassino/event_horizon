"""
Legacy compatibility configuration for luminet reference implementation.

This module is deprecated. Use eventHorizon.config.model_config instead.
"""
import warnings
from .model_config import ModelConfig, get_default_config as get_unified_config

warnings.warn(
    "luminet_config is deprecated. Use eventHorizon.config.model_config instead.",
    DeprecationWarning,
    stacklevel=2
)

# Clean framework-native aliases
ParticleConfiguration = ModelConfig

# Legacy reference-specific aliases (deprecated)
LuminetConfiguration = ParticleConfiguration
ConfigurationManager = None  # Deprecated
config_manager = None  # Deprecated

def get_default_config():
    """Legacy function - use get_default_config from model_config instead."""
    return get_unified_config()

def get_config_preset(preset_name: str):
    """Legacy function - use get_preset_config from model_config instead."""
    from .model_config import get_preset_config
    return get_preset_config(preset_name)

def create_config_from_dict(config_dict):
    """Legacy function - use ModelConfig.from_dict instead."""
    return ModelConfig.from_dict(config_dict)