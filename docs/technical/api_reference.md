# API Reference

## Overview

This document provides comprehensive API documentation for the EventHorizon particle-based black hole visualization system. All classes, methods, and functions are documented with their parameters, return values, and usage examples.

## Core Classes

### ParticleSystem

Main class for managing particle-based representation of the accretion disk.

```python
class ParticleSystem:
    def __init__(
        self,
        black_hole_mass: float = 1.0,
        particle_count: int = 10000,
        distribution_type: str = 'biased_center',
        inner_radius: float = None,
        outer_radius: float = None,
        **distribution_params
    )
```

**Parameters:**
- `black_hole_mass` (float): Black hole mass in geometric units
- `particle_count` (int): Number of particles to generate
- `distribution_type` (str): Distribution strategy ('uniform', 'biased_center', 'luminet', 'custom')
- `inner_radius` (float, optional): Inner disk radius (default: 6*M)
- `outer_radius` (float, optional): Outer disk radius (default: 50*M)
- `**distribution_params`: Additional parameters for distribution

#### Methods

##### generate_particles()

```python
def generate_particles(self) -> List[Particle]:
    """Generate particles with realistic distribution."""
```

**Returns:**
- `List[Particle]`: List of generated particles with physical properties

**Example:**
```python
particle_system = ParticleSystem(particle_count=5000, distribution_type='luminet')
particles = particle_system.generate_particles()
```

##### sample_points()

```python
def sample_points(
    self, 
    n_points: int = 1000, 
    inclination: float = 80.0,
    black_hole_mass: float = None,
    solver_params: Dict[str, Any] = None
) -> Tuple[List[Particle], List[Particle]]:
    """Sample points using Luminet's algorithm for both direct and ghost images."""
```

**Parameters:**
- `n_points` (int): Number of points to sample
- `inclination` (float): Observer inclination angle in degrees
- `black_hole_mass` (float, optional): Black hole mass (uses instance mass if None)
- `solver_params` (Dict, optional): Parameters for impact parameter calculation

**Returns:**
- `Tuple[List[Particle], List[Particle]]`: Direct image particles and ghost image particles

**Example:**
```python
direct_particles, ghost_particles = particle_system.sample_points(
    n_points=2000, inclination=85.0
)
```

##### apply_physics()

```python
def apply_physics(self) -> None:
    """Apply physical properties to all particles."""
```

Updates temperature and flux for all particles based on their radial positions.

##### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]:
    """Get particle system statistics."""
```

**Returns:**
- `Dict[str, Any]`: Statistics including particle count, ranges, and configuration

### PhysicsEngine

Handles physical calculations and relativistic effects for particles.

```python
class PhysicsEngine:
    def __init__(self, mass: float = 1.0, spin: float = 0.0)
```

**Parameters:**
- `mass` (float): Black hole mass
- `spin` (float): Black hole spin parameter (0 for Schwarzschild)

#### Methods

##### execute_complete_pipeline()

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
    """Execute the complete physics and lensing pipeline."""
```

**Parameters:**
- `particles` (List[Particle]): Input particles from particle system
- `inclination` (float): Observer inclination angle in degrees
- `accretion_rate` (float): Mass accretion rate
- `enable_lensing` (bool): Whether to apply gravitational lensing
- `enable_flux_calculation` (bool): Whether to calculate flux
- `enable_redshift` (bool): Whether to apply redshift effects

**Returns:**
- `List[Particle]`: Processed particles with all effects applied

**Example:**
```python
physics_engine = PhysicsEngine(mass=1.0)
processed_particles = physics_engine.execute_complete_pipeline(
    particles, inclination=80.0, accretion_rate=1.0
)
```

##### calc_impact_parameter()

```python
def calc_impact_parameter(
    self, 
    radius: float, 
    inclination: float, 
    alpha: float, 
    image_order: int = 0,
    solver_params: Optional[Dict[str, Any]] = None
) -> Optional[float]:
    """Calculate impact parameter using luminet's algorithm."""
```

