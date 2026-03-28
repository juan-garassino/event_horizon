# Developer Guide

## Overview

This guide provides comprehensive information for developers who want to extend, modify, or contribute to the EventHorizon particle-based black hole visualization system. It covers architecture patterns, extension points, best practices, and development workflows.

## Architecture Overview

EventHorizon follows a modular pipeline architecture designed for extensibility and maintainability:

```
Configuration → Particle Generation → Physics Calculations → Geodesic Ray Tracing → Lensing Effects → Visualization
```

### Core Design Principles

1. **Modular Architecture**: Each component has well-defined interfaces and minimal coupling
2. **Scientific Accuracy**: All algorithms are extracted from validated reference implementations
3. **Performance Optimization**: Vectorized operations and efficient data structures
4. **Extensibility**: Clear extension points for custom functionality
5. **Backward Compatibility**: Maintains existing visualization capabilities

## Development Environment Setup

### Prerequisites

```bash
# Required dependencies
pip install numpy scipy matplotlib pandas sympy

# Optional dependencies for advanced features
pip install jupyter ipywidgets tqdm

# Development dependencies
pip install pytest black flake8 mypy sphinx
```

### Project Structure

```
eventHorizon/
├── core/                    # Core models and abstractions
│   ├── particle_system.py   # Particle management
│   ├── physics_engine.py    # Physical calculations
│   └── base_model.py        # Base classes
├── math/                    # Mathematical computations
│   ├── geodesics.py         # Geodesic calculations
│   ├── flux_calculations.py # Flux computations
│   └── coordinate_systems.py # Coordinate transformations
├── visualization/           # Rendering and plotting
│   ├── particle_renderer.py # Particle rendering
│   ├── luminet_compositor.py # Image composition
│   └── unified_plotter.py   # Unified plotting interface
├── config/                  # Configuration system
│   ├── model_config.py      # Main configuration
│   └── presets.py          # Quality presets
└── utils/                   # Utilities and helpers
    ├── validation.py        # Input validation
    └── performance.py       # Performance monitoring
```

## Extension Points

### 1. Custom Particle Distributions

Create custom particle sampling strategies by implementing the `ParticleDistribution` interface:

```python
from eventHorizon.core.particle_system import ParticleDistribution
import numpy as np

class CustomDistribution(ParticleDistribution):
    """Example custom distribution with spiral pattern."""
    
    def __init__(self, spiral_factor: float = 2.0):
        self.spiral_factor = spiral_factor
    
    def sample_positions(
        self, 
        n_particles: int, 
        inner_radius: float, 
        outer_radius: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Sample particles in spiral pattern."""
        
        # Radial sampling
        u = np.random.random(n_particles)
        radii = inner_radius + (outer_radius - inner_radius) * u
        
        # Spiral angular sampling
        angles = self.spiral_factor * np.pi * u + \
                np.random.normal(0, 0.1, n_particles)  # Add noise
        
        return radii, angles

# Usage
particle_system = ParticleSystem(
    distribution_type='custom',
    distribution_func=CustomDistribution(spiral_factor=3.0)
)
```

### 2. Custom Physics Models

Extend the physics engine with custom temperature and flux profiles:

```python
from eventHorizon.core.physics_engine import PhysicsEngine

class CustomPhysicsEngine(PhysicsEngine):
    """Extended physics engine with custom disk model."""
    
    def calculate_temperature_profile(
        self, 
        radius: float, 
        accretion_rate: float = 1.0
    ) -> float:
        """Custom temperature profile with additional heating."""
        
        # Start with standard Shakura-Sunyaev
        base_temp = super().calculate_temperature_profile(radius, accretion_rate)
        
        # Add custom heating mechanism
        r_normalized = radius / self.mass
        
        if 6.0 <= r_normalized <= 20.0:
            # Enhanced heating in intermediate region
            heating_factor = 1.5 * np.exp(-(r_normalized - 10.0)**2 / 20.0)
            return base_temp * (1.0 + heating_factor)
        
        return base_temp
    
    def custom_magnetic_field_effects(
        self, 
        particles: List[Particle]
    ) -> List[Particle]:
        """Apply custom magnetic field effects."""
        
        for particle in particles:
            # Custom magnetic field model
            b_field_strength = self.calculate_magnetic_field(particle.radius)
            
            # Modify particle properties based on magnetic field
            particle.temperature *= (1.0 + 0.1 * b_field_strength)
            particle.flux *= (1.0 + 0.05 * b_field_strength)
        
        return particles
    
    def calculate_magnetic_field(self, radius: float) -> float:
        """Calculate magnetic field strength at radius."""
        r_normalized = radius / self.mass
        return np.exp(-r_normalized / 10.0)  # Exponential decay

# Usage
custom_physics = CustomPhysicsEngine(mass=1.0)
processed_particles = custom_physics.execute_complete_pipeline(
    particles, inclination=80.0
)
```

