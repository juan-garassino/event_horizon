"""
Unified model configuration for eventHorizon framework.

This module provides configuration management for all black hole visualization
models in a unified, framework-native approach.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
import numpy as np


@dataclass
class PhysicsConfig:
    """Configuration for physics parameters."""
    mass: float = 1.0
    spin: float = 0.0  # For Kerr black holes
    inclination_deg: float = 80.0
    accretion_rate: float = 1e-8
    
    @property
    def inclination_rad(self) -> float:
        """Get inclination in radians."""
        return self.inclination_deg * np.pi / 180


@dataclass
class DiskConfig:
    """Configuration for accretion disk parameters."""
    inner_edge_factor: float = 6.0  # Multiple of mass
    outer_edge_factor: float = 50.0  # Multiple of mass
    temperature_profile: str = "standard"  # "standard", "custom"
    emission_profile: str = "blackbody"  # "blackbody", "power_law"
    
    def get_inner_edge(self, mass: float) -> float:
        """Get inner edge radius."""
        return self.inner_edge_factor * mass
        
    def get_outer_edge(self, mass: float) -> float:
        """Get outer edge radius."""
        return self.outer_edge_factor * mass


@dataclass
class NumericalConfig:
    """Configuration for numerical methods."""
    solver_tolerance: float = 1e-8
    max_iterations: int = 1000
    midpoint_iterations: int = 100
    initial_guesses: int = 20
    min_periastron_factor: float = 3.01  # Multiple of mass
    use_ellipse_fallback: bool = True
    
    def get_min_periastron(self, mass: float) -> float:
        """Get minimum periastron distance."""
        return self.min_periastron_factor * mass


@dataclass
class VisualizationConfig:
    """Configuration for visualization parameters."""
    image_width: int = 800
    image_height: int = 600
    pixel_scale: float = 20.0
    color_scheme: str = "plasma"
    show_event_horizon: bool = True
    show_photon_sphere: bool = True
    show_disk_edge: bool = True
    
    
@dataclass
class ModelConfig:
    """Unified configuration for all black hole models."""
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    disk: DiskConfig = field(default_factory=DiskConfig)
    numerical: NumericalConfig = field(default_factory=NumericalConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Model-specific settings
    model_type: str = "unified"  # "unified", "luminet", "bhsim", "isoradial"
    enable_ray_tracing: bool = True
    enable_lensing: bool = True
    enable_redshift: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'physics': {
                'mass': self.physics.mass,
                'spin': self.physics.spin,
                'inclination_deg': self.physics.inclination_deg,
                'accretion_rate': self.physics.accretion_rate
            },
            'disk': {
                'inner_edge_factor': self.disk.inner_edge_factor,
                'outer_edge_factor': self.disk.outer_edge_factor,
                'temperature_profile': self.disk.temperature_profile,
                'emission_profile': self.disk.emission_profile
            },
            'numerical': {
                'solver_tolerance': self.numerical.solver_tolerance,
                'max_iterations': self.numerical.max_iterations,
                'midpoint_iterations': self.numerical.midpoint_iterations,
                'initial_guesses': self.numerical.initial_guesses,
                'min_periastron_factor': self.numerical.min_periastron_factor,
                'use_ellipse_fallback': self.numerical.use_ellipse_fallback
            },
            'visualization': {
                'image_width': self.visualization.image_width,
                'image_height': self.visualization.image_height,
                'pixel_scale': self.visualization.pixel_scale,
                'color_scheme': self.visualization.color_scheme,
                'show_event_horizon': self.visualization.show_event_horizon,
                'show_photon_sphere': self.visualization.show_photon_sphere,
                'show_disk_edge': self.visualization.show_disk_edge
            },
            'model_type': self.model_type,
            'enable_ray_tracing': self.enable_ray_tracing,
            'enable_lensing': self.enable_lensing,
            'enable_redshift': self.enable_redshift
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ModelConfig':
        """Create configuration from dictionary."""
        physics = PhysicsConfig(**config_dict.get('physics', {}))
        disk = DiskConfig(**config_dict.get('disk', {}))
        numerical = NumericalConfig(**config_dict.get('numerical', {}))
        visualization = VisualizationConfig(**config_dict.get('visualization', {}))
        
        return cls(
            physics=physics,
            disk=disk,
            numerical=numerical,
            visualization=visualization,
            model_type=config_dict.get('model_type', 'unified'),
            enable_ray_tracing=config_dict.get('enable_ray_tracing', True),
            enable_lensing=config_dict.get('enable_lensing', True),
            enable_redshift=config_dict.get('enable_redshift', True)
        )


def get_default_config() -> ModelConfig:
    """Get default configuration for eventHorizon models."""
    return ModelConfig()


def get_preset_config(preset_name: str) -> ModelConfig:
    """Get preset configuration by name."""
    presets = {
        'standard': ModelConfig(),
        'high_quality': ModelConfig(
            numerical=NumericalConfig(
                solver_tolerance=1e-10,
                max_iterations=5000,
                midpoint_iterations=200,
                initial_guesses=50
            ),
            visualization=VisualizationConfig(
                image_width=1920,
                image_height=1080,
                pixel_scale=10.0
            )
        ),
        'high_resolution': ModelConfig(
            visualization=VisualizationConfig(
                image_width=1920,
                image_height=1080,
                pixel_scale=10.0
            )
        ),
        'fast': ModelConfig(
            numerical=NumericalConfig(
                midpoint_iterations=50,
                initial_guesses=10
            )
        )
    }
    
    if preset_name not in presets:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(presets.keys())}")
    
    return presets[preset_name]