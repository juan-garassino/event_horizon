# Troubleshooting Guide

This comprehensive guide helps you diagnose and solve common issues when creating black hole visualizations with EventHorizon.

## Common Issues and Solutions

### 1. Visualization Problems

#### Issue: Visualization is completely black or empty

**Symptoms:**
- No visible particles in the output
- Completely black image
- Empty plot area

**Diagnosis:**
```python
from eventHorizon import ParticleSystem, PhysicsEngine

# Debug particle generation
particle_system = ParticleSystem(particle_count=1000)
particles = particle_system.generate_particles()

print(f"Generated particles: {len(particles)}")
print(f"Sample particle: radius={particles[0].radius}, flux={particles[0].flux}")

# Debug physics processing
physics_engine = PhysicsEngine(mass=1.0)
processed = physics_engine.execute_complete_pipeline(particles, inclination=80.0)

visible_particles = [p for p in processed if p.is_visible]
print(f"Visible particles: {len(visible_particles)}")

if not visible_particles:
    print("PROBLEM: No visible particles after physics processing")
```

**Solutions:**

1. **Check inclination angle:**
```python
# Problem: Inclination too low (face-on view)
fig, ax = draw_blackhole(inclination=30.0)  # May show few particles

# Solution: Use higher inclination for better lensing
fig, ax = draw_blackhole(inclination=80.0)  # Optimal for Luminet effect
```

2. **Verify particle count:**
```python
# Problem: Too few particles
fig, ax = draw_blackhole(particle_count=100)  # Too sparse

# Solution: Increase particle count
fig, ax = draw_blackhole(particle_count=10000)  # Better coverage
```

3. **Check power scaling:**
```python
# Problem: Power scale too low (image too dim)
fig, ax = draw_blackhole(power_scale=0.3)  # Too dim

# Solution: Increase power scale
fig, ax = draw_blackhole(power_scale=0.9)  # Better contrast
```

#### Issue: Visualization is too dark or dim

**Symptoms:**
- Particles barely visible
- Low contrast
- Difficult to see disk structure

**Solutions:**

1. **Increase power scaling:**
```python
# Gradually increase power scale
power_scales = [0.5, 0.7, 0.9, 0.95]

for power in power_scales:
    fig, ax = draw_blackhole(power_scale=power, inclination=80.0)
    plt.title(f'Power Scale: {power}')
    plt.show()
```

2. **Adjust flux normalization:**
```python
from eventHorizon import ParticleSystem, PhysicsEngine

# Manual flux adjustment
particle_system = ParticleSystem(particle_count=10000)
particles = particle_system.generate_particles()

# Check flux range
fluxes = [p.flux for p in particles]
print(f"Flux range: {min(fluxes):.2e} - {max(fluxes):.2e}")

# If flux range is too small, check disk parameters
if max(fluxes) / min([f for f in fluxes if f > 0]) < 100:
    print("WARNING: Low flux dynamic range")
    print("Solution: Check disk inner/outer radius settings")
```

3. **Verify matplotlib colormap:**
```python
# Ensure proper colormap for black hole visualization
import matplotlib.pyplot as plt

# Good colormaps for black hole visualization
colormaps = ['Greys_r', 'hot', 'plasma', 'inferno']

for cmap in colormaps:
    # Test with different colormaps
    # (Implementation depends on your rendering setup)
    print(f"Testing colormap: {cmap}")
```

#### Issue: Missing ghost images

**Symptoms:**
- Only direct image visible
- No secondary lensed images
- Asymmetric appearance

**Diagnosis:**
```python
# Check for ghost image particles
processed_particles = physics_engine.execute_complete_pipeline(
    particles, inclination=80.0
)

direct_particles = [p for p in processed_particles if p.image_order == 0 and p.is_visible]
ghost_particles = [p for p in processed_particles if p.image_order == 1 and p.is_visible]

print(f"Direct image particles: {len(direct_particles)}")
print(f"Ghost image particles: {len(ghost_particles)}")

if len(ghost_particles) == 0:
    print("PROBLEM: No ghost images generated")
```

**Solutions:**

1. **Increase inclination angle:**
```python
# Ghost images are more prominent at higher inclinations
fig, ax = draw_blackhole(
    inclination=85.0,  # Higher inclination
    enable_ghost_images=True
)
```

