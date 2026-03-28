# Particle System Architecture

## Overview

The ParticleSystem is the foundation of EventHorizon's particle-based black hole visualization. It represents matter in the accretion disk as individual particles/dots, enabling Luminet-style visualization with accurate gravitational lensing effects.

## Core Components

### Particle Data Structure

```python
@dataclass
class Particle:
    # Spatial coordinates (disk frame)
    radius: float           # Radial position in accretion disk
    angle: float           # Angular position
    
    # Physical properties
    temperature: float     # Local temperature
    flux: float           # Intrinsic flux
    redshift_factor: float # Gravitational redshift (1+z)
    
    # Observed coordinates (after lensing)
    impact_parameter: float
    observed_alpha: float
    observed_x: float
    observed_y: float
    
    # Image properties
    image_order: int      # 0=direct, 1=ghost, etc.
    brightness: float     # Rendered brightness
    color: Tuple[float, float, float]  # RGB color values
    
    # Metadata
    particle_id: int = 0
    is_visible: bool = True
```

### Distribution Strategies

The system supports multiple particle distribution strategies extracted from reference implementations:

#### UniformDistribution
- Area-weighted uniform sampling across disk surface
- Standard approach for general-purpose visualization

#### BiasedCenterDistribution
- Configurable bias toward disk center
- Better representation of matter density profiles
- Controlled by `bias_exponent` parameter

#### LuminetDistribution
- **Extracted from luminet reference implementation**
- Linear radius sampling (bias toward center where flux is higher)
- Implements exact algorithm from `references/luminet/core/black_hole.py`
- Creates bias toward center where interesting physics happens

#### CustomDistribution
- User-provided distribution function
- Enables specialized sampling strategies

## Key Methods

### generate_particles()

Generates particles with realistic distribution based on selected strategy:

```python
def generate_particles(self) -> List[Particle]:
    # Sample positions using selected distribution
    radii, angles = self.distribution.sample_positions(
        self.particle_count, self.inner_radius, self.outer_radius
    )
    
    # Create particles with physical properties
    for r, theta in zip(radii, angles):
        particle = Particle(
            radius=r,
            angle=theta,
            temperature=self._calculate_temperature(r),
            flux=self._calculate_flux(r),
            # ... other properties
        )
```

### sample_points()

**Extracted from luminet reference** - implements the exact sampling algorithm:

```python
def sample_points(self, n_points: int, inclination: float) -> Tuple[List[Particle], List[Particle]]:
    """
    Implements luminet's exact sampling algorithm:
    - Linear sampling in radius: r = min_radius + max_radius * random()
    - Uniform sampling in angle: theta = random() * 2 * pi
    - Creates both direct and ghost image particles
    """
```

## Physical Property Calculations

### Temperature Profile

Implements Shakura-Sunyaev disk model from luminet reference:

```python
def _calculate_temperature(self, radius: float) -> float:
    """
    Luminet/Shakura-Sunyaev temperature profile:
    T ∝ (M/r³)^(1/4)
    """
    r_normalized = radius / self.black_hole_mass
    
    if r_normalized <= 3.0:  # Inside ISCO
        return 0.0
    
    # Temperature from Shakura-Sunyaev disk
    temperature = (3.0 * self.black_hole_mass / (8.0 * np.pi * radius**3))**(1/4)
    return temperature
```

### Flux Profile

Implements exact flux calculation from luminet reference:

```python
def _calculate_flux(self, radius: float) -> float:
    """
    Luminet's exact Shakura-Sunyaev disk flux formula
    Extracted from references/luminet/core/bh_math.py
    """
    r_normalized = radius / self.black_hole_mass
    
    if r_normalized <= 3.0:  # Inside ISCO
        return 0.0
    
    # Luminet's flux formula with logarithmic term
    log_arg = ((np.sqrt(r_normalized) + np.sqrt(3)) * (np.sqrt(6) - np.sqrt(3))) / \
              ((np.sqrt(r_normalized) - np.sqrt(3)) * (np.sqrt(6) + np.sqrt(3)))
    
    flux = (1 / ((r_normalized - 3) * radius ** 2.5)) * \
           (np.sqrt(r_normalized) - np.sqrt(6) + 
            (1.0 / np.sqrt(3)) * np.log(log_arg))
    
    return max(flux, 0.0)
```

## Configuration System

The ParticleSystem supports extensive configuration:

```python
config = {
    'temperature_profile': 'luminet',   # 'standard', 'luminet', 'custom'
    'flux_profile': 'luminet',          # 'standard', 'luminet', 'custom'
    'color_scheme': 'temperature',      # 'temperature', 'redshift', 'flux'
    'brightness_scaling': 'logarithmic' # 'linear', 'logarithmic'
}
```

## Performance Considerations

### Memory Usage
- Particle storage: ~100 bytes per particle
- 10,000 particles ≈ 1MB memory footprint
- Configurable particle count for different use cases

### Computational Complexity
- Particle generation: O(n) where n=particle_count
- Physics application: O(n) per particle
- Spatial queries: O(log n) with proper indexing

## Integration with Physics Engine

The ParticleSystem integrates seamlessly with the PhysicsEngine:

```python
# Generate particles
particles = particle_system.generate_particles()

# Apply physics and lensing
physics_engine = PhysicsEngine(mass=1.0)
processed_particles = physics_engine.execute_complete_pipeline(
    particles, inclination=80.0
)
```

## Extracted Algorithms

### From Luminet Reference
- `sample_points()` method - exact particle sampling algorithm
- Temperature and flux profiles - Shakura-Sunyaev disk model
- Linear radius sampling with center bias

### From bhsim Reference
- Impact parameter calculations (integrated via PhysicsEngine)
- Geodesic ray tracing (integrated via mathematical modules)

## Usage Examples

### Basic Particle Generation
```python
particle_system = ParticleSystem(
    particle_count=10000,
    distribution_type='luminet'
)
particles = particle_system.generate_particles()
```

### Custom Distribution
```python
def custom_distribution(n_particles, inner_r, outer_r):
    # Custom sampling logic
    radii = np.random.uniform(inner_r, outer_r, n_particles)
    angles = np.random.uniform(0, 2*np.pi, n_particles)
    return radii, angles

particle_system = ParticleSystem(
    distribution_type='custom',
    distribution_func=custom_distribution
)
```

### Luminet-Style Sampling
```python
# Direct implementation of luminet's algorithm
direct_particles, ghost_particles = particle_system.sample_points(
    n_points=1000,
    inclination=80.0
)
```

## Extension Points

The ParticleSystem is designed for extensibility:

1. **Custom Distributions**: Implement `ParticleDistribution` interface
2. **Custom Physics**: Override temperature/flux calculation methods
3. **Custom Properties**: Extend `Particle` dataclass with additional fields
4. **Custom Sampling**: Implement specialized sampling algorithms

This architecture provides the foundation for accurate, efficient, and extensible particle-based black hole visualization while maintaining scientific fidelity to the original luminet implementation.