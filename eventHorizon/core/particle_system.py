"""
Particle system for dot-based black hole visualization.

This module provides the foundation for representing matter in the accretion disk
as individual particles/dots, enabling Luminet-style visualization.
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Particle:
    """Data structure representing a single particle in the accretion disk."""
    
    # Spatial coordinates (disk frame)
    radius: float           # Radial position in accretion disk
    angle: float           # Angular position
    
    # Physical properties
    temperature: float     # Local temperature
    flux: float           # Intrinsic flux
    redshift_factor: float # Gravitational redshift (1+z)
    
    # Observed coordinates (after lensing)
    impact_parameter: float
    observed_alpha: float
    observed_x: float
    observed_y: float
    
    # Image properties
    image_order: int      # 0=direct, 1=ghost, etc.
    brightness: float     # Rendered brightness
    color: Tuple[float, float, float]  # RGB color values
    
    # Metadata
    particle_id: int = 0
    is_visible: bool = True


class ParticleDistribution(ABC):
    """Abstract base class for particle distribution strategies."""
    
    @abstractmethod
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample particle positions.
        
        Parameters
        ----------
        n_particles : int
            Number of particles to sample
        inner_radius : float
            Inner radius of disk
        outer_radius : float
            Outer radius of disk
            
        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Radial and angular positions
        """
        pass


class UniformDistribution(ParticleDistribution):
    """Uniform distribution across disk surface."""
    
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample uniformly across disk surface."""
        # Uniform sampling of disk surface (area-weighted)
        u = np.random.random(n_particles)
        radii = np.sqrt(u * (outer_radius**2 - inner_radius**2) + inner_radius**2)
        angles = np.random.random(n_particles) * 2 * np.pi
        
        return radii, angles


class BiasedCenterDistribution(ParticleDistribution):
    """Distribution biased toward disk center for realistic matter distribution."""
    
    def __init__(self, bias_exponent: float = 2.0):
        """Initialize biased distribution.
        
        Parameters
        ----------
        bias_exponent : float
            Exponent controlling bias strength (higher = more bias toward center)
        """
        self.bias_exponent = bias_exponent
    
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample with bias toward center."""
        # Biased sampling toward center
        u = np.random.random(n_particles)
        # Apply bias: smaller radii are more likely
        biased_u = u ** (1.0 / self.bias_exponent)
        radii = inner_radius + (outer_radius - inner_radius) * biased_u
        angles = np.random.random(n_particles) * 2 * np.pi
        
        return radii, angles