2. **Check ghost image calculation:**
```python
# Ensure ghost images are enabled in physics engine
physics_engine = PhysicsEngine(mass=1.0)

# Manual ghost image processing
for particle in particles:
    # Check if impact parameter calculation includes ghost images
    impact_param_direct = physics_engine.calc_impact_parameter(
        particle.radius, np.radians(80.0), particle.angle, image_order=0
    )
    impact_param_ghost = physics_engine.calc_impact_parameter(
        particle.radius, np.radians(80.0), particle.angle, image_order=1
    )
    
    if impact_param_direct and not impact_param_ghost:
        print("Ghost image calculation may have issues")
        break
```

3. **Verify rendering includes ghost images:**
```python
# Ensure renderer processes both direct and ghost images
from eventHorizon import ParticleRenderer

renderer = ParticleRenderer()

# Check that both particle sets are passed to renderer
fig, ax = renderer.render_frame(
    direct_particles_df,
    ghost_particles_df  # Make sure this is not None
)
```

### 2. Performance Issues

#### Issue: Calculations are too slow

**Symptoms:**
- Long wait times for particle generation
- Slow physics processing
- Rendering takes too long

**Diagnosis:**
```python
import time

# Benchmark different components
def benchmark_components():
    # Particle generation
    start = time.time()
    particle_system = ParticleSystem(particle_count=10000)
    particles = particle_system.generate_particles()
    generation_time = time.time() - start
    
    # Physics processing
    start = time.time()
    physics_engine = PhysicsEngine(mass=1.0)
    processed = physics_engine.execute_complete_pipeline(particles, inclination=80.0)
    physics_time = time.time() - start
    
    # Rendering (simplified timing)
    start = time.time()
    # Rendering code here
    rendering_time = time.time() - start
    
    print(f"Particle generation: {generation_time:.2f}s")
    print(f"Physics processing: {physics_time:.2f}s")
    print(f"Rendering: {rendering_time:.2f}s")
    
    return generation_time, physics_time, rendering_time

benchmark_components()
```

**Solutions:**

1. **Reduce particle count for testing:**
```python
# Use fewer particles during development
fig, ax = draw_blackhole(
    particle_count=5000,  # Reduced from 20000
    quality='draft'       # Faster rendering
)
```

2. **Use quality presets:**
```python
# Quality presets optimize performance automatically
qualities = ['draft', 'standard', 'high']

for quality in qualities:
    start = time.time()
    fig, ax = draw_blackhole(quality=quality)
    end = time.time()
    print(f"{quality}: {end-start:.2f}s")
```

3. **Optimize physics calculations:**
```python
# Reduce precision for faster calculations
physics_engine = PhysicsEngine(mass=1.0)
physics_engine.solver_tolerance = 1e-6  # Reduced from 1e-10
physics_engine.integration_steps = 500  # Reduced from 2000
```

4. **Profile performance bottlenecks:**
```python
import cProfile

def profile_visualization():
    """Profile the complete visualization process."""
    
    def create_visualization():
        return draw_blackhole(
            particle_count=10000,
            inclination=80.0,
            quality='standard'
        )
    
    # Run profiler
    profiler = cProfile.Profile()
    profiler.enable()
    
    fig, ax = create_visualization()
    
    profiler.disable()
    
    # Print top time consumers
    import pstats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

profile_visualization()
```

#### Issue: Memory usage too high

**Symptoms:**
- System runs out of memory
- Slow performance due to swapping
- Python process killed

**Diagnosis:**
```python
import psutil
import os

def monitor_memory():
    """Monitor memory usage during visualization."""
    
    process = psutil.Process(os.getpid())
    
    print(f"Initial memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    
    # Generate particles
    particle_system = ParticleSystem(particle_count=50000)  # Large count
    particles = particle_system.generate_particles()
    
    print(f"After particles: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    
    # Process physics
    physics_engine = PhysicsEngine(mass=1.0)
    processed = physics_engine.execute_complete_pipeline(particles, inclination=80.0)
    
    print(f"After physics: {process.memory_info().rss / 1024 / 1024:.1f} MB")

monitor_memory()
```

**Solutions:**

