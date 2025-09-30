"""
Configuration presets for different use cases.

This module provides pre-configured settings for common
black hole visualization scenarios.
"""
from .model_config import ModelConfig, PhysicsConfig, DiskConfig, NumericalConfig, VisualizationConfig


class ConfigPresets:
    """Collection of configuration presets for different use cases."""
    
    @staticmethod
    def draft_quality() -> ModelConfig:
        """Draft quality preset for quick previews."""
        return ModelConfig(
            numerical=NumericalConfig(
                max_iterations=100,
                midpoint_iterations=20,
                initial_guesses=5
            ),
            visualization=VisualizationConfig(
                image_width=400,
                image_height=300
            )
        )
    
    @staticmethod
    def standard_quality() -> ModelConfig:
        """Standard quality preset for general use."""
        return ModelConfig()
    
    @staticmethod
    def high_quality() -> ModelConfig:
        """High quality preset for detailed analysis."""
        return ModelConfig(
            numerical=NumericalConfig(
                solver_tolerance=1e-10,
                max_iterations=5000,
                midpoint_iterations=200,
                initial_guesses=50
            ),
            visualization=VisualizationConfig(
                image_width=1920,
                image_height=1080
            )
        )
    
    @staticmethod
    def publication_quality() -> ModelConfig:
        """Publication quality preset for research papers."""
        return ModelConfig(
            numerical=NumericalConfig(
                solver_tolerance=1e-12,
                max_iterations=10000,
                midpoint_iterations=500,
                initial_guesses=100
            ),
            visualization=VisualizationConfig(
                image_width=3840,
                image_height=2160,
                pixel_scale=5.0
            )
        )
    
    @staticmethod
    def animation_preset() -> ModelConfig:
        """Preset optimized for animation creation."""
        return ModelConfig(
            numerical=NumericalConfig(
                max_iterations=500,
                midpoint_iterations=50,
                initial_guesses=10
            ),
            visualization=VisualizationConfig(
                image_width=1280,
                image_height=720
            )
        )
    
    @staticmethod
    def interactive_preset() -> ModelConfig:
        """Preset optimized for interactive exploration."""
        return ModelConfig(
            numerical=NumericalConfig(
                max_iterations=200,
                midpoint_iterations=25,
                initial_guesses=5
            ),
            visualization=VisualizationConfig(
                image_width=800,
                image_height=600
            )
        )