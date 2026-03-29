"""
Unified reference implementation adapter.

This module provides a unified interface for adapting between different
reference implementations and the eventHorizon framework.
"""
from typing import Dict, Any, Optional, Protocol, List
import numpy as np


class ReferenceAdapter(Protocol):
    """Protocol for reference implementation adapters."""
    
    def adapt_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt parameters from reference format to eventHorizon format."""
        ...
    
    def adapt_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt results from eventHorizon format to reference format."""
        ...


class UnifiedReferenceAdapter:
    """Unified adapter for all reference implementations."""
    
    def __init__(self, reference_type: str = "auto"):
        """Initialize adapter with reference type detection."""
        self.reference_type = reference_type
        self.bhsim_params = {}
        self.luminet_params = {}
        
    def adapt_bhsim_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt bhsim-style parameters to unified format."""
        unified_params = {
            'mass': params.get('mass', 1.0),
            'inclination_deg': params.get('inclination', 80.0),
            'particle_count': params.get('n_points', 10000),
            'inner_radius': params.get('min_radius', 6.0),
            'outer_radius': params.get('max_radius', 50.0),
            'solver_method': params.get('solver_method', 'runge_kutta'),
            'integration_steps': params.get('integration_steps', 1000),
            'precision_tolerance': params.get('tolerance', 1e-8)
        }
        return unified_params
        
    def adapt_luminet_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt luminet-style parameters to unified format."""
        unified_params = {
            'mass': params.get('bh_mass', 1.0),
            'inclination_deg': params.get('incl', 80.0),
            'particle_count': params.get('n_points', 10000),
            'inner_radius': params.get('min_radius_', 6.0),
            'outer_radius': params.get('max_radius_', 50.0),
            'accretion_rate': params.get('acc', 1.0),
            'initial_guesses': params.get('initial_guesses', 20),
            'midpoint_iterations': params.get('midpoint_iterations', 100)
        }
        return unified_params
        
    def detect_reference_type(self, params: Dict[str, Any]) -> str:
        """Auto-detect reference implementation type from parameters."""
        # Check for bhsim-specific parameters
        bhsim_indicators = ['solver_method', 'integration_steps', 'max_radius']
        bhsim_score = sum(1 for key in bhsim_indicators if key in params)
        
        # Check for luminet-specific parameters
        luminet_indicators = ['bh_mass', 'incl', 'acc', 'min_radius_', 'max_radius_']
        luminet_score = sum(1 for key in luminet_indicators if key in params)
        
        if luminet_score > bhsim_score:
            return 'luminet'
        elif bhsim_score > 0:
            return 'bhsim'
        else:
            return 'unified'
        
    def convert_to_unified(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert any reference format to unified eventHorizon format."""
        if self.reference_type == "auto":
            detected_type = self.detect_reference_type(params)
        else:
            detected_type = self.reference_type
            
        if detected_type == 'bhsim':
            return self.adapt_bhsim_parameters(params)
        elif detected_type == 'luminet':
            return self.adapt_luminet_parameters(params)
        else:
            # Already in unified format
            return params.copy()
        
    def convert_from_unified(self, params: Dict[str, Any], target_format: str) -> Dict[str, Any]:
        """Convert from unified format to specific reference format."""
        if target_format == 'bhsim':
            return {
                'mass': params.get('mass', 1.0),
                'inclination': params.get('inclination_deg', 80.0),
                'n_points': params.get('particle_count', 10000),
                'min_radius': params.get('inner_radius', 6.0),
                'max_radius': params.get('outer_radius', 50.0),
                'solver_method': params.get('solver_method', 'runge_kutta'),
                'integration_steps': params.get('integration_steps', 1000),
                'tolerance': params.get('precision_tolerance', 1e-8)
            }
        elif target_format == 'luminet':
            return {
                'bh_mass': params.get('mass', 1.0),
                'incl': params.get('inclination_deg', 80.0),
                'n_points': params.get('particle_count', 10000),
                'min_radius_': params.get('inner_radius', 6.0),
                'max_radius_': params.get('outer_radius', 50.0),
                'acc': params.get('accretion_rate', 1.0),
                'initial_guesses': params.get('initial_guesses', 20),
                'midpoint_iterations': params.get('midpoint_iterations', 100)
            }
        else:
            return params.copy()
    
    def create_physics_engine_from_params(self, params: Dict[str, Any]):
        """Create a physics engine from reference parameters."""
        from ..math.geodesics import UnifiedGeodesics

        unified_params = self.convert_to_unified(params)

        return UnifiedGeodesics(
            mass=unified_params.get('mass', 1.0),
        )
    
    def execute_reference_compatible_pipeline(
        self,
        params: Dict[str, Any],
        particles: Optional[List] = None
    ) -> Dict[str, Any]:
        """Execute pipeline with reference compatibility.
        
        Parameters
        ----------
        params : Dict[str, Any]
            Parameters in any reference format
        particles : Optional[List]
            Pre-generated particles (optional)
            
        Returns
        -------
        Dict[str, Any]
            Results in unified format
        """
        from ..math.fast_geodesics import generate_particles_fast

        # Convert parameters to unified format
        unified_params = self.convert_to_unified(params)

        mass = unified_params.get('mass', 1.0)
        inclination = unified_params.get('inclination', 1.4)
        particle_count = unified_params.get('particle_count', 10000)

        # Use fast vectorized pipeline
        direct_df, ghost_df, min_flux, max_flux = generate_particles_fast(
            particle_count=particle_count,
            mass=mass,
            inclination=inclination,
        )

        # Return results in unified format
        return {
            'direct_particles': direct_df,
            'ghost_particles': ghost_df,
            'min_flux': min_flux,
            'max_flux': max_flux,
            'parameters': unified_params,
        }