1. **Process particles in batches:**
```python
def process_particles_in_batches(particles, batch_size=5000):
    """Process particles in smaller batches to manage memory."""
    
    physics_engine = PhysicsEngine(mass=1.0)
    all_processed = []
    
    for i in range(0, len(particles), batch_size):
        batch = particles[i:i+batch_size]
        
        processed_batch = physics_engine.execute_complete_pipeline(
            batch, inclination=80.0
        )
        
        all_processed.extend(processed_batch)
        
        # Clear intermediate results
        del batch, processed_batch
    
    return all_processed

# Use batch processing for large particle counts
large_particles = ParticleSystem(particle_count=50000).generate_particles()
processed = process_particles_in_batches(large_particles)
```

2. **Use memory-efficient data structures:**
```python
# Use numpy arrays instead of lists where possible
import numpy as np

def create_efficient_particle_arrays(particles):
    """Convert particles to memory-efficient arrays."""
    
    n_particles = len(particles)
    
    # Create structured arrays
    particle_data = np.zeros(n_particles, dtype=[
        ('radius', 'f4'),
        ('angle', 'f4'),
        ('flux', 'f4'),
        ('temperature', 'f4'),
        ('observed_x', 'f4'),
        ('observed_y', 'f4'),
        ('is_visible', 'bool')
    ])
    
    for i, p in enumerate(particles):
        particle_data[i] = (
            p.radius, p.angle, p.flux, p.temperature,
            p.observed_x, p.observed_y, p.is_visible
        )
    
    return particle_data

# Convert to efficient format
efficient_data = create_efficient_particle_arrays(particles)
print(f"Memory usage reduced by ~{100 * (1 - efficient_data.nbytes / (len(particles) * 200)):.0f}%")
```

### 3. Scientific Accuracy Issues

#### Issue: Results don't match reference implementations

**Symptoms:**
- Different appearance from expected Luminet visualization
- Incorrect flux distributions
- Wrong lensing effects

**Diagnosis:**
```python
def validate_against_reference():
    """Validate results against known reference values."""
    
    # Test with known parameters from Luminet 1979
    particle_system = ParticleSystem(
        particle_count=10000,
        distribution_type='luminet'  # Use exact Luminet algorithm
    )
    
    particles = particle_system.generate_particles()
    
    # Check particle distribution
    radii = [p.radius for p in particles]
    
    # Luminet uses linear radius sampling
    # Check if distribution is biased toward center
    median_radius = np.median(radii)
    mean_radius = np.mean(radii)
    
    print(f"Median radius: {median_radius:.2f}")
    print(f"Mean radius: {mean_radius:.2f}")
    
    if median_radius >= mean_radius:
        print("WARNING: Distribution may not match Luminet algorithm")
        print("Expected: median < mean for linear radius sampling")
    
    # Check flux calculations
    physics_engine = PhysicsEngine(mass=1.0)
    
    # Test flux at known radius
    test_radius = 10.0  # 10 M
    flux_intrinsic = physics_engine.flux_intrinsic(test_radius, 1.0)
    
    # Compare with analytical expectation
    # (This would require reference values from literature)
    print(f"Flux at r=10M: {flux_intrinsic:.2e}")

validate_against_reference()
```

**Solutions:**

1. **Use exact Luminet algorithms:**
```python
# Ensure using Luminet distribution
particle_system = ParticleSystem(
    distribution_type='luminet',  # Not 'uniform' or 'biased_center'
    bias_toward_center=True
)

# Use Luminet physics formulas
physics_engine = PhysicsEngine(mass=1.0)
# Verify that flux_intrinsic uses exact Luminet formula
```

2. **Validate individual components:**
```python
def test_flux_formula():
    """Test flux formula against known values."""
    
    physics_engine = PhysicsEngine(mass=1.0)
    
    # Test at ISCO (should be finite)
    flux_isco = physics_engine.flux_intrinsic(6.0, 1.0)
    print(f"Flux at ISCO: {flux_isco}")
    
    # Test inside ISCO (should be zero)
    flux_inside = physics_engine.flux_intrinsic(5.0, 1.0)
    print(f"Flux inside ISCO: {flux_inside}")
    
    if flux_inside != 0.0:
        print("ERROR: Flux should be zero inside ISCO")
    
    # Test flux scaling with radius
    radii = [10, 20, 30, 40]
    fluxes = [physics_engine.flux_intrinsic(r, 1.0) for r in radii]
    
    print("Flux vs radius:")
    for r, f in zip(radii, fluxes):
        print(f"  r={r}: flux={f:.2e}")

test_flux_formula()
```

