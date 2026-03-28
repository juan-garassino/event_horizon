"""
Unified interface that eliminates code duplication between reference implementations.

This module provides a single, clean interface that consolidates the best algorithms
from both bhsim and luminet while maintaining backward compatibility.
"""
import numpy as np
import pandas as pd
from typing import Union, List, Optional, Dict, Any, Tuple
from abc import ABC, abstractmethod

from .geodesics import UnifiedGeodesics, GeodesicMethod
from .flux_calculations import FluxCalculations


class BlackHoleCalculationInterface(ABC):
    """Abstract interface for black hole calculations."""
    
    @abstractmethod
    def calculate_impact_parameter(self, alpha, radius, inclination, image_order=0, **kwargs):
        """Calculate impact parameter."""
        pass
    
    @abstractmethod
    def generate_isoradial_data(self, alpha_values, radius, image_orders=None, **kwargs):
        """Generate isoradial data."""
        pass
    
    @abstractmethod
    def generate_image_data(self, alpha_values, radius_values, inclination, image_orders=None, **kwargs):
        """Generate complete image data."""
        pass


class UnifiedBlackHoleCalculator(BlackHoleCalculationInterface):
    """Unified calculator that consolidates bhsim and luminet functionality."""
    
    def __init__(
        self, 
        mass: float = 1.0, 
        inclination: float = 80.0, 
        accretion_rate: float = 1e-8,
        method: str = GeodesicMethod.AUTO
    ):
        """Initialize unified black hole calculator.
        
        Parameters
        ----------
        mass : float
            Black hole mass
        inclination : float
            Inclination angle in degrees
        accretion_rate : float
            Accretion rate
        method : str
            Preferred calculation method
        """
        self.mass = mass
        self.inclination_deg = inclination
        self.inclination_rad = inclination * np.pi / 180
        self.accretion_rate = accretion_rate
        self.method = method
        
        # Initialize unified calculators
        self.geodesics = UnifiedGeodesics(mass, method)
        self.flux_calculator = FluxCalculations(mass)
        
        # Configuration
        self.config = {
            'disk_inner_edge': 6.0 * mass,
            'disk_outer_edge': 50.0 * mass,
            'default_solver_params': {
                'midpoint_iterations': 100,
                'initial_guesses': 20,
                'min_periastron': 3.01 * mass,
                'tol': 1e-6
            }
        }
    
    def calculate_impact_parameter(
        self,
        alpha: Union[float, np.ndarray],
        radius: float,
        inclination: Optional[float] = None,
        image_order: int = 0,
        **kwargs
    ) -> Union[float, np.ndarray]:
        """Calculate impact parameter using unified interface."""
        if inclination is None:
            inclination = self.inclination_rad
        
        # Merge with default solver parameters
        solver_params = {**self.config['default_solver_params'], **kwargs}
        
        return self.geodesics.calculate_impact_parameter(
            alpha, radius, inclination, image_order, **solver_params
        )
    
    # Additional methods would be implemented here...
    # For now, using pass to create placeholder structure
    
    def calculate_flux_and_redshift(self, *args, **kwargs):
        """Calculate impact parameters, redshift, and flux."""
        pass
    
    def generate_isoradial_data(self, *args, **kwargs):
        """Generate isoradial data for a single radius."""
        pass
    
    def generate_image_data(self, *args, **kwargs):
        """Generate complete image data for multiple radii."""
        pass


# Convenience function for backward compatibility
def create_unified_calculator(
    mass: float = 1.0,
    inclination: float = 80.0,
    accretion_rate: float = 1e-8,
    method: str = GeodesicMethod.AUTO
) -> UnifiedBlackHoleCalculator:
    """Create a unified black hole calculator with specified parameters."""
    return UnifiedBlackHoleCalculator(mass, inclination, accretion_rate, method)