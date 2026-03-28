# Physics Engine Documentation

## Overview

The PhysicsEngine handles all physical calculations and relativistic effects for particles in the black hole simulation. It integrates extracted algorithms from both bhsim and luminet reference implementations to provide accurate gravitational lensing, redshift calculations, and flux computations.

## Core Architecture

The PhysicsEngine follows a pipeline architecture that processes particles through multiple stages:

```
Particle Input → Basic Physics → Geodesic Ray Tracing → Lensing Effects → Relativistic Effects → Output
```

## Key Components

### Mathematical Calculators

The PhysicsEngine integrates with specialized mathematical modules:

```python
class PhysicsEngine:
    def __init__(self, mass: float = 1.0, spin: float = 0.0):
        self.flux_calculator = FluxCalculations(mass=mass)
        self.relativistic_effects = RelativisticEffects(mass=mass, spin=spin)
        self.geodesics = Geodesics()
        self.numerical_solvers = NumericalSolvers()
```

## Extracted Algorithms

### From Luminet Reference

#### Impact Parameter Calculation
```python
def calc_impact_parameter(self, radius: float, inclination: float, alpha: float, image_order: int = 0) -> Optional[float]:
    """
    Extracted from references/luminet/core/bh_math.py
    Calculates impact parameter for photon trajectories
    """
```

#### Redshift Factor Calculation
```python
def redshift_factor(self, radius: float, angle: float, inclination: float, impact_parameter: float) -> float:
    """
    Extracted redshift_factor function from luminet reference:
    z_factor = (1 + √(M/r³) * b * sin(incl) * sin(angle)) * (1 - 3M/r)^(-1/2)
    
    Combines:
    - Orbital frequency term: √(M/r³) * b * sin(incl) * sin(angle)
    - Gravitational redshift: (1 - 3M/r)^(-1/2)
    """
    try:
        orbital_term = np.sqrt(self.mass / (radius ** 3)) * impact_parameter * np.sin(inclination) * np.sin(angle)
        grav_term = (1 - 3.0 * self.mass / radius) ** (-0.5)
        z_factor = (1.0 + orbital_term) * grav_term
        return z_factor
    except (ValueError, ZeroDivisionError, OverflowError):
        return 1.0
```

#### Flux Calculations
```python
def flux_intrinsic(self, radius: float, accretion_rate: float) -> float:
    """
    Extracted from references/luminet/core/bh_math.py
    Implements Shakura-Sunyaev disk flux formula
    """
    r_normalized = radius / self.mass
    
    if r_normalized <= 3.0:  # Inside ISCO
        return 0.0
    
    # Shakura-Sunyaev disk flux with logarithmic correction
    log_arg = ((np.sqrt(r_normalized) + np.sqrt(3)) * (np.sqrt(6) - np.sqrt(3))) / \
              ((np.sqrt(r_normalized) - np.sqrt(3)) * (np.sqrt(6) + np.sqrt(3)))
    
    flux = (3.0 * self.mass * accretion_rate / (8 * np.pi)) * \
           (1 / ((r_normalized - 3) * radius ** 2.5)) * \
           (np.sqrt(r_normalized) - np.sqrt(6) + 
            (1.0 / np.sqrt(3)) * np.log(log_arg))
    
    return max(flux, 0.0)

def flux_observed(self, radius: float, accretion_rate: float, redshift_factor: float) -> float:
    """
    Extracted flux_observed function from luminet reference:
    F_observed = F_intrinsic / (1+z)^4
    """
    flux_intr = self.flux_intrinsic(radius, accretion_rate)
    return flux_intr / (redshift_factor ** 4)
```

### From bhsim Reference

#### Geodesic Ray Tracing
```python
def calc_impact_parameter_geodesic(self, radius: float, inclination: float, alpha: float, image_order: int = 0) -> Optional[float]:
    """
    Integrates extracted geodesic algorithms from bhsim
    Uses eventHorizon/math/geodesics.py for accurate ray tracing
    """
    try:
        impact_param = self.geodesics.calculate_impact_parameter(
            source_radius=radius,
            source_angle=alpha,
            observer_inclination=inclination,
            black_hole_mass=self.mass,
            image_order=image_order
        )
        return impact_param
    except Exception:
        # Fallback to simplified calculation
        return self.calc_impact_parameter(radius, inclination, alpha, image_order)
```

#### Ghost Image Coordinate Transformation
```python
def reorient_alpha_for_ghost_image(self, alpha: float, inclination: float, image_order: int) -> float:
    """
    Extracted reorient_alpha function from bhsim
    Handles coordinate transformation for ghost images
    """
    if image_order == 1:
        return alpha + np.pi  # Ghost image transformation
    else:
        return alpha
```

## Complete Physics Pipeline

### execute_complete_pipeline()

The main method that processes particles through the complete physics pipeline:

```python
def execute_complete_pipeline(
    self,
    particles: List[Particle],
    inclination: float,
    accretion_rate: float = 1.0,
    enable_lensing: bool = True,
    enable_flux_calculation: bool = True,
    enable_redshift: bool = True
) -> List[Particle]:
    """
    End-to-end pipeline: particle generation → physics → geodesic ray tracing → lensing → visualization
    """
```

#### Pipeline Stages:

1. **Basic Physics Application**
   ```python
   # Apply temperature and intrinsic flux
   particle.temperature = self.calculate_temperature_profile(particle.radius, accretion_rate)
   particle.flux = self.flux_intrinsic(particle.radius, accretion_rate)
   ```

2. **Gravitational Lensing**
   ```python
   if enable_lensing:
       particles = self.apply_lensing_effects(particles, inclination, self.mass)
   ```

