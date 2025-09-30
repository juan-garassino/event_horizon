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
        pass
    
    def suggest_corrections(self, parameters: Dict[str, Any]) -> List[str]:
        """Suggest corrections for invalid parameters."""
        pass