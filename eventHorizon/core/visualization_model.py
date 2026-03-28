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
        self.physics_engine = PhysicsEngine(mass=self.mass, spin=self.config.physics.spin)
        
        # Initialize ray tracing engine
        from .ray_tracing import RayTracingEngine, RayTracingConfig
        ray_config = RayTracingConfig(
            black_hole_mass=self.mass,
            observer_distance=self.config.observer.distance if hasattr(self.config, 'observer') else 1000.0,
            max_image_orders=2
        )
        self.ray_tracer = RayTracingEngine(ray_config)
        
        # Initialize mathematical modules
        self.geodesics = Geodesics()
        self.flux_calculator = FluxCalculations()
        self.numerical_methods = NumericalMethods()
        
    def generate_particles(self, count: Optional[int] = None) -> pd.DataFrame:
        """Generate particles from the accretion disk."""
        if count is None:
            count = self.config.visualization.image_width * self.config.visualization.image_height // 100
        
        # Update particle count in particle system
        self.particle_system.particle_count = count
        
        # Generate particles using the correct method
        particles_list = self.particle_system.generate_particles()
        
        # Convert to DataFrame for compatibility with existing code
        particles_data = []
        for particle in particles_list:
            particles_data.append({
                'radius': particle.radius,
                'angle': particle.angle,
                'temperature': particle.temperature,
                'flux': particle.flux,
                'redshift_factor': particle.redshift_factor,
                'impact_parameter': particle.impact_parameter,
                'observed_alpha': particle.observed_alpha,
                'observed_x': particle.observed_x,
                'observed_y': particle.observed_y,
                'image_order': particle.image_order,
                'brightness': particle.brightness,
                'color_r': particle.color[0],
                'color_g': particle.color[1],
                'color_b': particle.color[2],
                'particle_id': particle.particle_id,
                'is_visible': particle.is_visible
            })
        
        return pd.DataFrame(particles_data)
    
    def calculate_lensing(self, particles: pd.DataFrame) -> pd.DataFrame:
        """Calculate gravitational lensing for particles."""
        # Convert DataFrame back to Particle objects for processing
        particle_objects = []
        for _, row in particles.iterrows():
            from .particle_system import Particle
            particle = Particle(
                radius=row['radius'],
                angle=row['angle'],
                temperature=row['temperature'],
                flux=row['flux'],
                redshift_factor=row['redshift_factor'],
                impact_parameter=row['impact_parameter'],
                observed_alpha=row['observed_alpha'],
                observed_x=row['observed_x'],
                observed_y=row['observed_y'],
                image_order=row['image_order'],
                brightness=row['brightness'],
                color=(row['color_r'], row['color_g'], row['color_b']),
                particle_id=row['particle_id'],
                is_visible=row['is_visible']
            )
            particle_objects.append(particle)
        
        # Apply lensing calculations using physics engine
        lensed_particles = self.physics_engine.apply_lensing_effects(
            particle_objects, 
            self.inclination,
            self.mass
        )
        
        # Convert back to DataFrame
        lensed_data = []
        for particle in lensed_particles:
            lensed_data.append({
                'radius': particle.radius,
                'angle': particle.angle,
                'temperature': particle.temperature,
                'flux': particle.flux,
                'redshift_factor': particle.redshift_factor,
                'impact_parameter': particle.impact_parameter,
                'observed_alpha': particle.observed_alpha,
                'observed_x': particle.observed_x,
                'observed_y': particle.observed_y,
                'image_order': particle.image_order,
                'brightness': particle.brightness,
                'color_r': particle.color[0],
                'color_g': particle.color[1],
                'color_b': particle.color[2],
                'particle_id': particle.particle_id,
                'is_visible': particle.is_visible
            })
        
        return pd.DataFrame(lensed_data)
    
    def calculate_flux_and_redshift(self, particles: pd.DataFrame) -> pd.DataFrame:
        """Calculate flux and redshift for particles."""
        # Convert DataFrame to Particle objects for processing
        particle_objects = []
        for _, row in particles.iterrows():
            from .particle_system import Particle
            particle = Particle(
                radius=row['radius'],
                angle=row['angle'],
                temperature=row['temperature'],
                flux=row['flux'],
                redshift_factor=row['redshift_factor'],
                impact_parameter=row['impact_parameter'],
                observed_alpha=row['observed_alpha'],
                observed_x=row['observed_x'],
                observed_y=row['observed_y'],
                image_order=row['image_order'],
                brightness=row['brightness'],
                color=(row['color_r'], row['color_g'], row['color_b']),
                particle_id=row['particle_id'],
                is_visible=row['is_visible']
            )
            particle_objects.append(particle)
        
        # Apply flux and redshift calculations using physics engine
        updated_particles = self.physics_engine.calculate_flux_and_redshift(
            particle_objects,
            self.inclination,
            self.mass
        )
        
        # Convert back to DataFrame
        flux_data = []
        for particle in updated_particles:
            flux_data.append({
                'radius': particle.radius,
                'angle': particle.angle,
                'temperature': particle.temperature,
                'flux': particle.flux,
                'redshift_factor': particle.redshift_factor,
                'impact_parameter': particle.impact_parameter,
                'observed_alpha': particle.observed_alpha,
                'observed_x': particle.observed_x,
                'observed_y': particle.observed_y,
                'image_order': particle.image_order,
                'brightness': particle.brightness,
                'color_r': particle.color[0],
                'color_g': particle.color[1],
                'color_b': particle.color[2],
                'particle_id': particle.particle_id,
                'is_visible': particle.is_visible
            })
        
        return pd.DataFrame(flux_data)
    
    def generate_visualization_data(self, 
                                  particle_count: Optional[int] = None,
                                  include_lensing: bool = True,
                                  include_flux: bool = True,
                                  include_ray_tracing: bool = True) -> VisualizationResult:
        """Generate complete visualization data."""
        # Generate particles
        particles = self.generate_particles(particle_count)
        
        # Apply ray tracing if requested
        if include_ray_tracing and self.config.enable_ray_tracing:
            # Convert DataFrame to particle objects for ray tracing
            particle_objects = []
            for _, row in particles.iterrows():
                from .particle_system import Particle
                particle = Particle(
                    radius=row['radius'],
                    angle=row['angle'],
                    temperature=row['temperature'],
                    flux=row['flux'],
                    redshift_factor=row['redshift_factor'],
                    impact_parameter=row['impact_parameter'],
                    observed_alpha=row['observed_alpha'],
                    observed_x=row['observed_x'],
                    observed_y=row['observed_y'],
                    image_order=row['image_order'],
                    brightness=row['brightness'],
                    color=(row['color_r'], row['color_g'], row['color_b']),
                    particle_id=row['particle_id'],
                    is_visible=row['is_visible']
                )
                particle_objects.append(particle)
            
            # Apply ray tracing
            traced_particles = self.ray_tracer.trace_particle_paths(
                particle_objects, 
                self.inclination
            )
            
            # Convert back to DataFrame
            particles_data = []
            for particle in traced_particles:
                particles_data.append({
                    'radius': particle.radius,
                    'angle': particle.angle,
                    'temperature': particle.temperature,
                    'flux': particle.flux,
                    'redshift_factor': particle.redshift_factor,
                    'impact_parameter': particle.impact_parameter,
                    'observed_alpha': particle.observed_alpha,
                    'observed_x': particle.observed_x,
                    'observed_y': particle.observed_y,
                    'image_order': particle.image_order,
                    'brightness': particle.brightness,
                    'color_r': particle.color[0],
                    'color_g': particle.color[1],
                    'color_b': particle.color[2],
                    'particle_id': particle.particle_id,
                    'is_visible': particle.is_visible
                })
            particles = pd.DataFrame(particles_data)
        
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
            'ray_tracing_enabled': include_ray_tracing and self.config.enable_ray_tracing,
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
        self.particle_system.black_hole_mass = self.mass
        self.particle_system.inner_radius = new_config.disk.get_inner_edge(self.mass)
        self.particle_system.outer_radius = new_config.disk.get_outer_edge(self.mass)
        
        self.physics_engine.update_config(new_config)
        
        # Update ray tracer configuration
        self.ray_tracer.update_configuration(
            black_hole_mass=self.mass,
            observer_distance=new_config.observer.distance if hasattr(new_config, 'observer') else 1000.0
        )
    
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