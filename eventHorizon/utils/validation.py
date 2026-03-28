"""
Parameter validation utilities.

This module provides comprehensive validation for all
black hole simulation parameters.
"""
import numpy as np
from typing import Dict, Any, List, Union, Optional


class ParameterValidator:
    """Validator for black hole simulation parameters."""
    
    def __init__(self):
        """Initialize parameter validator."""
        self.validation_rules = self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Setup validation rules for different parameter types."""
        return {
            'mass': {
                'type': (int, float),
                'range': (0, float('inf')),
                'required': True
            },
            'spin': {
                'type': (int, float),
                'range': (0, 1),
                'required': False
            },
            'inclination': {
                'type': (int, float),
                'range': (0, 180),
                'required': True
            },
            'radius': {
                'type': (int, float),
                'range': (0, float('inf')),
                'required': True
            },
            'particle_count': {
                'type': int,
                'range': (1, 1000000),
                'required': True
            }
        }
    
    def validate_parameter(self, name: str, value: Any) -> Dict[str, Any]:
        """Validate a single parameter."""
        if name not in self.validation_rules:
            return {'valid': False, 'error': f'Unknown parameter: {name}'}
        
        rules = self.validation_rules[name]
        
        # Type validation
        if not isinstance(value, rules['type']):
            return {'valid': False, 'error': f'Invalid type for {name}'}
        
        # Range validation
        if 'range' in rules:
            min_val, max_val = rules['range']
            if not (min_val <= value <= max_val):
                return {'valid': False, 'error': f'{name} out of range [{min_val}, {max_val}]'}
        
        return {'valid': True}
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate multiple parameters."""
        results = {}
        all_valid = True
        
        for name, value in parameters.items():
            result = self.validate_parameter(name, value)
            results[name] = result
            if not result['valid']:
                all_valid = False
        
        results['all_valid'] = all_valid
        return results
    
    def validate_physical_consistency(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate physical consistency between parameters."""
        results = {'consistent': True, 'warnings': [], 'errors': []}
        
        # Check if radius is outside event horizon
        if 'mass' in parameters and 'radius' in parameters:
            event_horizon = 2.0 * parameters['mass']
            if parameters['radius'] <= event_horizon:
                results['errors'].append(f'Radius {parameters["radius"]} is inside event horizon ({event_horizon})')
                results['consistent'] = False
        
        # Check if particle count is reasonable for given parameters
        if 'particle_count' in parameters:
            count = parameters['particle_count']
            if count > 100000:
                results['warnings'].append(f'Large particle count ({count}) may cause performance issues')
            elif count < 1000:
                results['warnings'].append(f'Small particle count ({count}) may produce low-quality visualization')
        
        # Check inclination angle reasonableness
        if 'inclination' in parameters:
            inclination = parameters['inclination']
            if inclination < 10 or inclination > 170:
                results['warnings'].append(f'Extreme inclination angle ({inclination}°) may produce unusual results')
        
        return results
    
    def suggest_corrections(self, parameters: Dict[str, Any]) -> List[str]:
        """Suggest corrections for invalid parameters."""
        suggestions = []
        
        for name, value in parameters.items():
            validation = self.validate_parameter(name, value)
            if not validation['valid']:
                if name == 'mass' and value <= 0:
                    suggestions.append(f"Set mass to positive value (e.g., mass=1.0)")
                elif name == 'inclination' and not (0 <= value <= 180):
                    suggestions.append(f"Set inclination between 0° and 180° (e.g., inclination=80.0)")
                elif name == 'particle_count' and value <= 0:
                    suggestions.append(f"Set particle_count to positive integer (e.g., particle_count=10000)")
                elif name == 'spin' and not (0 <= value <= 1):
                    suggestions.append(f"Set spin between 0 and 1 (e.g., spin=0.5)")
                else:
                    suggestions.append(f"Fix {name}: {validation['error']}")
        
        return suggestions


def validate_luminet_parameters(
    mass: float = None,
    inclination: float = None,
    particle_count: int = None,
    power_scale: float = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Validate parameters for luminet-style visualization functions.
    
    Parameters
    ----------
    mass : float, optional
        Black hole mass
    inclination : float, optional
        Observer inclination angle in degrees
    particle_count : int, optional
        Number of particles
    power_scale : float, optional
        Power scaling factor
    **kwargs
        Additional parameters
        
    Returns
    -------
    Dict[str, Any]
        Validation results with 'valid' flag and any error messages
        
    Examples
    --------
    >>> result = validate_luminet_parameters(mass=1.0, inclination=80.0, particle_count=10000)
    >>> if not result['valid']:
    ...     print("Validation errors:", result['errors'])
    """
    validator = ParameterValidator()
    results = {'valid': True, 'errors': [], 'warnings': [], 'suggestions': []}
    
    # Validate individual parameters
    params_to_check = {}
    if mass is not None:
        params_to_check['mass'] = mass
    if inclination is not None:
        params_to_check['inclination'] = inclination
    if particle_count is not None:
        params_to_check['particle_count'] = particle_count
    
    # Add power_scale validation
    if power_scale is not None:
        if not isinstance(power_scale, (int, float)):
            results['errors'].append("power_scale must be a number")
            results['valid'] = False
        elif not (0.1 <= power_scale <= 2.0):
            results['warnings'].append(f"power_scale {power_scale} is outside typical range [0.1, 2.0]")
    
    # Validate standard parameters
    validation_results = validator.validate_parameters(params_to_check)
    if not validation_results['all_valid']:
        results['valid'] = False
        for param, result in validation_results.items():
            if param != 'all_valid' and not result['valid']:
                results['errors'].append(f"{param}: {result['error']}")
    
    # Check physical consistency
    consistency = validator.validate_physical_consistency(params_to_check)
    if not consistency['consistent']:
        results['errors'].extend(consistency['errors'])
        results['valid'] = False
    results['warnings'].extend(consistency['warnings'])
    
    # Add suggestions for fixes
    if not results['valid']:
        results['suggestions'] = validator.suggest_corrections(params_to_check)
    
    return results


def validate_and_suggest(func_name: str, **kwargs) -> None:
    """
    Validate parameters and provide helpful suggestions.
    
    Parameters
    ----------
    func_name : str
        Name of the function being called
    **kwargs
        Parameters to validate
        
    Raises
    ------
    ValueError
        If parameters are invalid with helpful error message
    """
    validation = validate_luminet_parameters(**kwargs)
    
    if not validation['valid']:
        error_msg = f"Invalid parameters for {func_name}():\n"
        for error in validation['errors']:
            error_msg += f"  ❌ {error}\n"
        
        if validation['suggestions']:
            error_msg += "\nSuggestions:\n"
            for suggestion in validation['suggestions']:
                error_msg += f"  💡 {suggestion}\n"
        
        if validation['warnings']:
            error_msg += "\nWarnings:\n"
            for warning in validation['warnings']:
                error_msg += f"  ⚠️  {warning}\n"
        
        raise ValueError(error_msg)
    
    # Print warnings even if validation passes
    if validation['warnings']:
        print(f"Warnings for {func_name}():")
        for warning in validation['warnings']:
            print(f"  ⚠️  {warning}")


# Convenience validation functions for specific use cases
def validate_basic_params(mass: float, inclination: float, particle_count: int) -> None:
    """Validate basic black hole visualization parameters."""
    validate_and_suggest(
        "black hole visualization",
        mass=mass,
        inclination=inclination,
        particle_count=particle_count
    )


def validate_advanced_params(mass: float, inclination: float, particle_count: int, 
                           power_scale: float, levels: int) -> None:
    """Validate advanced visualization parameters."""
    # Validate levels parameter
    if not isinstance(levels, int) or levels < 10 or levels > 1000:
        raise ValueError(f"levels must be an integer between 10 and 1000, got {levels}")
    
    validate_and_suggest(
        "advanced visualization",
        mass=mass,
        inclination=inclination,
        particle_count=particle_count,
        power_scale=power_scale
    )