### 3. Custom Rendering Techniques

Extend the particle renderer with new visualization methods:

```python
from eventHorizon.visualization.particle_renderer import ParticleRenderer
import matplotlib.pyplot as plt

class CustomRenderer(ParticleRenderer):
    """Extended renderer with custom visualization techniques."""
    
    def render_3d_visualization(
        self, 
        particles_df: pd.DataFrame,
        elevation: float = 30.0,
        azimuth: float = 45.0
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Create 3D visualization of particle system."""
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Calculate 3D positions
        x = particles_df['X']
        y = particles_df['Y']
        z = self._calculate_disk_height(particles_df)
        
        # Color by flux
        colors = particles_df['flux_o']
        
        # Create 3D scatter plot
        scatter = ax.scatter(x, y, z, c=colors, cmap='hot', alpha=0.6)
        
        # Set viewing angle
        ax.view_init(elev=elevation, azim=azimuth)
        
        # Styling
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z (Disk Height)')
        fig.colorbar(scatter, label='Flux')
        
        return fig, ax
    
    def render_velocity_field(
        self, 
        particles_df: pd.DataFrame
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Render velocity field visualization."""
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Calculate velocity vectors
        vx, vy = self._calculate_velocity_vectors(particles_df)
        
        # Create quiver plot
        ax.quiver(
            particles_df['X'], particles_df['Y'], vx, vy,
            particles_df['flux_o'], cmap='plasma', alpha=0.7
        )
        
        # Styling
        ax.set_aspect('equal')
        ax.set_xlim(-40, 40)
        ax.set_ylim(-40, 40)
        
        return fig, ax
    
    def _calculate_disk_height(self, particles_df: pd.DataFrame) -> np.ndarray:
        """Calculate disk scale height for 3D visualization."""
        radii = np.sqrt(particles_df['X']**2 + particles_df['Y']**2)
        
        # Simple scale height model: H/R ∝ (T/T_0)^0.5
        temperatures = particles_df.get('temperature', np.ones_like(radii))
        scale_heights = 0.1 * radii * np.sqrt(temperatures)
        
        # Add random vertical displacement
        z_positions = np.random.normal(0, scale_heights)
        
        return z_positions
    
    def _calculate_velocity_vectors(
        self, 
        particles_df: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate orbital velocity vectors."""
        x, y = particles_df['X'], particles_df['Y']
        radii = np.sqrt(x**2 + y**2)
        
        # Keplerian velocity: v = sqrt(GM/r)
        v_magnitude = np.sqrt(1.0 / radii)  # GM = 1 in geometric units
        
        # Velocity direction (tangential)
        vx = -v_magnitude * y / radii
        vy = v_magnitude * x / radii
        
        return vx, vy

# Usage
custom_renderer = CustomRenderer()
fig_3d, ax_3d = custom_renderer.render_3d_visualization(particles_df)
fig_vel, ax_vel = custom_renderer.render_velocity_field(particles_df)
```

### 4. Custom Mathematical Models

Extend the mathematical foundation with new geodesic calculations:

