"""
Unified visualization model for eventHorizon framework.

This module provides the main visualization model that unifies all black hole
visualization approaches into a single, coherent interface.
"""
from typing import Dict, Any, Optional, Tuple, List, Union
import numpy as np
import pandas as pd
from dataclasses import dataclass

from ..config.model_config import ModelConfig, get_default_config
from ..math.geodesics import Geodesics
from ..math.flux_calculations import FluxCalculations
from ..math.numerical_methods import NumericalMethods
from .base_model import BaseModel
from .particle_system import ParticleSystem
from .physics_engine import PhysicsEngine


@dataclass
class VisualizationResult:
    """Result container for visualization calculations."""
    particles: pd.DataFrame
    lensed_positions: pd.DataFrame
    flux_data: pd.DataFrame
    metadata: Dict[str, Any]


class VisualizationModel:
    """Unified visualization model for black hole physics."""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize the visualization model."""
        self.config = config or get_default_config()
        self.mass = self.config.physics.mass
        self.inclination = self.config.physics.inclination_deg
        
        # Initialize subsystems
        self.particle_system = ParticleSystem(
            black_hole_mass=self.mass,
            inner_radius=self.config.disk.get_inner_edge(self.mass),
            outer_radius=self.config.disk.get_outer_edge(self.mass)
        )
        self.physics_engine = PhysicsEngine()
        
        # Initialize mathematical modules
        self.geodesics = Geodesics()
        self.flux_calculator = FluxCalculations()
        self.numerical_methods = NumericalMethods()
        
    def generate_particles(self, count: Optional[int] = None) -> pd.DataFrame:
        """Generate particles from the accretion disk."""
        if count is None:
            count = self.config.visualization.image_width * self.config.visualization.image_height // 100
            
        return self.particle_system.sample_particles(count)
    
    def calculate_lensing(self, particles: pd.DataFrame) -> pd.DataFrame:
        """Calculate gravitational lensing for particles."""
        return self.physics_engine.calculate_lensing(particles)
    
    def calculate_flux_and_redshift(self, particles: pd.DataFrame) -> pd.DataFrame:
        """Calculate flux and redshift for particles."""
        return self.physics_engine.calculate_flux_and_redshift(particles)
    
    def generate_visualization_data(self, 
                                  particle_count: Optional[int] = None,
                                  include_lensing: bool = True,
                                  include_flux: bool = True) -> VisualizationResult:
        """Generate complete visualization data."""
        # Generate particles
        particles = self.generate_particles(particle_count)
        
        # Calculate lensing if requested
        lensed_positions = pd.DataFrame()
        if include_lensing and self.config.enable_lensing:
            lensed_positions = self.calculate_lensing(particles)
        
        # Calculate flux and redshift if requested
        flux_data = pd.DataFrame()
        if include_flux and self.config.enable_redshift:
            flux_data = self.calculate_flux_and_redshift(particles)
        
        # Compile metadata
        metadata = {
            'model_type': self.config.model_type,
            'mass': self.config.physics.mass,
            'inclination_deg': self.config.physics.inclination_deg,
            'particle_count': len(particles),
            'lensing_enabled': include_lensing and self.config.enable_lensing,
            'flux_enabled': include_flux and self.config.enable_redshift,
            'disk_inner_edge': self.config.disk.get_inner_edge(self.config.physics.mass),
            'disk_outer_edge': self.config.disk.get_outer_edge(self.config.physics.mass)
        }
        
        return VisualizationResult(
            particles=particles,
            lensed_positions=lensed_positions,
            flux_data=flux_data,
            metadata=metadata
        )
    
    def update_config(self, new_config: ModelConfig) -> None:
        """Update model configuration."""
        self.config = new_config
        self.mass = new_config.physics.mass
        self.inclination = new_config.physics.inclination_deg
        
        # Update subsystems
        self.particle_system.update_config(new_config)
        self.physics_engine.update_config(new_config)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model state."""
        return {
            'model_class': self.__class__.__name__,
            'config': self.config.to_dict(),
            'capabilities': {
                'ray_tracing': self.config.enable_ray_tracing,
                'lensing': self.config.enable_lensing,
                'redshift': self.config.enable_redshift
            },
            'physical_parameters': {
                'mass': self.config.physics.mass,
                'spin': self.config.physics.spin,
                'inclination_deg': self.config.physics.inclination_deg,
                'accretion_rate': self.config.physics.accretion_rate
            },
            'disk_parameters': {
                'inner_edge': self.config.disk.get_inner_edge(self.config.physics.mass),
                'outer_edge': self.config.disk.get_outer_edge(self.config.physics.mass),
                'temperature_profile': self.config.disk.temperature_profile,
                'emission_profile': self.config.disk.emission_profile
            }
        }
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate current configuration."""
        validation_results = {}
        
        # Physics validation
        validation_results['mass_positive'] = self.config.physics.mass > 0
        validation_results['inclination_valid'] = 0 <= self.config.physics.inclination_deg <= 180
        validation_results['accretion_rate_positive'] = self.config.physics.accretion_rate > 0
        validation_results['spin_valid'] = 0 <= abs(self.config.physics.spin) <= 1
        
        # Disk validation
        inner_edge = self.config.disk.get_inner_edge(self.config.physics.mass)
        outer_edge = self.config.disk.get_outer_edge(self.config.physics.mass)
        validation_results['disk_edges_valid'] = inner_edge < outer_edge
        validation_results['disk_inner_physical'] = inner_edge >= 6.0 * self.config.physics.mass
        
        # Numerical validation
        validation_results['tolerance_positive'] = self.config.numerical.solver_tolerance > 0
        validation_results['iterations_positive'] = self.config.numerical.max_iterations > 0
        
        # Overall validation
        validation_results['all_valid'] = all(validation_results.values())
        
        return validation_results


def create_visualization_model(config_preset: str = "standard") -> VisualizationModel:
    """Create a visualization model with a preset configuration."""
    from ..config.model_config import get_preset_config
    config = get_preset_config(config_preset)
    return VisualizationModel(config)