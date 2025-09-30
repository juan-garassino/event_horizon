"""
Configuration validation utilities.

This module provides comprehensive validation for
Luminet configuration objects.
"""
from typing import Dict, Any, List
from .luminet_config import LuminetConfiguration


class ConfigValidator:
    """Validator for Luminet configuration objects."""
    
    def __init__(self):
        """Initialize configuration validator."""
        pass
    
    def validate_configuration(self, config: LuminetConfiguration) -> Dict[str, Any]:
        """Validate complete configuration."""
        return config.validate()
    
    def check_cross_dependencies(self, config: LuminetConfiguration) -> Dict[str, bool]:
        """Check cross-dependencies between configuration sections."""
        results = {}
        
        # Check particle count vs quality level
        quality_minimums = {
            'draft': 100,
            'standard': 1000,
            'high': 10000,
            'publication': 50000
        }
        
        min_particles = quality_minimums.get(config.visualization.quality_level, 1000)
        results['particle_quality_consistency'] = config.particle_system.particle_count >= min_particles
        
        # Check disk parameters consistency
        results['disk_particle_consistency'] = (
            config.particle_system.min_radius_factor >= config.physical.disk_inner_edge and
            config.particle_system.max_radius_factor <= config.physical.disk_outer_edge
        )
        
        return results
    
    def suggest_improvements(self, config: LuminetConfiguration) -> List[str]:
        """Suggest improvements for configuration."""
        suggestions = []
        
        # Check particle count vs quality level
        quality_minimums = {
            'draft': 1000,
            'standard': 10000,
            'high': 50000,
            'publication': 100000
        }
        
        min_particles = quality_minimums.get(config.visualization.quality_level, 10000)
        if config.particle_system.particle_count < min_particles:
            suggestions.append(
                f"Consider increasing particle count to at least {min_particles} "
                f"for {config.visualization.quality_level} quality"
            )
        
        # Check integration steps
        if (config.ray_tracing.integration_steps < 1000 and 
            config.visualization.quality_level in ['high', 'publication']):
            suggestions.append("Consider increasing integration steps for better accuracy")
        
        return suggestions
    
    def validate_physics_consistency(self, config: LuminetConfiguration) -> Dict[str, bool]:
        """Validate physical consistency of parameters."""
        results = {}
        
        # Check that inner disk edge is above ISCO
        results['inner_edge_above_isco'] = config.physical.disk_inner_edge >= 6.0
        
        # Check that mass is positive
        results['mass_positive'] = config.physical.mass > 0
        
        # Check spin parameter bounds
        results['spin_valid'] = 0 <= abs(config.physical.spin) <= 1
        
        return results