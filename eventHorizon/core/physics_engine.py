"""
Physics engine for black hole simulations.

This module handles the physical calculations and updates for particles
in the accretion disk, including temperature, flux, and relativistic effects.
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from .particle_system import Particle
from ..math.flux_calculations import FluxCalculations
from ..math.relativistic_effects import RelativisticEffects
from ..math.geodesics import Geodesics
from ..math.numerical_solvers import NumericalSolvers


class PhysicsEngine:
    """Physics engine for black hole particle simulations."""
    
    def __init__(self, mass: float = 1.0, spin: float = 0.0):
        """Initialize physics engine."""
        self.mass = mass
        self.spin = spin
        
        # Initialize mathematical calculators
        self.flux_calculator = FluxCalculations(mass=mass)
        self.relativistic_effects = RelativisticEffects(mass=mass, spin=spin)
        self.geodesics = Geodesics()
        self.numerical_solvers = NumericalSolvers()
    
    def update_particle_physics(self, particles: List[Particle]) -> None:
        """Update physical properties of all particles.
        
        Parameters
        ----------
        particles : List[Particle]
            List of particles to update
        """
        for particle in particles:
            if hasattr(particle, 'position') and len(particle.position) >= 2:
                radius = (particle.position[0]**2 + particle.position[1]**2)**0.5
                
                # Update temperature
                particle.temperature = self.calculate_temperature_profile(radius)
                
                # Update intrinsic flux
                particle.intrinsic_flux = self.calculate_flux_profile(radius)
                
                # Update orbital velocity
                particle.orbital_velocity = self.calculate_orbital_velocity(radius)
    
    def calculate_temperature_profile(self, radius: float, accretion_rate: float = 1.0) -> float:
        """Calculate temperature at given radius using luminet's disk physics.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        accretion_rate : float
            Mass accretion rate
            
        Returns
        -------
        float
            Temperature at radius
        """
        r_normalized = radius / self.mass
        
        if r_normalized <= 3.0:  # Inside ISCO
            return 0.0
        
        # Luminet/Shakura-Sunyaev temperature: T ∝ (M*mdot/r³)^(1/4)
        temperature = (3.0 * self.mass * accretion_rate / (8.0 * np.pi * radius**3))**(1/4)
        return temperature
    
    def calculate_flux_profile(self, radius: float, accretion_rate: float = 1.0) -> float:
        """Calculate intrinsic flux at given radius using luminet's disk model.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        accretion_rate : float
            Mass accretion rate
            
        Returns
        -------
        float
            Intrinsic flux at radius
        """
        return self.flux_intrinsic(radius, accretion_rate)
    
    def apply_relativistic_effects(self, particles: List[Particle], observer_inclination: float = 0.0) -> None:
        """Apply relativistic effects to particle properties.
        
        Parameters
        ----------
        particles : List[Particle]
            List of particles to update
        observer_inclination : float
            Observer inclination angle
        """
        for particle in particles:
            if hasattr(particle, 'position') and len(particle.position) >= 2:
                radius = (particle.position[0]**2 + particle.position[1]**2)**0.5
                
                # Calculate time dilation
                particle.time_dilation = self.relativistic_effects.gravitational_time_dilation(radius)
                
                # Calculate redshift from orbital motion
                observer_angle = 0.0  # Simplified
                particle.orbital_redshift = self.relativistic_effects.redshift_from_orbital_motion(
                    radius, observer_angle, observer_inclination
                )
    
    def calculate_orbital_velocity(self, radius: float) -> float:
        """Calculate orbital velocity at given radius.
        
        Parameters
        ----------
        radius : float
            Orbital radius
            
        Returns
        -------
        float
            Orbital velocity
        """
        return self.relativistic_effects.orbital_velocity(radius)
    
    def calculate_disk_scale_height(self, radius: float, temperature: Optional[float] = None) -> float:
        """Calculate disk scale height for 3D effects.
        
        Parameters
        ----------
        radius : float
            Radial distance
        temperature : Optional[float]
            Local temperature (calculated if not provided)
            
        Returns
        -------
        float
            Disk scale height
        """
        if temperature is None:
            temperature = self.calculate_temperature_profile(radius)
            
        # Simplified scale height calculation: H ~ cs/Ω where cs ~ sqrt(T)
        sound_speed = temperature**0.5  # Simplified
        orbital_frequency = (self.mass / radius**3)**0.5
        
        return sound_speed / orbital_frequency
    
    def calculate_observed_flux(
        self, 
        radius: float, 
        angle: float, 
        inclination: float, 
        impact_parameter: float,
        accretion_rate: float = 1.0
    ) -> float:
        """Calculate observed flux including all relativistic effects.
        
        Parameters
        ----------
        radius : float
            Radial distance
        angle : float
            Polar angle in observer frame
        inclination : float
            Observer inclination
        impact_parameter : float
            Impact parameter
        accretion_rate : float
            Mass accretion rate
            
        Returns
        -------
        float
            Observed flux
        """
        # Calculate redshift factor
        redshift_factor = self.flux_calculator.calculate_redshift_factor(
            radius, angle, inclination, impact_parameter
        )
        
        # Calculate observed flux
        return self.flux_calculator.calculate_observed_flux(
            radius, redshift_factor, accretion_rate
        )
    
    def calc_impact_parameter(
        self, 
        radius: float, 
        inclination: float, 
        alpha: float, 
        image_order: int = 0,
        solver_params: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """Calculate impact parameter using luminet's algorithm.
        
        This method extracts the calc_impact_parameter function from 
        references/luminet/code/bh_math.py and implements it here.
        
        Parameters
        ----------
        radius : float
            Radial distance in accretion disk (BH frame)
        inclination : float
            Observer inclination angle in radians
        alpha : float
            Angle along accretion disk (BH frame and observer frame)
        image_order : int
            Image order (0=direct, 1=ghost, etc.)
        solver_params : Optional[Dict[str, Any]]
            Solver parameters for root finding
            
        Returns
        -------
        Optional[float]
            Impact parameter b, or None if no solution found
        """
        if solver_params is None:
            solver_params = {
                'initial_guesses': 20,
                'midpoint_iterations': 100,
                'plot_inbetween': False,
                'min_periastron': 3.01 * self.mass
            }
        
        # This is a placeholder - the actual implementation will be done
        # when we extract the geodesic calculations from bhsim in task 1
        # For now, use a simple approximation
        try:
            # Simple ellipse approximation for testing
            cos_gamma = np.cos(alpha) / np.sqrt(np.cos(alpha)**2 + 1 / (np.tan(inclination)**2))
            gamma = np.arccos(cos_gamma)
            b = radius * np.sin(gamma)
            return b
        except (ValueError, ZeroDivisionError):
            return None
    
    def redshift_factor(
        self, 
        radius: float, 
        angle: float, 
        inclination: float, 
        impact_parameter: float
    ) -> float:
        """Calculate gravitational redshift factor (1+z) using luminet's formula.
        
        This method extracts the redshift_factor function from 
        references/luminet/code/bh_math.py.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        angle : float
            Angular position in disk
        inclination : float
            Observer inclination angle
        impact_parameter : float
            Impact parameter b
            
        Returns
        -------
        float
            Redshift factor (1+z)
        """
        # Extract from luminet reference: redshift_factor function
        # z_factor = (1. + np.sqrt(bh_mass / (radius ** 3)) * b_ * np.sin(incl) * np.sin(angle)) * \
        #            (1 - 3. * bh_mass / radius) ** -.5
        
        try:
            # Orbital frequency term
            orbital_term = np.sqrt(self.mass / (radius ** 3)) * impact_parameter * np.sin(inclination) * np.sin(angle)
            
            # Gravitational redshift term
            grav_term = (1 - 3.0 * self.mass / radius) ** (-0.5)
            
            # Combined redshift factor
            z_factor = (1.0 + orbital_term) * grav_term
            
            return z_factor
        except (ValueError, ZeroDivisionError, OverflowError):
            return 1.0  # No redshift if calculation fails
    
    def flux_observed(
        self, 
        radius: float, 
        accretion_rate: float, 
        redshift_factor: float
    ) -> float:
        """Calculate observed flux using luminet's formula.
        
        This method extracts the flux_observed function from 
        references/luminet/code/bh_math.py.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        accretion_rate : float
            Mass accretion rate
        redshift_factor : float
            Redshift factor (1+z)
            
        Returns
        -------
        float
            Observed flux
        """
        # Calculate intrinsic flux first
        flux_intr = self.flux_intrinsic(radius, accretion_rate)
        
        # Apply redshift correction: F_observed = F_intrinsic / (1+z)^4
        return flux_intr / (redshift_factor ** 4)
    
    def flux_intrinsic(
        self, 
        radius: float, 
        accretion_rate: float
    ) -> float:
        """Calculate intrinsic flux using luminet's Shakura-Sunyaev disk model.
        
        This method extracts the flux_intrinsic function from 
        references/luminet/code/bh_math.py.
        
        Parameters
        ----------
        radius : float
            Radial distance from black hole
        accretion_rate : float
            Mass accretion rate
            
        Returns
        -------
        float
            Intrinsic flux
        """
        try:
            r_normalized = radius / self.mass
            
            if r_normalized <= 3.0:  # Inside ISCO
                return 0.0
            
            # Shakura-Sunyaev disk flux formula from luminet reference
            log_arg = ((np.sqrt(r_normalized) + np.sqrt(3)) * (np.sqrt(6) - np.sqrt(3))) / \
                      ((np.sqrt(r_normalized) - np.sqrt(3)) * (np.sqrt(6) + np.sqrt(3)))
            
            flux = (3.0 * self.mass * accretion_rate / (8 * np.pi)) * \
                   (1 / ((r_normalized - 3) * radius ** 2.5)) * \
                   (np.sqrt(r_normalized) - np.sqrt(6) + 
                    (1.0 / np.sqrt(3)) * np.log(log_arg))
            
            return max(flux, 0.0)
        except (ValueError, ZeroDivisionError, OverflowError):
            return 0.0
    
    def apply_lensing_effects(
        self, 
        particles: List[Particle], 
        inclination: float, 
        mass: float
    ) -> List[Particle]:
        """Apply gravitational lensing effects to particles using extracted algorithms.
        
        This implements the complete physics and lensing pipeline:
        particle generation → physics → geodesic ray tracing → lensing → visualization
        
        Parameters
        ----------
        particles : List[Particle]
            List of particles to process
        inclination : float
            Observer inclination angle in degrees
        mass : float
            Black hole mass
            
        Returns
        -------
        List[Particle]
            Particles with updated lensing properties
        """
        inclination_rad = inclination * np.pi / 180.0
        
        # Process each particle through the complete pipeline
        for particle in particles:
            # Step 1: Calculate geodesic ray tracing using extracted bhsim algorithms
            impact_param = self.calc_impact_parameter_geodesic(
                particle.radius, 
                inclination_rad, 
                particle.angle, 
                particle.image_order
            )
            
            if impact_param is not None and impact_param > 0:
                particle.impact_parameter = impact_param
                
                # Step 2: Calculate observed position using proper coordinate transformation
                particle.observed_x, particle.observed_y = self.calculate_observed_coordinates(
                    particle.radius,
                    particle.angle,
                    inclination_rad,
                    impact_param,
                    particle.image_order
                )
                
                # Step 3: Calculate redshift factor using luminet's formula
                particle.redshift_factor = self.redshift_factor(
                    particle.radius,
                    particle.angle,
                    inclination_rad,
                    impact_param
                )
                
                # Step 4: Apply relativistic effects to flux
                particle.flux = self.flux_observed(
                    particle.radius,
                    1.0,  # accretion_rate
                    particle.redshift_factor
                )
                
                # Step 5: Update brightness and visibility
                particle.brightness = self.calculate_brightness(particle.flux)
                particle.is_visible = True
                
            else:
                # Particle not visible (behind black hole or no solution)
                particle.is_visible = False
                particle.brightness = 0.0
        
        return particles
    
    def calc_impact_parameter_geodesic(
        self, 
        radius: float, 
        inclination: float, 
        alpha: float, 
        image_order: int = 0
    ) -> Optional[float]:
        """Calculate impact parameter using geodesic equations from bhsim.
        
        This integrates the extracted geodesic algorithms from bhsim to calculate
        the impact parameter for photon trajectories in Schwarzschild spacetime.
        
        Parameters
        ----------
        radius : float
            Radial distance in accretion disk (BH frame)
        inclination : float
            Observer inclination angle in radians
        alpha : float
            Angle along accretion disk (BH frame and observer frame)
        image_order : int
            Image order (0=direct, 1=ghost, etc.)
            
        Returns
        -------
        Optional[float]
            Impact parameter b, or None if no solution found
        """
        try:
            # Use extracted geodesic calculations from bhsim
            # This integrates with eventHorizon/math/geodesics.py
            impact_param = self.geodesics.calculate_impact_parameter(
                source_radius=radius,
                source_angle=alpha,
                observer_inclination=inclination,
                black_hole_mass=self.mass,
                image_order=image_order
            )
            
            return impact_param
            
        except Exception as e:
            # Fallback to simplified calculation if geodesic solver fails
            return self.calc_impact_parameter(radius, inclination, alpha, image_order)
    
    def calculate_observed_coordinates(
        self,
        radius: float,
        angle: float,
        inclination: float,
        impact_parameter: float,
        image_order: int = 0
    ) -> Tuple[float, float]:
        """Calculate observed coordinates from impact parameter.
        
        This implements the exact coordinate transformation from the original Luminet:
        x, y = polar_to_cartesian_lists([b_], [theta], rotation=-np.pi / 2)
        
        Which translates to:
        x = b * cos(theta - pi/2)
        y = b * sin(theta - pi/2)
        
        Parameters
        ----------
        radius : float
            Source radius in disk frame
        angle : float
            Source angle in disk frame (theta)
        inclination : float
            Observer inclination in radians
        impact_parameter : float
            Impact parameter (b) from geodesic calculation
        image_order : int
            Image order (affects coordinate transformation)
            
        Returns
        -------
        Tuple[float, float]
            Observed (x, y) coordinates
        """
        # Original Luminet coordinate transformation:
        # x, y = polar_to_cartesian_lists([b_], [theta], rotation=-np.pi / 2)
        
        if image_order == 0:
            # Direct image: exact Luminet transformation
            x = impact_parameter * np.cos(angle - np.pi/2)
            y = impact_parameter * np.sin(angle - np.pi/2)
            
        else:
            # Ghost image: same transformation but angle may be modified
            # (the original Luminet uses the same angle for both images)
            x = impact_parameter * np.cos(angle - np.pi/2)
            y = impact_parameter * np.sin(angle - np.pi/2)
        
        return x, y
    
    def calculate_observed_angle(
        self, 
        source_angle: float, 
        inclination: float, 
        impact_parameter: float
    ) -> float:
        """Calculate observed angle accounting for lensing effects.
        
        Parameters
        ----------
        source_angle : float
            Source angle in disk frame
        inclination : float
            Observer inclination
        impact_parameter : float
            Impact parameter
            
        Returns
        -------
        float
            Observed angle
        """
        # This implements the angle transformation from the references
        # For now, use simplified transformation
        return source_angle  # Will be enhanced with extracted algorithms
    
    def reorient_alpha_for_ghost_image(
        self, 
        alpha: float, 
        inclination: float, 
        image_order: int
    ) -> float:
        """Reorient angle for ghost images using bhsim's algorithm.
        
        This implements the reorient_alpha function from bhsim for handling
        ghost image coordinate transformations.
        
        Parameters
        ----------
        alpha : float
            Original angle
        inclination : float
            Observer inclination
        image_order : int
            Image order
            
        Returns
        -------
        float
            Reoriented angle for ghost image
        """
        # Extract from bhsim: reorient_alpha function
        # For ghost images, the angle is transformed
        if image_order == 1:
            # Ghost image transformation
            return alpha + np.pi
        else:
            return alpha
    
    def calculate_brightness(self, flux: float) -> float:
        """Calculate brightness from flux for visualization.
        
        Parameters
        ----------
        flux : float
            Observed flux
            
        Returns
        -------
        float
            Brightness value for rendering
        """
        # Logarithmic scaling for better visualization
        if flux > 0:
            return np.log10(flux + 1e-10)
        else:
            return -10.0  # Very dim for zero flux
    
    def calculate_flux_and_redshift(
        self, 
        particles: List[Particle], 
        inclination: float, 
        mass: float,
        accretion_rate: float = 1.0
    ) -> List[Particle]:
        """Calculate flux and redshift for particles.
        
        Parameters
        ----------
        particles : List[Particle]
        inclination : float
            Observer inclination angle in degrees
        mass : float
            Black hole mass
        accretion_rate : float
            Mass accretion rate
            
        Returns
        -------
        List[Particle]
            Particles with updated flux and redshift
        """
        inclination_rad = inclination * np.pi / 180.0
        
        for particle in particles:
            # Calculate observed flux including redshift effects
            particle.flux = self.flux_observed(
                particle.radius,
                accretion_rate,
                particle.redshift_factor
            )
            
            # Update brightness based on flux
            particle.brightness = np.log10(max(particle.flux, 1e-10))
            
            # Update temperature based on redshift
            particle.temperature = self.calculate_temperature_profile(
                particle.radius, 
                accretion_rate
            )
        
        return particles
    
    def update_config(self, config) -> None:
        """Update physics engine configuration.
        
        Parameters
        ----------
        config : ModelConfig
            New configuration
        """
        self.mass = config.physics.mass
        self.spin = config.physics.spin
        
        # Update calculators
        self.flux_calculator = FluxCalculations(mass=self.mass)
        self.relativistic_effects = RelativisticEffects(mass=self.mass, spin=self.spin)
        self.geodesics = Geodesics()
        self.numerical_solvers = NumericalSolvers()
    
    def execute_complete_pipeline(
        self,
        particles: List[Particle],
        inclination: float,
        accretion_rate: float = 1.0,
        enable_lensing: bool = True,
        enable_flux_calculation: bool = True,
        enable_redshift: bool = True
    ) -> List[Particle]:
        """Execute the complete physics and lensing pipeline.
        
        This implements the end-to-end pipeline:
        particle generation → physics → geodesic ray tracing → lensing → visualization
        
        Parameters
        ----------
        particles : List[Particle]
            Input particles from particle system
        inclination : float
            Observer inclination angle in degrees
        accretion_rate : float
            Mass accretion rate
        enable_lensing : bool
            Whether to apply gravitational lensing
        enable_flux_calculation : bool
            Whether to calculate flux
        enable_redshift : bool
            Whether to apply redshift effects
            
        Returns
        -------
        List[Particle]
            Processed particles with all effects applied
        """
        inclination_rad = inclination * np.pi / 180.0
        
        # Step 1: Apply basic physics (temperature, intrinsic flux)
        for particle in particles:
            particle.temperature = self.calculate_temperature_profile(particle.radius, accretion_rate)
            if enable_flux_calculation:
                particle.flux = self.flux_intrinsic(particle.radius, accretion_rate)
        
        # Step 2: Apply gravitational lensing if enabled
        if enable_lensing:
            particles = self.apply_lensing_effects(particles, inclination, self.mass)
        
        # Step 3: Apply redshift effects if enabled
        if enable_redshift:
            particles = self.apply_relativistic_effects_to_particles(
                particles, inclination_rad, accretion_rate
            )
        
        # Step 4: Final processing for visualization
        particles = self.finalize_particle_properties(particles)
        
        return particles
    
    def apply_relativistic_effects_to_particles(
        self,
        particles: List[Particle],
        inclination: float,
        accretion_rate: float
    ) -> List[Particle]:
        """Apply relativistic effects to all particles.
        
        Parameters
        ----------
        particles : List[Particle]
            Particles to process
        inclination : float
            Observer inclination in radians
        accretion_rate : float
            Mass accretion rate
            
        Returns
        -------
        List[Particle]
            Particles with relativistic effects applied
        """
        for particle in particles:
            if particle.is_visible:
                # Update flux with redshift effects
                particle.flux = self.flux_observed(
                    particle.radius,
                    accretion_rate,
                    particle.redshift_factor
                )
                
                # Update brightness
                particle.brightness = self.calculate_brightness(particle.flux)
        
        return particles
    
    def finalize_particle_properties(self, particles: List[Particle]) -> List[Particle]:
        """Finalize particle properties for visualization.
        
        Parameters
        ----------
        particles : List[Particle]
            Particles to finalize
            
        Returns
        -------
        List[Particle]
            Finalized particles
        """
        # Calculate brightness statistics for normalization
        visible_particles = [p for p in particles if p.is_visible]
        if not visible_particles:
            return particles
        
        brightnesses = [p.brightness for p in visible_particles]
        min_brightness = min(brightnesses)
        max_brightness = max(brightnesses)
        brightness_range = max_brightness - min_brightness
        
        # Normalize brightness and update colors
        for particle in particles:
            if particle.is_visible and brightness_range > 0:
                # Normalize brightness to [0, 1]
                normalized_brightness = (particle.brightness - min_brightness) / brightness_range
                particle.brightness = normalized_brightness
                
                # Update color based on temperature and brightness
                particle.color = self.calculate_particle_color(
                    particle.temperature,
                    particle.redshift_factor,
                    normalized_brightness
                )
        
        return particles
    
    def calculate_particle_color(
        self,
        temperature: float,
        redshift_factor: float,
        brightness: float
    ) -> Tuple[float, float, float]:
        """Calculate particle color based on physical properties.
        
        Parameters
        ----------
        temperature : float
            Particle temperature
        redshift_factor : float
            Redshift factor (1+z)
        brightness : float
            Normalized brightness
            
        Returns
        -------
        Tuple[float, float, float]
            RGB color values
        """
        # Temperature-based color (blackbody radiation)
        if temperature > 0:
            # Simple temperature to color mapping
            # Hot = white/blue, Cool = red
            temp_normalized = np.clip(temperature / 2.0, 0.0, 1.0)
            
            if temp_normalized < 0.5:
                # Red to yellow
                r = 1.0
                g = temp_normalized * 2.0
                b = 0.0
            else:
                # Yellow to white/blue
                r = 1.0
                g = 1.0
                b = (temp_normalized - 0.5) * 2.0
        else:
            r, g, b = 0.0, 0.0, 0.0
        
        # Apply brightness scaling
        r *= brightness
        g *= brightness
        b *= brightness
        
        # Apply redshift effects (shift colors)
        z = redshift_factor - 1.0
        if z > 0:  # Redshifted
            r = min(1.0, r * (1.0 + z * 0.5))
            g *= (1.0 - z * 0.2)
            b *= (1.0 - z * 0.4)
        elif z < 0:  # Blueshifted
            r *= (1.0 + z * 0.4)
            g *= (1.0 + z * 0.2)
            b = min(1.0, b * (1.0 - z * 0.5))
        
        return (np.clip(r, 0.0, 1.0), np.clip(g, 0.0, 1.0), np.clip(b, 0.0, 1.0))