```python
from eventHorizon.math.geodesics import Geodesics
import numpy as np
from scipy.integrate import solve_ivp

class KerrGeodesics(Geodesics):
    """Extended geodesics for Kerr (spinning) black holes."""
    
    def __init__(self, spin: float = 0.0):
        super().__init__()
        self.spin = spin
    
    def calculate_impact_parameter_kerr(
        self,
        source_radius: float,
        source_angle: float,
        observer_inclination: float,
        black_hole_mass: float,
        **kwargs
    ) -> Optional[float]:
        """Calculate impact parameter for Kerr spacetime."""
        
        if self.spin == 0.0:
            # Fall back to Schwarzschild
            return super().calculate_impact_parameter(
                source_radius, source_angle, observer_inclination, 
                black_hole_mass, **kwargs
            )
        
        # Kerr geodesic calculation
        return self._solve_kerr_geodesic(
            source_radius, source_angle, observer_inclination, 
            black_hole_mass
        )
    
    def _solve_kerr_geodesic(
        self,
        r_source: float,
        theta_source: float,
        inclination: float,
        mass: float
    ) -> Optional[float]:
        """Solve Kerr geodesic equation."""
        
        # Kerr metric parameters
        a = self.spin * mass  # Spin parameter
        
        # Initial conditions
        r0, theta0 = r_source, theta_source
        
        # Conserved quantities (simplified)
        E = 1.0  # Energy at infinity
        L = self._calculate_angular_momentum_kerr(r_source, inclination)
        
        # Carter constant
        Q = self._calculate_carter_constant_kerr(r_source, theta_source, E, L, a)
        
        # Solve geodesic equation
        try:
            solution = self._integrate_kerr_geodesic(r0, theta0, E, L, Q, a, mass)
            
            if solution is not None:
                return solution['impact_parameter']
            
        except Exception:
            pass
        
        return None
    
    def _calculate_angular_momentum_kerr(
        self, 
        radius: float, 
        inclination: float
    ) -> float:
        """Calculate angular momentum for Kerr geodesic."""
        # Simplified calculation
        return radius * np.sin(inclination)
    
    def _calculate_carter_constant_kerr(
        self,
        radius: float,
        theta: float,
        energy: float,
        angular_momentum: float,
        spin: float
    ) -> float:
        """Calculate Carter constant for Kerr spacetime."""
        # Simplified Carter constant
        cos_theta = np.cos(theta)
        return angular_momentum**2 * cos_theta**2
    
    def _integrate_kerr_geodesic(
        self,
        r0: float,
        theta0: float,
        E: float,
        L: float,
        Q: float,
        a: float,
        M: float
    ) -> Optional[Dict[str, Any]]:
        """Integrate Kerr geodesic equations."""
        
        def kerr_geodesic_equations(t, y):
            """Kerr geodesic equations in Boyer-Lindquist coordinates."""
            r, theta, phi, pr, ptheta = y
            
            # Kerr metric functions
            rho2 = r**2 + a**2 * np.cos(theta)**2
            delta = r**2 - 2*M*r + a**2
            
            # Geodesic equations (simplified)
            drdt = pr * delta / rho2
            dthetadt = ptheta / rho2
            dphidt = (a*E + L/np.sin(theta)**2) / rho2
            
            # Momentum equations (simplified)
            dprdt = -(M*(r**2 - a**2) - r*delta) / (rho2 * delta) * pr**2
            dpthetadt = np.sin(theta) * np.cos(theta) * (L**2/np.sin(theta)**4 - a**2*E**2)
            
            return [drdt, dthetadt, dphidt, dprdt, dpthetadt]
        
        # Initial conditions
        y0 = [r0, theta0, 0.0, 0.0, 0.0]  # Simplified initial momenta
        
        # Integration
        try:
            sol = solve_ivp(
                kerr_geodesic_equations,
                [0, 100],  # Integration range
                y0,
                dense_output=True,
                rtol=1e-8
            )
            
            if sol.success:
                # Extract impact parameter from solution
                final_r = sol.y[0][-1]
                impact_param = self._extract_impact_parameter(sol)
                
                return {
                    'impact_parameter': impact_param,
                    'trajectory': sol,
                    'success': True
                }
            
        except Exception:
            pass
        
        return None
    
    def _extract_impact_parameter(self, solution) -> float:
        """Extract impact parameter from geodesic solution."""
        # Simplified extraction
        r_values = solution.y[0]
        phi_values = solution.y[2]
        
        # Impact parameter approximation
        r_min = np.min(r_values)
        return r_min * np.sin(phi_values[-1])

# Usage
kerr_geodesics = KerrGeodesics(spin=0.5)
physics_engine = PhysicsEngine(mass=1.0, spin=0.5)
physics_engine.geodesics = kerr_geodesics
```

