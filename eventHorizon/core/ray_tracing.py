"""
Ray tracing engine for geodesic calculations in black hole spacetime.

This module provides the core ray tracing functionality for calculating photon
paths and gravitational lensing effects in Schwarzschild spacetime.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .particle_system import Particle


@dataclass
class RayTracingConfig:
    """Configuration for ray tracing calculations."""
    
    # Solver parameters
    solver_method: str = 'runge_kutta'
    integration_steps: int = 1000
    precision_tolerance: float = 1e-8
    max_image_orders: int = 2
    
    # Physical parameters
    black_hole_mass: float = 1.0
    observer_distance: float = 1000.0
    
    # Numerical parameters
    step_size: float = 0.01
    max_iterations: int = 10000
    convergence_tolerance: float = 1e-10
    
    # Method selection
    geodesic_method: str = 'auto'


class RayTracingMethod(ABC):
    """Abstract base class for ray tracing methods."""
    
    @abstractmethod
    def trace_ray(self, *args, **kwargs) -> Dict[str, Any]:
        """Trace a single ray from source to observer."""
        pass


class RayTracingEngine:
    """Main ray tracing engine for gravitational lensing calculations."""
    
    def __init__(self, config: RayTracingConfig = None):
        """Initialize ray tracing engine."""
        self.config = config if config is not None else RayTracingConfig()

    # -------------------------------------------------------------------------
    # 🧠 Restored: Full solver-based tracer producing DataFrames
    # -------------------------------------------------------------------------
    def trace_particles_to_dataframes(
        self,
        particles: List[Particle],
        inclination_deg: float,
        solver_params: Optional[Dict[str, Any]] = None,
        accretion_rate: float = 1.0,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Trace all particles and return (direct_df, ghost_df) for rendering.

        This version calls the real PhysicsEngine.calc_impact_parameter()
        and PhysicsEngine.redshift_factor() methods so both the direct
        and ghost (photon ring) images appear.
        """
        from ..physics.physics_engine import PhysicsEngine

        # small utility to avoid external dependency
        def polar_to_cartesian_lists(rs, thetas, rotation=-np.pi / 2):
            xs, ys = [], []
            for r, t in zip(rs, thetas):
                tr = t + rotation
                xs.append(r * np.cos(tr))
                ys.append(r * np.sin(tr))
            return xs, ys

        engine = PhysicsEngine(mass=self.config.black_hole_mass, spin=0.0)
        inclination = np.deg2rad(inclination_deg)
        solver_params = solver_params or {}

        direct_rows, ghost_rows = [], []

        for particle in particles:
            r = particle.radius
            alpha = particle.angle

            for n in range(min(self.config.max_image_orders, 2)):  # 0=direct, 1=ghost
                try:
                    b = engine.calc_impact_parameter(r, inclination, alpha, n, **solver_params)
                    if b is None or np.isnan(b):
                        continue

                    x, y = polar_to_cartesian_lists([b], [alpha])
                    z_factor = engine.redshift_factor(r, alpha, inclination, b)
                    flux_o = particle.flux / (z_factor**4)

                    row = dict(
                        X=float(x[0]),
                        Y=float(y[0]),
                        impact_parameter=float(b),
                        angle=float(alpha),
                        z_factor=float(z_factor),
                        flux_o=float(flux_o),
                        radius=float(r),
                        image_order=n,
                    )
                    if n == 0:
                        direct_rows.append(row)
                    else:
                        ghost_rows.append(row)
                except Exception:
                    continue

        return pd.DataFrame(direct_rows), pd.DataFrame(ghost_rows)

    # -------------------------------------------------------------------------
    # Simplified utilities preserved for backward compatibility
    # -------------------------------------------------------------------------
    def trace_particle_paths(self, particles: List[Particle], inclination: float) -> List[Particle]:
        """Simplified projection for quick previews."""
        inclination_rad = inclination * np.pi / 180.0
        for particle in particles:
            try:
                cos_gamma = np.cos(particle.angle) / np.sqrt(
                    np.cos(particle.angle) ** 2 + 1 / (np.tan(inclination_rad) ** 2)
                )
                gamma = np.arccos(cos_gamma)
                b = particle.radius * np.sin(gamma)
                particle.observed_x = b * np.cos(particle.angle)
                particle.observed_y = b * np.sin(particle.angle) * np.cos(inclination_rad)
                particle.image_order = 0
                particle.is_visible = True
            except Exception:
                particle.is_visible = False
        return particles

    def calculate_magnification(self, particles: List[Particle]) -> Dict[int, float]:
        """Calculate gravitational magnification for each image."""
        magnifications = {}
        for particle in particles:
            if getattr(particle, "impact_parameter", 0) > 0:
                magnifications[particle.particle_id] = 1.0 / max(
                    particle.impact_parameter / 10.0, 0.1
                )
            else:
                magnifications[particle.particle_id] = 1.0
        return magnifications

    def update_configuration(self, **config_updates) -> None:
        """Update ray tracing configuration."""
        for key, value in config_updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            "solver_method": self.config.solver_method,
            "integration_steps": self.config.integration_steps,
            "precision_tolerance": self.config.precision_tolerance,
            "max_image_orders": self.config.max_image_orders,
            "black_hole_mass": self.config.black_hole_mass,
            "observer_distance": self.config.observer_distance,
            "geodesic_method": self.config.geodesic_method,
        }

    def validate_configuration(self) -> Dict[str, bool]:
        """Validate current configuration."""
        results = {
            "mass_positive": self.config.black_hole_mass > 0,
            "distance_positive": self.config.observer_distance > 0,
            "steps_positive": self.config.integration_steps > 0,
            "tolerance_positive": self.config.precision_tolerance > 0,
            "max_orders_valid": 0 <= self.config.max_image_orders <= 5,
        }
        results["all_valid"] = all(results.values())
        return results