3. **Relativistic Effects**
   ```python
   if enable_redshift:
       particles = self.apply_relativistic_effects_to_particles(particles, inclination_rad, accretion_rate)
   ```

4. **Final Processing**
   ```python
   particles = self.finalize_particle_properties(particles)
   ```

## Lensing Effects Implementation

### apply_lensing_effects()

Applies gravitational lensing using extracted algorithms:

```python
def apply_lensing_effects(self, particles: List[Particle], inclination: float, mass: float) -> List[Particle]:
    """
    Complete lensing pipeline using extracted bhsim and luminet algorithms
    """
    for particle in particles:
        # Step 1: Calculate geodesic ray tracing (bhsim algorithms)
        impact_param = self.calc_impact_parameter_geodesic(
            particle.radius, inclination_rad, particle.angle, particle.image_order
        )
        
        # Step 2: Calculate observed coordinates
        particle.observed_x, particle.observed_y = self.calculate_observed_coordinates(
            particle.radius, particle.angle, inclination_rad, impact_param, particle.image_order
        )
        
        # Step 3: Calculate redshift factor (luminet formula)
        particle.redshift_factor = self.redshift_factor(
            particle.radius, particle.angle, inclination_rad, impact_param
        )
        
        # Step 4: Apply relativistic effects to flux
        particle.flux = self.flux_observed(
            particle.radius, 1.0, particle.redshift_factor
        )
        
        # Step 5: Update brightness and visibility
        particle.brightness = self.calculate_brightness(particle.flux)
        particle.is_visible = True if impact_param else False
```

## Temperature and Flux Profiles

### Shakura-Sunyaev Disk Model

Extracted from luminet reference implementation:

```python
def calculate_temperature_profile(self, radius: float, accretion_rate: float = 1.0) -> float:
    """
    Luminet/Shakura-Sunyaev temperature: T ∝ (M*mdot/r³)^(1/4)
    """
    r_normalized = radius / self.mass
    
    if r_normalized <= 3.0:  # Inside ISCO
        return 0.0
    
    temperature = (3.0 * self.mass * accretion_rate / (8.0 * np.pi * radius**3))**(1/4)
    return temperature
```

## Coordinate Transformations

### calculate_observed_coordinates()

Transforms from disk frame to observer frame with lensing:

```python
def calculate_observed_coordinates(
    self, radius: float, angle: float, inclination: float, 
    impact_parameter: float, image_order: int = 0
) -> Tuple[float, float]:
    """
    Coordinate transformation from disk frame to observer frame
    Accounts for gravitational lensing effects
    """
    if image_order == 0:
        # Direct image
        observed_alpha = self.calculate_observed_angle(angle, inclination, impact_parameter)
        x = impact_parameter * np.cos(observed_alpha)
        y = impact_parameter * np.sin(observed_alpha)
    else:
        # Ghost images with reorientation
        observed_alpha = self.reorient_alpha_for_ghost_image(angle, inclination, image_order)
        x = impact_parameter * np.cos(observed_alpha)
        y = impact_parameter * np.sin(observed_alpha)
    
    return x, y
```

## Color and Brightness Calculations

### calculate_particle_color()

Calculates realistic colors based on physical properties:

```python
def calculate_particle_color(
    self, temperature: float, redshift_factor: float, brightness: float
) -> Tuple[float, float, float]:
    """
    Temperature-based color with redshift effects
    - Hot regions: white/blue
    - Cool regions: red
    - Redshift: shifts toward red
    - Blueshift: shifts toward blue
    """
    # Temperature-based blackbody color
    temp_normalized = np.clip(temperature / 2.0, 0.0, 1.0)
    
    if temp_normalized < 0.5:
        r, g, b = 1.0, temp_normalized * 2.0, 0.0  # Red to yellow
    else:
        r, g, b = 1.0, 1.0, (temp_normalized - 0.5) * 2.0  # Yellow to white/blue
    
    # Apply brightness scaling
    r, g, b = r * brightness, g * brightness, b * brightness
    
    # Apply redshift effects
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
```

## Performance Optimizations

### Computational Complexity
- Ray tracing: O(n × m) where n=particles, m=integration_steps
- Physics application: O(n) where n=particle_count
- Coordinate transformation: O(n) where n=particle_count

### Error Handling
- Robust error checking for geodesic integration
- Graceful degradation for failed calculations
- Fallback methods for edge cases

## Usage Examples

### Basic Physics Application
```python
physics_engine = PhysicsEngine(mass=1.0, spin=0.0)
processed_particles = physics_engine.execute_complete_pipeline(
    particles, inclination=80.0, accretion_rate=1.0
)
```

### Custom Physics Configuration
```python
# Enable only specific effects
processed_particles = physics_engine.execute_complete_pipeline(
    particles,
    inclination=80.0,
    enable_lensing=True,
    enable_flux_calculation=True,
    enable_redshift=False
)
```

### Manual Pipeline Control
```python
# Step-by-step processing
for particle in particles:
    particle.temperature = physics_engine.calculate_temperature_profile(particle.radius)
    particle.flux = physics_engine.flux_intrinsic(particle.radius, 1.0)

particles = physics_engine.apply_lensing_effects(particles, 80.0, 1.0)
particles = physics_engine.finalize_particle_properties(particles)
```

## Integration with Other Components

The PhysicsEngine integrates seamlessly with:

- **ParticleSystem**: Processes generated particles
- **Mathematical Modules**: Uses extracted geodesic and flux calculations
- **ParticleRenderer**: Provides processed particles for visualization
- **Configuration System**: Respects quality and performance settings

This comprehensive physics engine provides the scientific accuracy needed for publication-quality black hole visualizations while maintaining the performance required for interactive use.