## Best Practices

### 1. Code Organization

**Module Structure:**
```python
# Good: Clear module organization
from eventHorizon.core import ParticleSystem, PhysicsEngine
from eventHorizon.visualization import ParticleRenderer
from eventHorizon.config import ModelConfig

# Avoid: Importing everything
from eventHorizon import *
```

**Class Design:**
```python
# Good: Single responsibility principle
class FluxCalculator:
    """Handles only flux calculations."""
    
    def calculate_intrinsic_flux(self, radius: float) -> float:
        pass
    
    def calculate_observed_flux(self, flux: float, redshift: float) -> float:
        pass

# Avoid: Classes that do too much
class EverythingCalculator:
    """Handles flux, geodesics, rendering, and configuration."""
    pass
```

### 2. Performance Optimization

**Vectorization:**
```python
# Good: Vectorized operations
def calculate_fluxes_vectorized(radii: np.ndarray) -> np.ndarray:
    """Calculate fluxes for multiple radii at once."""
    valid_mask = radii > 6.0  # Outside ISCO
    fluxes = np.zeros_like(radii)
    
    if np.any(valid_mask):
        valid_radii = radii[valid_mask]
        fluxes[valid_mask] = flux_formula(valid_radii)
    
    return fluxes

# Avoid: Loop-based calculations
def calculate_fluxes_loop(radii: np.ndarray) -> np.ndarray:
    """Slow loop-based calculation."""
    fluxes = []
    for r in radii:
        fluxes.append(flux_formula(r))
    return np.array(fluxes)
```

**Memory Management:**
```python
# Good: Efficient memory usage
def process_particles_streaming(
    particles: List[Particle], 
    batch_size: int = 1000
) -> List[Particle]:
    """Process particles in batches to manage memory."""
    
    processed = []
    for i in range(0, len(particles), batch_size):
        batch = particles[i:i+batch_size]
        processed_batch = apply_physics_to_batch(batch)
        processed.extend(processed_batch)
        
        # Clear intermediate results
        del batch, processed_batch
    
    return processed

# Avoid: Loading everything into memory
def process_particles_all_at_once(particles: List[Particle]) -> List[Particle]:
    """Memory-intensive processing."""
    # This could cause memory issues with large particle counts
    return [apply_physics(p) for p in particles]
```

### 3. Error Handling

**Robust Error Handling:**
```python
from eventHorizon.utils.validation import validate_physical_parameters

def calculate_impact_parameter_robust(
    radius: float,
    inclination: float,
    **kwargs
) -> Optional[float]:
    """Robust impact parameter calculation with error handling."""
    
    try:
        # Validate inputs
        validate_physical_parameters(radius=radius, inclination=inclination)
        
        # Attempt calculation
        result = calculate_impact_parameter_core(radius, inclination, **kwargs)
        
        # Validate output
        if result is not None and result > 0:
            return result
        else:
            logger.warning(f"Invalid impact parameter result: {result}")
            return None
            
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        return None
    except Exception as e:
        logger.error(f"Calculation failed: {e}")
        return None

# Good: Specific exception handling
def safe_geodesic_calculation(params):
    try:
        return calculate_geodesic(params)
    except NumericalInstabilityError:
        # Try alternative method
        return calculate_geodesic_fallback(params)
    except InvalidParameterError as e:
        logger.warning(f"Invalid parameters: {e}")
        return None

# Avoid: Catching all exceptions
def unsafe_calculation(params):
    try:
        return calculate_geodesic(params)
    except:  # Too broad
        return None
```

### 4. Testing Strategies

