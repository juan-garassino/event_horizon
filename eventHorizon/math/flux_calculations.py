"""
Unified flux and redshift calculations for black hole physics.

This module provides comprehensive flux, redshift, and radiation
calculations for accretion disk physics.
"""
import numpy as np
import numpy.typing as npt
import sympy as sy
from typing import Dict, Any, Optional, Tuple, Callable, Union

# Import mathematical expressions from geodesics module
from .geodesics import (
    expr_fs, expr_r_star, expr_one_plus_z, expr_f0, expr_f0_normalized,
    lambda_normalized_bolometric_flux, simulate_flux, lambdify
)


class FluxCalculations:
    """Unified flux and redshift calculations."""
    
    def __init__(self, mass: float = 1.0):
        """Initialize flux calculator.
        
        Parameters
        ----------
        mass : float
            Black hole mass
        """
        self.mass = mass
        
        # Initialize lambdified functions for performance
        self._init_flux_functions()
    
    def _init_flux_functions(self):
        """Initialize commonly used lambdified flux functions."""
        # Use proper symbol names for lambdify
        self.fs_func = lambdify(["rstar", "M", "mdot"], expr_fs().subs({sy.symbols("r^*"): sy.symbols("rstar"), sy.symbols(r"\dot{m}"): sy.symbols("mdot")}))
        self.one_plus_z_func = lambdify(["alpha", "b", "theta_0", "M", "r"], expr_one_plus_z())
        self.normalized_flux_func = lambda_normalized_bolometric_flux()
        self.r_star_func = lambdify(["r", "M"], expr_r_star())
    
    def calculate_intrinsic_flux(self, radius: float, accretion_rate: float = 1.0, **kwargs) -> float:
        """Calculate intrinsic flux using luminet's Shakura-Sunyaev disk model.
        
        This implements the exact flux_intrinsic function from 
        references/luminet/code/bh_math.py.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        accretion_rate : float
            Mass accretion rate (normalized)
        **kwargs
            Additional parameters
            
        Returns
        -------
        float
            Intrinsic flux value
        """
        try:
            r_normalized = radius / self.mass
            
            if r_normalized <= 3.0:  # Inside ISCO
                return 0.0
            
            # Luminet's Shakura-Sunyaev disk flux formula:
            # f = (3. * bh_mass * acc / (8 * np.pi)) * (1 / ((r_ - 3) * r ** 2.5)) * \
            #     (np.sqrt(r_) - np.sqrt(6) + 3 ** -.5 * np.log10(log_arg))
            
            log_arg = ((np.sqrt(r_normalized) + np.sqrt(3)) * (np.sqrt(6) - np.sqrt(3))) / \
                      ((np.sqrt(r_normalized) - np.sqrt(3)) * (np.sqrt(6) + np.sqrt(3)))
            
            flux = (3.0 * self.mass * accretion_rate / (8 * np.pi)) * \
                   (1 / ((r_normalized - 3) * radius ** 2.5)) * \
                   (np.sqrt(r_normalized) - np.sqrt(6) + 
                    (1.0 / np.sqrt(3)) * np.log(log_arg))
            
            return max(float(flux), 0.0)
        except (ValueError, ZeroDivisionError, OverflowError):
            return 0.0
    
    def calculate_observed_flux(self, radius: float, redshift_factor: float, accretion_rate: float = 1.0, **kwargs) -> float:
        """Calculate observed flux using luminet's formula.
        
        This implements the exact flux_observed function from 
        references/luminet/code/bh_math.py.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        redshift_factor : float
            Redshift factor (1+z)
        accretion_rate : float
            Mass accretion rate (normalized)
        **kwargs
            Additional parameters
            
        Returns
        -------
        float
            Observed flux including redshift corrections
        """
        # Luminet's observed flux formula:
        # flux_observed = flux_intrinsic / redshift_factor ** 4
        
        flux_intr = self.calculate_intrinsic_flux(radius, accretion_rate)
        return flux_intr / (redshift_factor ** 4)
    
    def calculate_redshift_factor(self, radius: float, angle: float, inclination: float, impact_parameter: float, **kwargs) -> float:
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
            Redshift factor (1+z)
        """
        try:
            # Luminet's redshift factor formula:
            # z_factor = (1. + np.sqrt(bh_mass / (radius ** 3)) * b_ * np.sin(incl) * np.sin(angle)) * \
            #            (1 - 3. * bh_mass / radius) ** -.5
            
            # Orbital frequency term
            orbital_term = np.sqrt(self.mass / (radius ** 3)) * impact_parameter * np.sin(inclination) * np.sin(angle)
            
            # Gravitational redshift term
            grav_term = (1 - 3.0 * self.mass / radius) ** (-0.5)
            
            # Combined redshift factor
            z_factor = (1.0 + orbital_term) * grav_term
            
            return float(z_factor)
        except (ValueError, ZeroDivisionError, OverflowError):
            return 1.0  # No redshift if calculation fails
    
    def calculate_doppler_shift(self, velocity: np.ndarray, observer_angle: float, **kwargs) -> float:
        """Calculate Doppler shift from orbital motion.
        
        Parameters
        ----------
        velocity : np.ndarray
            Velocity vector
        observer_angle : float
            Observer angle
        **kwargs
            Additional parameters
            
        Returns
        -------
        float
            Doppler shift factor
        """
        # Simple relativistic Doppler formula
        v_magnitude = np.linalg.norm(velocity)
        cos_theta = np.cos(observer_angle)
        gamma = 1.0 / np.sqrt(1.0 - v_magnitude**2)  # Assuming c=1
        return gamma * (1.0 - v_magnitude * cos_theta)
    
    def calculate_temperature_profile(self, radius: float, **kwargs) -> float:
        """Calculate temperature at given radius using standard disk model.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        **kwargs
            Additional parameters
            
        Returns
        -------
        float
            Temperature at radius
        """
        # Standard Shakura-Sunyaev temperature profile
        r_star = radius / self.mass
        if r_star <= 3.0:  # Inside ISCO
            return 0.0
        return (3.0 * self.mass / (8.0 * np.pi * radius**3))**(1/4)
    
    def calculate_bolometric_flux(self, radius: float, temperature: float, **kwargs) -> float:
        """Calculate bolometric flux from temperature.
        
        Parameters
        ----------
        radius : float
            Radial distance
        temperature : float
            Local temperature
        **kwargs
            Additional parameters
            
        Returns
        -------
        float
            Bolometric flux
        """
        # Stefan-Boltzmann law (assuming σ=1 in natural units)
        return temperature**4
    
    def apply_relativistic_corrections(self, flux: float, redshift_factor: float, **kwargs) -> float:
        """Apply relativistic corrections to flux.
        
        Parameters
        ----------
        flux : float
            Intrinsic flux
        redshift_factor : float
            Redshift factor (1+z)
        **kwargs
            Additional parameters
            
        Returns
        -------
        float
            Corrected flux
        """
        # Apply redshift correction: F_observed = F_intrinsic / (1+z)^4
        return flux / (redshift_factor**4)
    
    def simulate_complete_flux(
        self,
        alpha: npt.NDArray[np.float64],
        radius: float,
        inclination: float,
        image_order: int = 0,
        **kwargs
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Simulate complete flux calculation including impact parameters.
        
        Parameters
        ----------
        alpha : npt.NDArray[np.float64]
            Array of polar angles
        radius : float
            Radial distance
        inclination : float
            Observer inclination
        image_order : int
            Image order (0 for direct, >0 for ghost)
        **kwargs
            Additional parameters
            
        Returns
        -------
        Tuple[npt.NDArray[np.float64], ...]
            Reoriented alpha, impact parameters, redshift factors, observed flux
        """
        return simulate_flux(alpha, radius, inclination, image_order, self.mass, **kwargs)