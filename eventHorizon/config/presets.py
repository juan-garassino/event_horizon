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
    
    @staticmethod
    def luminet_preset(inclination: float = 80.0, mass: float = 1.0, 
                      particle_count: int = 10000, power_scale: float = 0.9,
                      levels: int = 100) -> ModelConfig:
        """
        Luminet-style black hole visualization preset.
        
        Configured for Jean-Pierre Luminet's iconic dot-based visualization
        with proper particle sampling and tricontourf rendering.
        
        Parameters
        ----------
        inclination : float
            Observer inclination angle in degrees
        mass : float
            Black hole mass
        particle_count : int
            Number of particles for sampling
        power_scale : float
            Power scaling for flux visualization
        levels : int
            Number of contour levels for tricontourf
        """
        return ModelConfig(
            physics=PhysicsConfig(
                mass=mass,
                spin=0.0,  # Schwarzschild black hole
                inclination_deg=inclination
            ),
            disk=DiskConfig(
                inner_radius_factor=6.0,  # Luminet's disk inner edge
                outer_radius_factor=50.0,  # Luminet's disk outer edge
                accretion_rate=1e-8,
                temperature_profile='luminet',
                flux_profile='luminet'
            ),
            numerical=NumericalConfig(
                solver_tolerance=1e-8,
                max_iterations=1000,
                midpoint_iterations=100,
                initial_guesses=20,
                min_periastron_factor=3.01
            ),
            visualization=VisualizationConfig(
                image_width=1000,
                image_height=1000,
                pixel_scale=1.0,
                color_scheme='luminet',
                background_color='black',
                power_scale=power_scale,
                contour_levels=levels,
                particle_count=particle_count,
                distribution_type='luminet',
                bias_toward_center=True
            )
        )


def get_luminet_preset(inclination: float = 80.0, mass: float = 1.0, 
                      particle_count: int = 10000, power_scale: float = 0.9,
                      levels: int = 100) -> ModelConfig:
    """
    Get Luminet-style configuration preset.
    
    Convenience function for creating luminet visualization configurations.
    """
    return ConfigPresets.luminet_preset(
        inclination=inclination,
        mass=mass,
        particle_count=particle_count,
        power_scale=power_scale,
        levels=levels
    )