**Unit Testing:**
```python
import pytest
import numpy as np
from eventHorizon.core import ParticleSystem

class TestParticleSystem:
    """Comprehensive tests for ParticleSystem."""
    
    def test_particle_generation_count(self):
        """Test that correct number of particles are generated."""
        particle_system = ParticleSystem(particle_count=1000)
        particles = particle_system.generate_particles()
        
        assert len(particles) == 1000
    
    def test_particle_physical_properties(self):
        """Test that particles have valid physical properties."""
        particle_system = ParticleSystem(particle_count=100)
        particles = particle_system.generate_particles()
        
        for particle in particles:
            assert particle.radius > 0
            assert 0 <= particle.angle < 2 * np.pi
            assert particle.temperature >= 0
            assert particle.flux >= 0
    
    def test_luminet_distribution(self):
        """Test Luminet distribution algorithm."""
        particle_system = ParticleSystem(
            particle_count=10000,
            distribution_type='luminet'
        )
        particles = particle_system.generate_particles()
        
        radii = [p.radius for p in particles]
        
        # Test that distribution is biased toward center
        median_radius = np.median(radii)
        mean_radius = np.mean(radii)
        
        # For linear sampling, median should be less than mean
        assert median_radius < mean_radius
    
    @pytest.mark.parametrize("distribution_type", [
        'uniform', 'biased_center', 'luminet'
    ])
    def test_different_distributions(self, distribution_type):
        """Test all distribution types."""
        particle_system = ParticleSystem(
            particle_count=1000,
            distribution_type=distribution_type
        )
        particles = particle_system.generate_particles()
        
        assert len(particles) == 1000
        assert all(p.radius > 0 for p in particles)

# Integration Testing
class TestPhysicsPipeline:
    """Test complete physics pipeline."""
    
    def test_end_to_end_pipeline(self):
        """Test complete particle processing pipeline."""
        # Generate particles
        particle_system = ParticleSystem(particle_count=100)
        particles = particle_system.generate_particles()
        
        # Apply physics
        physics_engine = PhysicsEngine(mass=1.0)
        processed = physics_engine.execute_complete_pipeline(
            particles, inclination=80.0
        )
        
        # Verify results
        assert len(processed) == 100
        assert all(p.redshift_factor > 0 for p in processed if p.is_visible)
        assert any(p.is_visible for p in processed)  # Some particles should be visible
```

**Performance Testing:**
```python
import time
import numpy as np

def benchmark_particle_generation():
    """Benchmark particle generation performance."""
    
    particle_counts = [1000, 5000, 10000, 50000]
    
    for count in particle_counts:
        particle_system = ParticleSystem(particle_count=count)
        
        start_time = time.time()
        particles = particle_system.generate_particles()
        end_time = time.time()
        
        generation_time = end_time - start_time
        particles_per_second = count / generation_time
        
        print(f"Generated {count} particles in {generation_time:.3f}s "
              f"({particles_per_second:.0f} particles/s)")
        
        # Performance assertion
        assert particles_per_second > 1000, f"Performance too slow: {particles_per_second} particles/s"

def benchmark_physics_pipeline():
    """Benchmark complete physics pipeline."""
    
    particle_system = ParticleSystem(particle_count=10000)
    particles = particle_system.generate_particles()
    physics_engine = PhysicsEngine(mass=1.0)
    
    start_time = time.time()
    processed = physics_engine.execute_complete_pipeline(
        particles, inclination=80.0
    )
    end_time = time.time()
    
    processing_time = end_time - start_time
    particles_per_second = len(particles) / processing_time
    
    print(f"Processed {len(particles)} particles in {processing_time:.3f}s "
          f"({particles_per_second:.0f} particles/s)")
    
    # Performance requirement
    assert particles_per_second > 500, "Physics pipeline too slow"
```

## Debugging and Profiling

### 1. Debugging Tools

