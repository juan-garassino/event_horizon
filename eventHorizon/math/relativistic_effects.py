"""
Relativistic effects calculations for black hole physics.

This module contains calculations for various relativistic effects
including time dilation, redshift, and frame dragging.
"""
import numpy as np
import numpy.typing as npt
import sympy as sy
from typing import Dict, Any, Tuple, Callable, Union

# Import mathematical expressions from geodesics module
from .geodesics import expr_one_plus_z, lambdify


class RelativisticEffects:
    """Calculations for relativistic effects in black hole spacetime."""
    
    def __init__(self, mass: float = 1.0, spin: float = 0.0):
        """Initialize relativistic effects calculator."""
        self.mass = mass
        self.spin = spin
        
        # Initialize lambdified functions
        self._init_relativistic_functions()
    
    def _init_relativistic_functions(self):
        """Initialize commonly used relativistic functions."""
        self.redshift_func = lambdify(["alpha", "b", "theta_0", "M", "r"], expr_one_plus_z())
    
    def gravitational_time_dilation(self, radius: float) -> float:
        """Calculate gravitational time dilation factor.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
            
        Returns
        -------
        float
            Time dilation factor sqrt(1 - 2M/r)
        """
        if radius <= 2.0 * self.mass:
            return 0.0  # At or inside event horizon
        return np.sqrt(1.0 - 2.0 * self.mass / radius)
    
    def doppler_shift(self, velocity: npt.NDArray[np.float64], observer_velocity: npt.NDArray[np.float64]) -> float:
        """Calculate relativistic Doppler shift.
        
        Parameters
        ----------
        velocity : npt.NDArray[np.float64]
            Source velocity vector
        observer_velocity : npt.NDArray[np.float64]
            Observer velocity vector
            
        Returns
        -------
        float
            Doppler shift factor
        """
        # Relativistic velocity addition
        relative_velocity = velocity - observer_velocity
        v_rel_magnitude = np.linalg.norm(relative_velocity)
        
        if v_rel_magnitude >= 1.0:  # Assuming c=1
            return np.inf
            
        gamma = 1.0 / np.sqrt(1.0 - v_rel_magnitude**2)
        return gamma
    
    def gravitational_redshift(
        self, 
        radius: float, 
        angle: float, 
        inclination: float, 
        impact_parameter: float, 
        **kwargs
    ) -> float:
        """Calculate gravitational redshift factor (1+z) using luminet's formula.
        
        This implements the exact redshift_factor function from 
        references/luminet/code/bh_math.py.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        angle : float
            Polar angle in observer frame
        inclination : float
            Observer inclination angle
        impact_parameter : float
            Impact parameter b
        **kwargs
            Additional parameters
            
        Returns
        -------
        float
            Gravitational redshift factor (1+z)
        """
        try:
            # Luminet's redshift factor formula:
            # z_factor = (1. + np.sqrt(bh_mass / (radius ** 3)) * b_ * np.sin(incl) * np.sin(angle)) * \
            #            (1 - 3. * bh_mass / radius) ** -.5
            
            # Orbital frequency term (Doppler effect from orbital motion)
            orbital_term = np.sqrt(self.mass / (radius ** 3)) * impact_parameter * np.sin(inclination) * np.sin(angle)
            
            # Gravitational redshift term
            grav_term = (1 - 3.0 * self.mass / radius) ** (-0.5)
            
            # Combined redshift factor
            z_factor = (1.0 + orbital_term) * grav_term
            
            return float(z_factor)
        except (ValueError, ZeroDivisionError, OverflowError):
            return 1.0  # No redshift if calculation fails
    
    def frame_dragging_effects(self, radius: float, **kwargs) -> Dict[str, float]:
        """Calculate frame dragging effects for rotating black holes.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        **kwargs
            Additional parameters
            
        Returns
        -------
        Dict[str, float]
            Dictionary containing frame dragging effects
        """
        if self.spin == 0.0:
            return {
                'lense_thirring_precession': 0.0,
                'frame_dragging_frequency': 0.0,
                'ergosphere_radius': 0.0
            }
        
        # Simplified frame dragging calculations for Kerr metric
        r_g = 2.0 * self.mass
        a = self.spin * self.mass  # Specific angular momentum
        
        # Lense-Thirring precession frequency
        omega_lt = 2.0 * a * self.mass / (radius**3)
        
        # Frame dragging frequency
        omega_fd = a / (radius**3 + a**2 * radius)
        
        # Ergosphere outer radius (equatorial)
        r_ergo = self.mass + np.sqrt(self.mass**2 - a**2) if a < self.mass else self.mass
        
        return {
            'lense_thirring_precession': omega_lt,
            'frame_dragging_frequency': omega_fd,
            'ergosphere_radius': r_ergo
        }
    
    def light_bending_angle(self, impact_parameter: float) -> float:
        """Calculate light bending angle for weak field approximation.
        
        Parameters
        ----------
        impact_parameter : float
            Impact parameter b
            
        Returns
        -------
        float
            Light bending angle in radians
        """
        if impact_parameter <= 0:
            return np.pi  # Complete deflection
            
        # Weak field approximation: δφ ≈ 4M/b
        return 4.0 * self.mass / impact_parameter
    
    def shapiro_time_delay(self, distance: float, impact_parameter: float, **kwargs) -> float:
        """Calculate Shapiro time delay.
        
        Parameters
        ----------
        distance : float
            Distance to source
        impact_parameter : float
            Impact parameter of light ray
        **kwargs
            Additional parameters
            
        Returns
        -------
        float
            Time delay in geometric units
        """
        if impact_parameter <= 2.0 * self.mass:
            return np.inf  # Ray doesn't escape
            
        # Shapiro delay: Δt ≈ 4M ln(r/2M)
        return 4.0 * self.mass * np.log(distance / (2.0 * self.mass))
    
    def orbital_velocity(self, radius: float) -> float:
        """Calculate orbital velocity at given radius.
        
        Parameters
        ----------
        radius : float
            Orbital radius
            
        Returns
        -------
        float
            Orbital velocity (in units where c=1)
        """
        if radius <= 3.0 * self.mass:  # Inside ISCO
            return np.sqrt(self.mass / (3.0 * self.mass))  # ISCO velocity
            
        return np.sqrt(self.mass / radius)
    
    def redshift_from_orbital_motion(
        self, 
        radius: float, 
        observer_angle: float, 
        inclination: float
    ) -> float:
        """Calculate redshift from orbital motion.
        
        Parameters
        ----------
        radius : float
            Orbital radius
        observer_angle : float
            Observer angle
        inclination : float
            Disk inclination
            
        Returns
        -------
        float
            Redshift factor from orbital motion
        """
        v_orbital = self.orbital_velocity(radius)
        
        # Doppler factor from orbital motion
        cos_phi = np.cos(observer_angle) * np.sin(inclination)
        gamma = 1.0 / np.sqrt(1.0 - v_orbital**2)
        
        return gamma * (1.0 - v_orbital * cos_phi)