# """
# Ray tracing engine for geodesic calculations in black hole spacetime.

# This module provides the core ray tracing functionality for calculating photon
# paths and gravitational lensing effects in Schwarzschild spacetime.
# """
# import numpy as np
# from typing import List, Dict, Any, Optional, Tuple
# from abc import ABC, abstractmethod
# from dataclasses import dataclass

# from .particle_system import Particle


# @dataclass
# class RayTracingConfig:
#     """Configuration for ray tracing calculations."""
    
#     # Solver parameters
#     solver_method: str = 'runge_kutta'
#     integration_steps: int = 1000
#     precision_tolerance: float = 1e-8
#     max_image_orders: int = 2
    
#     # Physical parameters
#     black_hole_mass: float = 1.0
#     observer_distance: float = 1000.0
    
#     # Numerical parameters
#     step_size: float = 0.01
#     max_iterations: int = 10000
#     convergence_tolerance: float = 1e-10
    
#     # Method selection
#     geodesic_method: str = 'auto'


# class RayTracingMethod(ABC):
#     """Abstract base class for ray tracing methods."""
    
#     @abstractmethod
#     def trace_ray(self, *args, **kwargs) -> Dict[str, Any]:
#         """Trace a single ray from source to observer."""
#         pass


# class RayTracingEngine:
#     """Main ray tracing engine for gravitational lensing calculations."""
    
#     def __init__(self, config: RayTracingConfig = None):
#         """Initialize ray tracing engine."""
#         self.config = config if config is not None else RayTracingConfig()
    
#     def trace_particle_paths(self, particles: List[Particle], inclination: float) -> List[Particle]:
#         """Trace photon paths for all particles.
        
#         Parameters
#         ----------
#         particles : List[Particle]
#             Particles to trace
#         inclination : float
#             Observer inclination angle in degrees
            
#         Returns
#         -------
#         List[Particle]
#             Particles with updated ray tracing results
#         """
#         inclination_rad = inclination * np.pi / 180.0
        
#         for particle in particles:
#             # Use geodesic calculations to trace ray path
#             # This integrates with the extracted algorithms from bhsim/luminet
#             lensed_positions = self.calculate_lensed_positions_for_particle(
#                 particle.radius,
#                 particle.angle,
#                 inclination_rad
#             )
            
#             if lensed_positions:
#                 # Update particle with first (direct) image
#                 particle.observed_x = lensed_positions[0][0]
#                 particle.observed_y = lensed_positions[0][1]
#                 particle.image_order = 0
#                 particle.is_visible = True
#             else:
#                 particle.is_visible = False
        
#         return particles
    
