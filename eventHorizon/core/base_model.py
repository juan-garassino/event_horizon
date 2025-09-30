# base_model.py

import configparser
import numpy as np
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Enhanced base model with backward compatibility and Luminet support."""
    
    def __init__(
        self, 
        mass: float = 1.0, 
        inclination: float = 80.0, 
        accretion_rate: float = 1e-8,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize base model with physical parameters.
        
        Parameters
        ----------
        mass : float
            Black hole mass
        inclination : float
            Inclination angle in degrees
        accretion_rate : float
            Accretion rate
        config : Optional[Dict[str, Any]]
            Additional configuration parameters
        """
        self.mass = mass
        self.inclination_deg = inclination
        self.inclination_rad = inclination * np.pi / 180
        self.accretion_rate = accretion_rate
        self.config = config if config is not None else {}
        
        # Derived parameters
        self.critical_impact_parameter = 3 * np.sqrt(3) * mass  # Photon sphere
        self.schwarzschild_radius = 2 * mass
        self.isco_radius = 6 * mass  # Innermost stable circular orbit
    
    @staticmethod
    def read_parameters(config_file: str) -> Dict[str, Dict[str, Any]]:
        """Read parameters from configuration file (backward compatibility).
        
        Parameters
        ----------
        config_file : str
            Path to configuration file
            
        Returns
        -------
        Dict[str, Dict[str, Any]]
            Configuration parameters organized by section
        """
        config = configparser.ConfigParser(inline_comment_prefixes='#')
        config.read(config_file)
        return {section: {key: eval(val) for key, val in config[section].items()} 
                for section in config.sections()}
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current model configuration.
        
        Returns
        -------
        Dict[str, Any]
            Current configuration
        """
        return {
            'mass': self.mass,
            'inclination_deg': self.inclination_deg,
            'inclination_rad': self.inclination_rad,
            'accretion_rate': self.accretion_rate,
            'critical_impact_parameter': self.critical_impact_parameter,
            'schwarzschild_radius': self.schwarzschild_radius,
            'isco_radius': self.isco_radius,
            'config': self.config.copy()
        }
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate model configuration.
        
        Returns
        -------
        Dict[str, bool]
            Validation results
        """
        return {
            'mass_positive': self.mass > 0,
            'inclination_valid': 0 <= self.inclination_deg <= 180,
            'accretion_rate_positive': self.accretion_rate > 0
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get model statistics.
        
        Returns
        -------
        Dict[str, Any]
            Model statistics
        """
        return {
            'mass': self.mass,
            'inclination_deg': self.inclination_deg,
            'accretion_rate': self.accretion_rate,
            'critical_impact_parameter': self.critical_impact_parameter,
            'schwarzschild_radius': self.schwarzschild_radius,
            'isco_radius': self.isco_radius
        }
    
    @abstractmethod
    def calculate_impact_parameter(self, *args, **kwargs):
        """Calculate impact parameter (to be implemented by subclasses)."""
        pass