3. **Check coordinate transformations:**
```python
def test_coordinate_transformations():
    """Test coordinate transformation accuracy."""
    
    # Test simple case: face-on disk
    physics_engine = PhysicsEngine(mass=1.0)
    
    # Particle at radius 20, angle 0
    test_radius = 20.0
    test_angle = 0.0
    inclination = 0.0  # Face-on
    
    impact_param = physics_engine.calc_impact_parameter(
        test_radius, np.radians(inclination), test_angle
    )
    
    print(f"Impact parameter for face-on view: {impact_param}")
    
    # For face-on view, impact parameter should approximately equal radius
    if abs(impact_param - test_radius) > 1.0:
        print("WARNING: Coordinate transformation may be incorrect")

test_coordinate_transformations()
```

### 4. Installation and Import Issues

#### Issue: Import errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'eventHorizon'`
- Import errors for specific components

**Solutions:**

1. **Check installation:**
```bash
# Verify EventHorizon is installed
pip list | grep eventhorizon

# If not installed, install from source
cd /path/to/eventhorizon
pip install -e .
```

2. **Check Python path:**
```python
import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")

# Add EventHorizon path if needed
sys.path.append('/path/to/eventhorizon')
```

3. **Test individual imports:**
```python
# Test imports one by one
try:
    from eventHorizon.core import ParticleSystem
    print("✓ ParticleSystem import successful")
except ImportError as e:
    print(f"✗ ParticleSystem import failed: {e}")

try:
    from eventHorizon.core import PhysicsEngine
    print("✓ PhysicsEngine import successful")
except ImportError as e:
    print(f"✗ PhysicsEngine import failed: {e}")

try:
    from eventHorizon.visualization import ParticleRenderer
    print("✓ ParticleRenderer import successful")
except ImportError as e:
    print(f"✗ ParticleRenderer import failed: {e}")
```

#### Issue: Dependency problems

**Symptoms:**
- Errors related to numpy, scipy, matplotlib
- Version compatibility issues

**Solutions:**

1. **Check dependencies:**
```python
import numpy as np
import scipy
import matplotlib
import pandas as pd

print(f"NumPy version: {np.__version__}")
print(f"SciPy version: {scipy.__version__}")
print(f"Matplotlib version: {matplotlib.__version__}")
print(f"Pandas version: {pd.__version__}")

# Check for minimum required versions
required_versions = {
    'numpy': '1.18.0',
    'scipy': '1.5.0',
    'matplotlib': '3.2.0',
    'pandas': '1.0.0'
}

# Version checking code would go here
```

2. **Update dependencies:**
```bash
# Update all dependencies
pip install --upgrade numpy scipy matplotlib pandas

# Or install specific versions
pip install numpy>=1.18.0 scipy>=1.5.0 matplotlib>=3.2.0 pandas>=1.0.0
```

### 5. Rendering Issues

#### Issue: Matplotlib rendering problems

**Symptoms:**
- Blank plots
- Incorrect colors
- Missing elements

**Solutions:**

1. **Check matplotlib backend:**
```python
import matplotlib
print(f"Matplotlib backend: {matplotlib.get_backend()}")

# Try different backends if having issues
backends = ['TkAgg', 'Qt5Agg', 'Agg']

for backend in backends:
    try:
        matplotlib.use(backend)
        print(f"Successfully set backend to {backend}")
        break
    except:
        continue
```

2. **Test basic plotting:**
```python
import matplotlib.pyplot as plt
import numpy as np

# Test basic matplotlib functionality
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y)
plt.title("Test Plot")
plt.show()

# If this doesn't work, matplotlib installation has issues
```

3. **Check display settings:**
```python
# For Jupyter notebooks
%matplotlib inline

# For interactive use
plt.ion()  # Turn on interactive mode

# For saving files without display
plt.ioff()  # Turn off interactive mode
```

### 6. Debugging Tools

#### Comprehensive Diagnostic Function