**Logging Configuration:**
```python
import logging

# Configure logging for development
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eventhorizon_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('eventHorizon')

# Use in code
def calculate_impact_parameter_debug(radius, inclination, **kwargs):
    """Impact parameter calculation with debug logging."""
    
    logger.debug(f"Calculating impact parameter for r={radius}, i={inclination}")
    
    try:
        result = calculate_impact_parameter_core(radius, inclination, **kwargs)
        logger.debug(f"Impact parameter result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Impact parameter calculation failed: {e}", exc_info=True)
        raise
```

**Visualization Debugging:**
```python
def debug_particle_distribution(particles: List[Particle]):
    """Create debug plots for particle distribution."""
    
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Radial distribution
    radii = [p.radius for p in particles]
    axes[0, 0].hist(radii, bins=50, alpha=0.7)
    axes[0, 0].set_title('Radial Distribution')
    axes[0, 0].set_xlabel('Radius')
    
    # Angular distribution
    angles = [p.angle for p in particles]
    axes[0, 1].hist(angles, bins=50, alpha=0.7)
    axes[0, 1].set_title('Angular Distribution')
    axes[0, 1].set_xlabel('Angle')
    
    # Temperature vs radius
    temperatures = [p.temperature for p in particles]
    axes[1, 0].scatter(radii, temperatures, alpha=0.5)
    axes[1, 0].set_title('Temperature vs Radius')
    axes[1, 0].set_xlabel('Radius')
    axes[1, 0].set_ylabel('Temperature')
    
    # Flux vs radius
    fluxes = [p.flux for p in particles]
    axes[1, 1].scatter(radii, fluxes, alpha=0.5)
    axes[1, 1].set_title('Flux vs Radius')
    axes[1, 1].set_xlabel('Radius')
    axes[1, 1].set_ylabel('Flux')
    
    plt.tight_layout()
    plt.savefig('particle_debug.png', dpi=150)
    plt.show()

def debug_geodesic_calculation(
    radius: float, 
    inclination: float, 
    impact_parameter: float
):
    """Debug geodesic calculation with detailed output."""
    
    print(f"Debugging geodesic calculation:")
    print(f"  Source radius: {radius}")
    print(f"  Inclination: {inclination}")
    print(f"  Impact parameter: {impact_parameter}")
    
    # Check physical constraints
    photon_sphere = 3.0 * 1.0  # Assuming M=1
    if impact_parameter < photon_sphere * np.sqrt(27):
        print(f"  WARNING: Impact parameter {impact_parameter} may be inside photon sphere")
    
    # Check ISCO
    isco_radius = 6.0 * 1.0  # Assuming M=1
    if radius < isco_radius:
        print(f"  WARNING: Source radius {radius} is inside ISCO")
    
    # Perform calculation with intermediate steps
    try:
        # Add detailed calculation steps here
        result = perform_geodesic_calculation_with_steps(
            radius, inclination, impact_parameter
        )
        print(f"  Result: {result}")
        return result
        
    except Exception as e:
        print(f"  ERROR: {e}")
        raise
```

### 2. Performance Profiling

**CPU Profiling:**
```python
import cProfile
import pstats
from pstats import SortKey

def profile_particle_generation():
    """Profile particle generation performance."""
    
    def run_generation():
        particle_system = ParticleSystem(particle_count=10000)
        particles = particle_system.generate_particles()
        return particles
    
    # Run profiler
    profiler = cProfile.Profile()
    profiler.enable()
    
    particles = run_generation()
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(20)  # Top 20 functions
    
    return particles

def profile_physics_pipeline():
    """Profile complete physics pipeline."""
    
    # Setup
    particle_system = ParticleSystem(particle_count=5000)
    particles = particle_system.generate_particles()
    physics_engine = PhysicsEngine(mass=1.0)
    
    def run_pipeline():
        return physics_engine.execute_complete_pipeline(
            particles, inclination=80.0
        )
    
    # Profile
    profiler = cProfile.Profile()
    profiler.enable()
    
    processed = run_pipeline()
    
    profiler.disable()
    
    # Save detailed results
    stats = pstats.Stats(profiler)
    stats.dump_stats('physics_pipeline_profile.prof')
    
    # Print summary
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(30)
    
    return processed
```