**Parameters:**
- `radius` (float): Radial distance in accretion disk
- `inclination` (float): Observer inclination angle in radians
- `alpha` (float): Angle along accretion disk
- `image_order` (int): Image order (0=direct, 1=ghost, etc.)
- `solver_params` (Dict, optional): Solver parameters for root finding

**Returns:**
- `Optional[float]`: Impact parameter b, or None if no solution found

##### redshift_factor()

```python
def redshift_factor(
    self, 
    radius: float, 
    angle: float, 
    inclination: float, 
    impact_parameter: float
) -> float:
    """Calculate gravitational redshift factor (1+z) using luminet's formula."""
```

**Parameters:**
- `radius` (float): Radial distance from black hole
- `angle` (float): Angular position in disk
- `inclination` (float): Observer inclination angle
- `impact_parameter` (float): Impact parameter b

**Returns:**
- `float`: Redshift factor (1+z)

##### flux_intrinsic()

```python
def flux_intrinsic(
    self, 
    radius: float, 
    accretion_rate: float
) -> float:
    """Calculate intrinsic flux using luminet's Shakura-Sunyaev disk model."""
```

**Parameters:**
- `radius` (float): Radial distance from black hole
- `accretion_rate` (float): Mass accretion rate

**Returns:**
- `float`: Intrinsic flux

##### flux_observed()

```python
def flux_observed(
    self, 
    radius: float, 
    accretion_rate: float, 
    redshift_factor: float
) -> float:
    """Calculate observed flux using luminet's formula."""
```

**Parameters:**
- `radius` (float): Radial distance from black hole
- `accretion_rate` (float): Mass accretion rate
- `redshift_factor` (float): Redshift factor (1+z)

**Returns:**
- `float`: Observed flux

### ParticleRenderer

Advanced rendering system for Luminet-style visualization.

```python
class ParticleRenderer:
    def __init__(self, config: RenderConfig = None)
```

**Parameters:**
- `config` (RenderConfig, optional): Rendering configuration

#### Methods

##### render_frame()

```python
def render_frame(
    self, 
    particles_df: pd.DataFrame, 
    ghost_particles_df: Optional[pd.DataFrame] = None,
    black_hole_params: Dict[str, Any] = None,
    viewport_config: Dict[str, Any] = None
) -> Tuple[plt.Figure, plt.Axes]:
    """Render a single frame using luminet's dot visualization approach."""
```

**Parameters:**
- `particles_df` (pd.DataFrame): Direct image particles
- `ghost_particles_df` (pd.DataFrame, optional): Ghost image particles
- `black_hole_params` (Dict, optional): Black hole visualization parameters
- `viewport_config` (Dict, optional): Viewport and styling configuration

**Returns:**
- `Tuple[plt.Figure, plt.Axes]`: Matplotlib figure and axes objects

**Example:**
```python
renderer = ParticleRenderer(RenderConfig(power_scale=0.9, levels=100))
fig, ax = renderer.render_frame(particles_df, ghost_particles_df)
```

##### render_animation()

```python
def render_animation(
    self, 
    particle_sequences: List[pd.DataFrame], 
    animation_config: Dict[str, Any] = None
) -> List[Tuple[plt.Figure, plt.Axes]]:
    """Render animation sequence using luminet techniques."""
```

**Parameters:**
- `particle_sequences` (List[pd.DataFrame]): Sequence of particle data frames
- `animation_config` (Dict, optional): Animation configuration

**Returns:**
- `List[Tuple[plt.Figure, plt.Axes]]`: List of rendered frames

##### export_render()

```python
def export_render(
    self, 
    render_data: Tuple[plt.Figure, plt.Axes], 
    filename: str, 
    format: str = 'png', 
    quality: str = 'high'
) -> str:
    """Export rendered image using luminet quality settings."""
```