```python
def run_comprehensive_diagnostics():
    """Run complete diagnostic suite for EventHorizon."""
    
    print("EVENTHORIZON DIAGNOSTIC SUITE")
    print("=" * 40)
    
    # 1. Import tests
    print("\n1. IMPORT TESTS:")
    try:
        from eventHorizon import draw_blackhole
        print("✓ Main function import successful")
    except Exception as e:
        print(f"✗ Main function import failed: {e}")
        return
    
    try:
        from eventHorizon.core import ParticleSystem, PhysicsEngine
        from eventHorizon.visualization import ParticleRenderer
        print("✓ Core components import successful")
    except Exception as e:
        print(f"✗ Core components import failed: {e}")
    
    # 2. Basic functionality test
    print("\n2. BASIC FUNCTIONALITY TEST:")
    try:
        fig, ax = draw_blackhole(
            particle_count=1000,
            inclination=80.0,
            quality='draft'
        )
        print("✓ Basic visualization successful")
        plt.close(fig)
    except Exception as e:
        print(f"✗ Basic visualization failed: {e}")
    
    # 3. Component tests
    print("\n3. COMPONENT TESTS:")
    
    # Particle system
    try:
        ps = ParticleSystem(particle_count=100)
        particles = ps.generate_particles()
        print(f"✓ Particle system: {len(particles)} particles generated")
    except Exception as e:
        print(f"✗ Particle system failed: {e}")
    
    # Physics engine
    try:
        pe = PhysicsEngine(mass=1.0)
        processed = pe.execute_complete_pipeline(particles, inclination=80.0)
        visible = [p for p in processed if p.is_visible]
        print(f"✓ Physics engine: {len(visible)} visible particles")
    except Exception as e:
        print(f"✗ Physics engine failed: {e}")
    
    # 4. Performance test
    print("\n4. PERFORMANCE TEST:")
    try:
        import time
        start = time.time()
        fig, ax = draw_blackhole(particle_count=5000, quality='draft')
        end = time.time()
        print(f"✓ Performance: {end-start:.2f}s for 5000 particles")
        plt.close(fig)
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
    
    print("\n" + "=" * 40)
    print("DIAGNOSTIC COMPLETE")

# Run diagnostics
run_comprehensive_diagnostics()
```

#### Debug Mode Visualization

```python
def create_debug_visualization():
    """Create visualization with debug information."""
    
    # Enable debug mode
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create visualization with detailed output
    particle_system = ParticleSystem(particle_count=1000)
    particles = particle_system.generate_particles()
    
    print(f"DEBUG: Generated {len(particles)} particles")
    
    physics_engine = PhysicsEngine(mass=1.0)
    processed = physics_engine.execute_complete_pipeline(
        particles, inclination=80.0
    )
    
    # Analyze results
    visible = [p for p in processed if p.is_visible]
    direct = [p for p in visible if p.image_order == 0]
    ghost = [p for p in visible if p.image_order == 1]
    
    print(f"DEBUG: Visible particles: {len(visible)}")
    print(f"DEBUG: Direct image: {len(direct)}")
    print(f"DEBUG: Ghost image: {len(ghost)}")
    
    if len(visible) == 0:
        print("DEBUG: No visible particles - check inclination and physics")
    
    if len(ghost) == 0:
        print("DEBUG: No ghost images - try higher inclination")
    
    # Create visualization with debug info
    fig, ax = draw_blackhole(
        particle_count=1000,
        inclination=80.0,
        quality='draft'
    )
    
    # Add debug annotations
    ax.text(0.02, 0.98, f"Particles: {len(visible)}", 
            transform=ax.transAxes, color='white', fontsize=10)
    ax.text(0.02, 0.94, f"Direct: {len(direct)}", 
            transform=ax.transAxes, color='white', fontsize=10)
    ax.text(0.02, 0.90, f"Ghost: {len(ghost)}", 
            transform=ax.transAxes, color='white', fontsize=10)
    
    return fig, ax

# Create debug visualization
debug_fig, debug_ax = create_debug_visualization()
plt.show()
```

## Getting Help

If you're still experiencing issues after trying these solutions:

1. **Check the [API Reference](../technical/api_reference.md)** for detailed parameter information
2. **Review the [Examples](../../examples/)** directory for working code
3. **Consult the [Developer Guide](../technical/developer_guide.md)** for advanced troubleshooting
4. **Run the comprehensive diagnostics** provided above
5. **Check system requirements** and dependency versions

## Prevention Tips

To avoid common issues:

1. **Start with small particle counts** during development
2. **Use quality presets** instead of manual parameter tuning
3. **Test individual components** before creating complex visualizations
4. **Monitor memory usage** with large particle counts
5. **Validate physics parameters** against known constraints
6. **Keep dependencies updated** but test compatibility

Remember: Most issues are related to parameter choices rather than bugs in the code. Start with the default parameters and modify them gradually to understand their effects.