**Memory Profiling:**
```python
from memory_profiler import profile
import psutil
import os

@profile
def memory_intensive_calculation():
    """Function decorated for memory profiling."""
    
    particle_system = ParticleSystem(particle_count=50000)
    particles = particle_system.generate_particles()
    
    physics_engine = PhysicsEngine(mass=1.0)
    processed = physics_engine.execute_complete_pipeline(
        particles, inclination=80.0
    )
    
    return processed

def monitor_memory_usage():
    """Monitor memory usage during calculation."""
    
    process = psutil.Process(os.getpid())
    
    print(f"Initial memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    
    # Generate particles
    particle_system = ParticleSystem(particle_count=20000)
    particles = particle_system.generate_particles()
    
    print(f"After particle generation: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    
    # Apply physics
    physics_engine = PhysicsEngine(mass=1.0)
    processed = physics_engine.execute_complete_pipeline(
        particles, inclination=80.0
    )
    
    print(f"After physics pipeline: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    
    # Clean up
    del particles, processed
    
    print(f"After cleanup: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

## Contributing Guidelines

### 1. Code Style

Follow PEP 8 with these specific guidelines:

```python
# Good: Clear variable names
particle_count = 10000
observer_inclination = 80.0
black_hole_mass = 1.0

# Avoid: Abbreviated names
n = 10000
inc = 80.0
m = 1.0

# Good: Descriptive function names
def calculate_impact_parameter_for_geodesic(radius, inclination):
    pass

# Avoid: Unclear function names
def calc_b(r, i):
    pass

# Good: Type hints
def process_particles(
    particles: List[Particle], 
    inclination: float
) -> List[Particle]:
    pass

# Good: Docstrings
def calculate_flux(radius: float, accretion_rate: float) -> float:
    """
    Calculate intrinsic flux using Shakura-Sunyaev disk model.
    
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
    pass
```

### 2. Documentation Standards

**Module Documentation:**
```python
"""
Module for advanced particle rendering techniques.

This module provides high-performance rendering capabilities for Luminet-style
black hole visualization, including tricontourf plotting, power scaling,
and ghost image composition.

Classes
-------
ParticleRenderer : Main rendering class
RenderConfig : Configuration for rendering parameters

Functions
---------
create_luminet_visualization : High-level visualization function

Examples
--------
>>> from eventHorizon.visualization import ParticleRenderer, RenderConfig
>>> config = RenderConfig(power_scale=0.9, levels=100)
>>> renderer = ParticleRenderer(config)
>>> fig, ax = renderer.render_frame(particles_df)
"""
```

**Class Documentation:**
```python
class ParticleSystem:
    """
    Manages discrete representation of matter in the accretion disk.
    
    This class provides the foundation for particle-based black hole
    visualization by generating and managing particles that represent
    matter in the accretion disk around a black hole.
    
    Parameters
    ----------
    black_hole_mass : float, default=1.0
        Black hole mass in geometric units
    particle_count : int, default=10000
        Number of particles to generate
    distribution_type : str, default='biased_center'
        Type of particle distribution ('uniform', 'biased_center', 'luminet', 'custom')
    
    Attributes
    ----------
    particles : List[Particle]
        List of generated particles
    config : Dict[str, Any]
        Configuration parameters
    
    Examples
    --------
    >>> particle_system = ParticleSystem(particle_count=5000)
    >>> particles = particle_system.generate_particles()
    >>> len(particles)
    5000
    """
```

### 3. Testing Requirements

All new code must include:

1. **Unit tests** with >90% coverage
2. **Integration tests** for pipeline components
3. **Performance benchmarks** for computationally intensive functions
4. **Validation tests** against reference implementations

### 4. Pull Request Process

1. **Fork and Branch**: Create feature branch from main
2. **Implement**: Follow coding standards and include tests
3. **Test**: Run full test suite and benchmarks
4. **Document**: Update documentation and examples
5. **Review**: Submit pull request with detailed description

This comprehensive developer guide provides the foundation for extending and contributing to the EventHorizon particle-based black hole visualization system while maintaining code quality, performance, and scientific accuracy.