class CustomDistribution(ParticleDistribution):
    """Custom distribution using user-provided function."""
    
    def __init__(self, distribution_func):
        """Initialize with custom distribution function.
        
        Parameters
        ----------
        distribution_func : callable
            Function that takes (n_particles, inner_radius, outer_radius) and returns (radii, angles)
        """
        self.distribution_func = distribution_func
    
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample using custom function."""
        return self.distribution_func(n_particles, inner_radius, outer_radius)


class ParticleSystem:
    """Manages the discrete representation of matter in the accretion disk."""
    
    def __init__(
        self,
        black_hole_mass: float = 1.0,
        particle_count: int = 10000,
        distribution_type: str = 'biased_center',
        inner_radius: float = None,
        outer_radius: float = None,
        **distribution_params
    ):
        """Initialize particle system.
        
        Parameters
        ----------
        black_hole_mass : float
            Black hole mass
        particle_count : int
            Number of particles to generate
        distribution_type : str
            Type of distribution ('uniform', 'biased_center', 'custom')
        inner_radius : float
            Inner radius of disk (default: 6*M)
        outer_radius : float
            Outer radius of disk (default: 50*M)
        **distribution_params
            Additional parameters for distribution
        """
        self.black_hole_mass = black_hole_mass
        self.particle_count = particle_count
        
        # Set default disk boundaries
        self.inner_radius = inner_radius if inner_radius is not None else 6.0 * black_hole_mass
        self.outer_radius = outer_radius if outer_radius is not None else 50.0 * black_hole_mass
        
        # Initialize distribution
        self.distribution = self._create_distribution(distribution_type, **distribution_params)
        
        # Particle storage
        self.particles: List[Particle] = []
        self._particle_counter = 0
        
        # Configuration
        self.config = {
            'temperature_profile': 'standard',  # 'standard', 'custom'
            'flux_profile': 'standard',         # 'standard', 'custom'
            'color_scheme': 'temperature',      # 'temperature', 'redshift', 'flux'
            'brightness_scaling': 'logarithmic' # 'linear', 'logarithmic'
        }
    
    def _create_distribution(self, distribution_type: str, **params) -> ParticleDistribution:
        """Create distribution object based on type."""
        if distribution_type == 'uniform':
            return UniformDistribution()
        elif distribution_type == 'biased_center':
            bias_exponent = params.get('bias_exponent', 2.0)
            return BiasedCenterDistribution(bias_exponent)
        elif distribution_type == 'custom':
            if 'distribution_func' not in params:
                raise ValueError("Custom distribution requires 'distribution_func' parameter")
            return CustomDistribution(params['distribution_func'])
        else:
            raise ValueError(f"Unknown distribution type: {distribution_type}")
    
    def generate_particles(self) -> List[Particle]:
        """Generate particles with realistic distribution.
        
        Returns
        -------
        List[Particle]
            List of generated particles
        """
        # Sample positions
        radii, angles = self.distribution.sample_positions(
            self.particle_count, self.inner_radius, self.outer_radius
        )
        
        # Create particles
        self.particles = []
        for i, (r, theta) in enumerate(zip(radii, angles)):
            particle = Particle(
                radius=r,
                angle=theta,
                temperature=self._calculate_temperature(r),
                flux=self._calculate_flux(r),
                redshift_factor=1.0,  # Will be calculated later with lensing
                impact_parameter=0.0,  # Will be calculated with ray tracing
                observed_alpha=theta,  # Will be updated with lensing
                observed_x=0.0,       # Will be calculated
                observed_y=0.0,       # Will be calculated
                image_order=0,        # Will be set during ray tracing
                brightness=1.0,       # Will be calculated
                color=(1.0, 1.0, 1.0), # Will be calculated
                particle_id=self._particle_counter + i,
                is_visible=True
            )
            self.particles.append(particle)
        
        self._particle_counter += len(self.particles)
        return self.particles
    
    def apply_physics(self) -> None:
        """Apply physical properties to all particles."""
        for particle in self.particles:
            particle.temperature = self._calculate_temperature(particle.radius)
            particle.flux = self._calculate_flux(particle.radius)
    
    def _calculate_temperature(self, radius: float) -> float:
        """Calculate temperature at given radius.
        
        Parameters
        ----------
        radius : float
            Radial distance
            
        Returns
        -------
        float
            Temperature
        """
        if self.config['temperature_profile'] == 'standard':
            # Standard accretion disk temperature profile: T ∝ r^(-3/4)
            r_normalized = radius / self.black_hole_mass
            return (r_normalized) ** (-0.75)
        else:
            # Custom temperature profile would go here
            return 1.0
    
    def _calculate_flux(self, radius: float) -> float:
        """Calculate intrinsic flux at given radius.
        
        Parameters
        ----------
        radius : float
            Radial distance
            
        Returns
        -------
        float
            Intrinsic flux
        """
        if self.config['flux_profile'] == 'standard':
            # Standard thin disk flux profile
            r_normalized = radius / self.black_hole_mass
            if r_normalized <= 3.0:  # Inside ISCO
                return 0.0
            
            # Shakura-Sunyaev disk flux
            flux = (1.0 / ((r_normalized - 3) * r_normalized ** 2.5)) * \
                   (np.sqrt(r_normalized) - np.sqrt(6) + 
                    (1.0 / np.sqrt(3)) * np.log(
                        (np.sqrt(r_normalized) + np.sqrt(3)) * (np.sqrt(6) - np.sqrt(3)) /
                        ((np.sqrt(r_normalized) - np.sqrt(3)) * (np.sqrt(6) + np.sqrt(3)))
                    ))
            return max(flux, 0.0)
        else:
            # Custom flux profile would go here
            return 1.0
    
    def get_particles_by_image_order(self, image_order: int) -> List[Particle]:
        """Get particles for specific image order.
        
        Parameters
        ----------
        image_order : int
            Image order (0=direct, 1=ghost, etc.)
            
        Returns
        -------
        List[Particle]
            Particles for specified image order
        """
        return [p for p in self.particles if p.image_order == image_order]
    
    def get_visible_particles(self) -> List[Particle]:
        """Get all visible particles.
        
        Returns
        -------
        List[Particle]
            Visible particles
        """
        return [p for p in self.particles if p.is_visible]
    
    def update_particle_colors(self, color_scheme: str = None) -> None:
        """Update particle colors based on physical properties.
        
        Parameters
        ----------
        color_scheme : str
            Color scheme to use ('temperature', 'redshift', 'flux')
        """
        if color_scheme is not None:
            self.config['color_scheme'] = color_scheme
        
        scheme = self.config['color_scheme']
        
        for particle in self.particles:
            if scheme == 'temperature':
                particle.color = self._temperature_to_color(particle.temperature)
            elif scheme == 'redshift':
                particle.color = self._redshift_to_color(particle.redshift_factor)
            elif scheme == 'flux':
                particle.color = self._flux_to_color(particle.flux)
            else:
                particle.color = (1.0, 1.0, 1.0)  # Default white
    
    def _temperature_to_color(self, temperature: float) -> Tuple[float, float, float]:
        """Convert temperature to RGB color."""
        # Simple temperature-based color mapping (blue-hot to red-hot)
        normalized_temp = np.clip(temperature, 0.0, 2.0) / 2.0
        
        if normalized_temp < 0.5:
            # Blue to white
            factor = normalized_temp * 2
            return (factor, factor, 1.0)
        else:
            # White to red
            factor = (normalized_temp - 0.5) * 2
            return (1.0, 1.0 - factor, 1.0 - factor)
    
    def _redshift_to_color(self, redshift_factor: float) -> Tuple[float, float, float]:
        """Convert redshift factor to RGB color."""
        # Map redshift to blue (blueshifted) to red (redshifted)
        z = redshift_factor - 1.0  # Convert to actual redshift
        normalized_z = np.clip((z + 0.5) / 1.0, 0.0, 1.0)  # Map [-0.5, 0.5] to [0, 1]
        
        if normalized_z < 0.5:
            # Blue (blueshifted)
            factor = (0.5 - normalized_z) * 2
            return (1.0 - factor, 1.0 - factor, 1.0)
        else:
            # Red (redshifted)
            factor = (normalized_z - 0.5) * 2
            return (1.0, 1.0 - factor, 1.0 - factor)
    
    def _flux_to_color(self, flux: float) -> Tuple[float, float, float]:
        """Convert flux to RGB color."""
        # Simple grayscale mapping based on flux
        normalized_flux = np.clip(flux, 0.0, 1.0)
        return (normalized_flux, normalized_flux, normalized_flux)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get particle system statistics.
        
        Returns
        -------
        Dict[str, Any]
            Statistics about the particle system
        """
        if not self.particles:
            return {'particle_count': 0}
        
        temperatures = [p.temperature for p in self.particles]
        fluxes = [p.flux for p in self.particles]
        radii = [p.radius for p in self.particles]
        
        return {
            'particle_count': len(self.particles),
            'visible_count': len(self.get_visible_particles()),
            'radius_range': (min(radii), max(radii)),
            'temperature_range': (min(temperatures), max(temperatures)),
            'flux_range': (min(fluxes), max(fluxes)),
            'image_orders': list(set(p.image_order for p in self.particles)),
            'config': self.config.copy()
        }
    
    def clear_particles(self) -> None:
        """Clear all particles."""
        self.particles.clear()
    
    def set_configuration(self, **config_updates) -> None:
        """Update configuration parameters.
        
        Parameters
        ----------
        **config_updates
            Configuration parameters to update
        """
        self.config.update(config_updates)