#     def calculate_lensed_positions_for_particle(
#         self, 
#         radius: float, 
#         angle: float, 
#         inclination: float
#     ) -> List[Tuple[float, float]]:
#         """Calculate lensed positions for a single particle.
        
#         Parameters
#         ----------
#         radius : float
#             Source radius
#         angle : float
#             Source angle
#         inclination : float
#             Observer inclination in radians
            
#         Returns
#         -------
#         List[Tuple[float, float]]
#             List of (x, y) positions for different image orders
#         """
#         positions = []
        
#         # Calculate for direct and ghost images
#         for image_order in range(self.config.max_image_orders):
#             # This will use the extracted geodesic algorithms
#             # For now, use simplified calculation
#             try:
#                 # Simple projection for testing
#                 cos_gamma = np.cos(angle) / np.sqrt(np.cos(angle)**2 + 1 / (np.tan(inclination)**2))
#                 gamma = np.arccos(cos_gamma)
                
#                 # Impact parameter calculation (simplified)
#                 b = radius * np.sin(gamma)
                
#                 # Project to observer coordinates
#                 x = b * np.cos(angle)
#                 y = b * np.sin(angle) * np.cos(inclination)
                
#                 positions.append((x, y))
#             except (ValueError, ZeroDivisionError):
#                 continue
        
#         return positions
    
#     def calculate_lensed_positions(self, source_positions: List[Tuple[float, float]], inclination: float) -> Dict[int, List[Tuple[float, float]]]:
#         """Calculate lensed positions for source positions.
        
#         Parameters
#         ----------
#         source_positions : List[Tuple[float, float]]
#             Source positions as (radius, angle) pairs
#         inclination : float
#             Observer inclination angle in degrees
            
#         Returns
#         -------
#         Dict[int, List[Tuple[float, float]]]
#             Dictionary mapping image order to list of lensed positions
#         """
#         inclination_rad = inclination * np.pi / 180.0
#         lensed_positions = {}
        
#         for image_order in range(self.config.max_image_orders):
#             lensed_positions[image_order] = []
            
#             for radius, angle in source_positions:
#                 positions = self.calculate_lensed_positions_for_particle(radius, angle, inclination_rad)
#                 if len(positions) > image_order:
#                     lensed_positions[image_order].append(positions[image_order])
        
#         return lensed_positions
    
#     def calculate_magnification(self, particles: List[Particle]) -> Dict[int, float]:
#         """Calculate gravitational magnification for each image.
        
#         Parameters
#         ----------
#         particles : List[Particle]
#             Particles to calculate magnification for
            
#         Returns
#         -------
#         Dict[int, float]
#             Dictionary mapping particle ID to magnification factor
#         """
#         magnifications = {}
        
#         for particle in particles:
#             # Simple magnification calculation based on impact parameter
#             # Full implementation will use extracted algorithms
#             if particle.impact_parameter > 0:
#                 # Simplified magnification: larger for smaller impact parameters
#                 magnifications[particle.particle_id] = 1.0 / max(particle.impact_parameter / 10.0, 0.1)
#             else:
#                 magnifications[particle.particle_id] = 1.0
        
#         return magnifications
    
#     def update_configuration(self, **config_updates) -> None:
#         """Update ray tracing configuration."""
#         for key, value in config_updates.items():
#             if hasattr(self.config, key):
#                 setattr(self.config, key, value)
    
#     def get_configuration(self) -> Dict[str, Any]:
#         """Get current configuration."""
#         return {
#             'solver_method': self.config.solver_method,
#             'integration_steps': self.config.integration_steps,
#             'precision_tolerance': self.config.precision_tolerance,
#             'max_image_orders': self.config.max_image_orders,
#             'black_hole_mass': self.config.black_hole_mass,
#             'observer_distance': self.config.observer_distance,
#             'geodesic_method': self.config.geodesic_method
#         }
    
#     def validate_configuration(self) -> Dict[str, bool]:
#         """Validate current configuration."""
#         results = {
#             'mass_positive': self.config.black_hole_mass > 0,
#             'distance_positive': self.config.observer_distance > 0,
#             'steps_positive': self.config.integration_steps > 0,
#             'tolerance_positive': self.config.precision_tolerance > 0,
#             'max_orders_valid': 0 <= self.config.max_image_orders <= 5
#         }
        
#         results['all_valid'] = all(results.values())
#         return results