**Parameters:**
- `render_data` (Tuple): Figure and axes from render_frame()
- `filename` (str): Output filename
- `format` (str): Output format ('png', 'pdf', 'svg')
- `quality` (str): Quality level ('draft', 'standard', 'high', 'publication')

**Returns:**
- `str`: Path to exported file

## Data Structures

### Particle

Core data structure representing a single particle in the accretion disk.

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

### RenderConfig

Configuration for particle rendering.

```python
@dataclass
class RenderConfig:
    dot_size_range: Tuple[float, float] = (0.1, 2.0)
    brightness_scaling: str = 'logarithmic'
    color_scheme: str = 'temperature'
    background_color: str = 'black'
    alpha_blending: bool = True
    anti_aliasing: bool = True
    quality_level: str = 'standard'
    power_scale: float = 0.9  # Power scaling for flux visualization
    levels: int = 100  # Contour levels for tricontourf
```

## Distribution Classes

### ParticleDistribution (Abstract Base)

```python
class ParticleDistribution(ABC):
    @abstractmethod
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample particle positions."""
```

### UniformDistribution

```python
class UniformDistribution(ParticleDistribution):
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample uniformly across disk surface."""
```

### BiasedCenterDistribution

```python
class BiasedCenterDistribution(ParticleDistribution):
    def __init__(self, bias_exponent: float = 2.0):
        """Initialize biased distribution."""
        
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample with bias toward center."""
```

### LuminetDistribution

```python
class LuminetDistribution(ParticleDistribution):
    def __init__(self, bias_toward_center: bool = True):
        """Initialize Luminet distribution."""
        
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample positions using Luminet's algorithm."""
```

## High-Level Functions

### draw_blackhole()

Main entry point for Luminet-style visualization.

```python
def draw_blackhole(
    mass: float = 1.0,
    inclination: float = 80.0,
    particle_count: int = 10000,
    accretion_rate: float = 1.0,
    quality: str = 'standard',
    distribution_type: str = 'luminet',
    enable_ghost_images: bool = True,
    power_scale: float = 0.9,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """Create Luminet-style black hole visualization."""
```

**Parameters:**
- `mass` (float): Black hole mass
- `inclination` (float): Observer inclination angle in degrees
- `particle_count` (int): Number of particles to generate
- `accretion_rate` (float): Mass accretion rate
- `quality` (str): Quality level ('draft', 'standard', 'high', 'publication')
- `distribution_type` (str): Particle distribution type
- `enable_ghost_images` (bool): Whether to include ghost images
- `power_scale` (float): Power scaling for flux visualization
- `**kwargs`: Additional configuration parameters

**Returns:**
- `Tuple[plt.Figure, plt.Axes]`: Matplotlib figure and axes

**Example:**
```python
from eventHorizon import draw_blackhole

fig, ax = draw_blackhole(
    mass=1.0,
    inclination=85.0,
    particle_count=15000,
    quality='high',
    power_scale=0.95
)
```

### plot_points()

Plot particles using luminet's technique.

```python
def plot_points(
    particles: List[Particle],
    ghost_particles: List[Particle] = None,
    power_scale: float = 0.9,
    levels: int = 100,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot particles using luminet's dot visualization."""
```

### plot_isoradials()

Plot isoradial contours.

```python
def plot_isoradials(
    mass: float = 1.0,
    inclination: float = 80.0,
    radial_values: List[float] = None,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot isoradial contours for black hole visualization."""
```

### plot_isoredshifts()

Plot isoredshift contours.

```python
def plot_isoredshifts(
    mass: float = 1.0,
    inclination: float = 80.0,
    redshift_values: List[float] = None,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot isoredshift contours for black hole visualization."""
```

### plot_photon_sphere()

Plot photon sphere boundary.

```python
def plot_photon_sphere(
    mass: float = 1.0,
    inclination: float = 80.0,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot photon sphere boundary."""
```

## Configuration Classes

