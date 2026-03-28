"""
Compatibility layer for backward compatibility with existing functionality.

This module provides compatibility wrappers and adapters to ensure that
existing code continues to work with the new architecture.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from .visualization_model import VisualizationModel
from .isoradial_model import Isoradial, IsoredshiftModel
from .particle_system import ParticleSystem


class LegacyCompatibilityWrapper:
    """Wrapper to maintain compatibility with legacy interfaces."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize compatibility wrapper."""
        self.config = config or {}
        self._visualization_model = None
    
    def get_visualization_model(self) -> VisualizationModel:
        """Get or create visualization model."""
        if self._visualization_model is None:
            from ..config.model_config import get_default_config
            config = get_default_config()
            self._visualization_model = VisualizationModel(config)
        return self._visualization_model
    
    def create_isoradial(
        self,
        mass: float = 1.0,
        inclination: float = 80.0,
        radius: float = 10.0,
        image_order: int = 0,
        **kwargs
    ) -> Isoradial:
        """Create isoradial model with backward compatibility."""
        isoradial = Isoradial(
            mass=mass,
            inclination=inclination,
            radius=radius,
            image_order=image_order,
            config=kwargs
        )
        
        # Automatically calculate coordinates for backward compatibility
        angular_precision = kwargs.get('angular_precision', 100)
        isoradial.calculate_coordinates(angular_precision=angular_precision)
        isoradial.calculate_redshift_factors()
        
        return isoradial
    
    def create_multiple_isoradials(
        self,
        radii: List[float],
        mass: float = 1.0,
        inclination: float = 80.0,
        image_order: int = 0,
        **kwargs
    ) -> List[Isoradial]:
        """Create multiple isoradial models."""
        isoradials = []
        for radius in radii:
            isoradial = self.create_isoradial(
                mass=mass,
                inclination=inclination,
                radius=radius,
                image_order=image_order,
                **kwargs
            )
            isoradials.append(isoradial)
        return isoradials
    
    def generate_luminet_particles(
        self,
        n_points: int = 10000,
        mass: float = 1.0,
        inclination: float = 80.0,
        inner_radius: float = 6.0,
        outer_radius: float = 50.0,
        **kwargs
    ) -> pd.DataFrame:
        """Generate Luminet-style particles with backward compatibility."""
        # Create particle system
        particle_system = ParticleSystem(
            black_hole_mass=mass,
            particle_count=n_points,
            distribution_type='luminet',
            inner_radius=inner_radius,
            outer_radius=outer_radius
        )
        
        # Generate particles
        particles = particle_system.generate_particles()
        
        # Apply physics using the new pipeline
        from .physics_engine import PhysicsEngine
        physics_engine = PhysicsEngine(mass=mass, spin=0.0)
        
        processed_particles = physics_engine.execute_complete_pipeline(
            particles=particles,
            inclination=inclination,
            accretion_rate=kwargs.get('accretion_rate', 1.0),
            enable_lensing=True,
            enable_flux_calculation=True,
            enable_redshift=True
        )
        
        # Convert to DataFrame for backward compatibility
        particles_data = []
        for particle in processed_particles:
            particles_data.append({
                'radius': particle.radius,
                'angle': particle.angle,
                'temperature': particle.temperature,
                'flux': particle.flux,
                'redshift_factor': particle.redshift_factor,
                'impact_parameter': particle.impact_parameter,
                'observed_x': particle.observed_x,
                'observed_y': particle.observed_y,
                'image_order': particle.image_order,
                'brightness': particle.brightness,
                'is_visible': particle.is_visible
            })
        
        return pd.DataFrame(particles_data)
    
    def ensure_existing_plots_work(self) -> bool:
        """Test that existing plotting functionality still works."""
        try:
            # Test isoradial creation
            isoradial = self.create_isoradial(mass=1.0, inclination=80.0, radius=10.0)
            
            # Check that data was calculated
            has_data = (
                hasattr(isoradial, 'angles') and len(isoradial.angles) > 0 and
                hasattr(isoradial, 'impact_parameters') and len(isoradial.impact_parameters) > 0 and
                hasattr(isoradial, 'cartesian_x') and len(isoradial.cartesian_x) > 0 and
                hasattr(isoradial, 'cartesian_y') and len(isoradial.cartesian_y) > 0
            )
            
            if not has_data:
                return False
            
            # Test particle generation
            particles_df = self.generate_luminet_particles(n_points=100)
            
            # Check that particles were generated
            has_particles = len(particles_df) > 0 and 'radius' in particles_df.columns
            
            return has_particles
            
        except Exception as e:
            print(f"Compatibility test failed: {e}")
            return False


# Global compatibility instance
compatibility = LegacyCompatibilityWrapper()


def create_isoradial_legacy(
    mass: float = 1.0,
    inclination: float = 80.0,
    radius: float = 10.0,
    **kwargs
) -> Isoradial:
    """Legacy function for creating isoradials."""
    return compatibility.create_isoradial(
        mass=mass,
        inclination=inclination,
        radius=radius,
        **kwargs
    )


def generate_particles_legacy(
    n_points: int = 10000,
    mass: float = 1.0,
    inclination: float = 80.0,
    **kwargs
) -> pd.DataFrame:
    """Legacy function for generating particles."""
    return compatibility.generate_luminet_particles(
        n_points=n_points,
        mass=mass,
        inclination=inclination,
        **kwargs
    )


def test_backward_compatibility() -> bool:
    """Test that all backward compatibility features work."""
    return compatibility.ensure_existing_plots_work()