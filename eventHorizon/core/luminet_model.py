"""
Legacy compatibility model for luminet reference implementation.

This module is deprecated. Use eventHorizon.core.visualization_model instead.
"""
import warnings
from .visualization_model import VisualizationModel
from ..config.model_config import ModelConfig

warnings.warn(
    "luminet_model is deprecated. Use eventHorizon.core.visualization_model instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import ModelConfig for aliases
from ..config.model_config import ModelConfig

# Clean framework-native aliases
ParticleModel = VisualizationModel
ParticleConfig = ModelConfig

# Legacy reference-specific aliases (deprecated)
LuminetModel = ParticleModel
LuminetConfig = ParticleConfig