### ModelConfig

Main configuration class for the entire system.

```python
class ModelConfig:
    def __init__(
        self,
        physics: PhysicsConfig = None,
        particle_system: ParticleSystemConfig = None,
        rendering: RenderConfig = None,
        quality: QualityConfig = None
    )
```

### PhysicsConfig

```python
@dataclass
class PhysicsConfig:
    mass: float = 1.0
    spin: float = 0.0
    accretion_rate: float = 1.0
    enable_lensing: bool = True
    enable_redshift: bool = True
```

### ParticleSystemConfig

```python
@dataclass
class ParticleSystemConfig:
    particle_count: int = 10000
    distribution_type: str = 'luminet'
    inner_radius: float = None
    outer_radius: float = None
    temperature_profile: str = 'luminet'
    flux_profile: str = 'luminet'
```

### QualityConfig

```python
@dataclass
class QualityConfig:
    level: str = 'standard'  # 'draft', 'standard', 'high', 'publication'
    particle_count_multiplier: float = 1.0
    integration_steps: int = 1000
    solver_tolerance: float = 1e-8
```

## Error Handling

### EventHorizonError

Base exception class for EventHorizon-specific errors.

```python
class EventHorizonError(Exception):
    """Base exception for EventHorizon package."""
```

### ParticleSystemError

```python
class ParticleSystemError(EventHorizonError):
    """Exception raised for particle system errors."""
```

### PhysicsEngineError

```python
class PhysicsEngineError(EventHorizonError):
    """Exception raised for physics engine errors."""
```

### RenderingError

```python
class RenderingError(EventHorizonError):
    """Exception raised for rendering errors."""
```

## Usage Examples

### Basic Usage

```python
from eventHorizon import ParticleSystem, PhysicsEngine, ParticleRenderer, RenderConfig

# Create particle system
particle_system = ParticleSystem(
    particle_count=10000,
    distribution_type='luminet'
)

# Generate particles
particles = particle_system.generate_particles()

# Apply physics
physics_engine = PhysicsEngine(mass=1.0)
processed_particles = physics_engine.execute_complete_pipeline(
    particles, inclination=80.0
)

# Render visualization
config = RenderConfig(power_scale=0.9, quality_level='high')
renderer = ParticleRenderer(config)

# Convert to DataFrame for rendering
import pandas as pd
particles_df = pd.DataFrame([
    {
        'X': p.observed_x,
        'Y': p.observed_y,
        'flux_o': p.flux,
        'angle': p.angle,
        'impact_parameter': p.impact_parameter
    }
    for p in processed_particles if p.is_visible and p.image_order == 0
])

fig, ax = renderer.render_frame(particles_df)
```

### Advanced Usage

```python
from eventHorizon import draw_blackhole, plot_points, LuminetDistribution

# High-quality luminet visualization
fig, ax = draw_blackhole(
    mass=1.0,
    inclination=85.0,
    particle_count=20000,
    quality='publication',
    power_scale=0.98,
    enable_ghost_images=True
)

# Custom particle distribution
def custom_distribution(n_particles, inner_r, outer_r):
    # Custom sampling logic
    radii = np.random.exponential(scale=10.0, size=n_particles)
    radii = np.clip(radii, inner_r, outer_r)
    angles = np.random.uniform(0, 2*np.pi, n_particles)
    return radii, angles

particle_system = ParticleSystem(
    distribution_type='custom',
    distribution_func=custom_distribution
)

# Animation sequence
particle_sequences = []
for inclination in np.linspace(60, 90, 30):
    particles = particle_system.generate_particles()
    processed = physics_engine.execute_complete_pipeline(
        particles, inclination=inclination
    )
    particles_df = convert_to_dataframe(processed)
    particle_sequences.append(particles_df)

frames = renderer.render_animation(particle_sequences)
```

This comprehensive API reference provides all the information needed to use EventHorizon's particle-based black hole visualization system effectively.