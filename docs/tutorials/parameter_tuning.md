# Parameter Tuning Guide

Master the art of creating stunning black hole visualizations by understanding how each parameter affects the final result. This guide provides comprehensive coverage of all tunable parameters and their effects.

## Core Parameters

### 1. Black Hole Mass

The black hole mass affects the strength of gravitational effects and the scale of the visualization.

```python
from eventHorizon import draw_blackhole
import matplotlib.pyplot as plt

# Compare different black hole masses
masses = [0.5, 1.0, 2.0, 5.0]
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

for i, mass in enumerate(masses):
    row, col = i // 2, i % 2
    
    temp_fig, temp_ax = draw_blackhole(
        mass=mass,
        inclination=80.0,
        particle_count=8000,
        quality='standard'
    )
    
    axes[row, col].set_title(f'Mass = {mass} M☉')
    # Implementation note: Copy visualization to subplot
    
plt.tight_layout()
plt.show()
```

**Effects of Mass:**
- **Larger mass**: Stronger gravitational lensing, larger apparent size
- **Smaller mass**: Weaker lensing effects, more compact appearance
- **Recommended range**: 0.5 - 10.0 (in geometric units)

### 2. Observer Inclination

The inclination angle dramatically changes the appearance of the black hole and accretion disk.

```python
# Systematic inclination study
inclinations = [30, 45, 60, 75, 85, 90]
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

for i, inc in enumerate(inclinations):
    row, col = i // 3, i % 3
    
    temp_fig, temp_ax = draw_blackhole(
        inclination=inc,
        particle_count=10000,
        quality='standard',
        power_scale=0.9
    )
    
    axes[row, col].set_title(f'Inclination = {inc}°')

plt.tight_layout()
plt.show()
```

**Inclination Effects:**

- **0° (face-on)**: Symmetric disk, minimal lensing distortion
- **30-45°**: Slight asymmetry, beginning of lensing effects
- **60-75°**: Strong asymmetry, clear bright and dim sides
- **80-85°**: **Optimal for Luminet effect**, maximum lensing distortion
- **90° (edge-on)**: Disk appears as thin line, extreme lensing

**Recommended Values:**
- **Scientific accuracy**: 80-85° (matches Luminet's original work)
- **Aesthetic appeal**: 75-85°
- **Educational purposes**: 60-90° range for comparison

### 3. Particle Count

Controls the resolution and detail level of the visualization.

```python
# Compare different particle counts
particle_counts = [2000, 5000, 10000, 20000]
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

import time

for i, count in enumerate(particle_counts):
    row, col = i // 2, i % 2
    
    start_time = time.time()
    temp_fig, temp_ax = draw_blackhole(
        particle_count=count,
        inclination=80.0,
        quality='standard'
    )
    end_time = time.time()
    
    axes[row, col].set_title(f'{count} particles ({end_time-start_time:.1f}s)')

plt.tight_layout()
plt.show()
```

**Particle Count Guidelines:**

| Use Case | Particle Count | Calculation Time | Quality |
|----------|----------------|------------------|---------|
| Quick preview | 2,000-5,000 | < 10 seconds | Draft |
| Interactive work | 8,000-12,000 | 10-30 seconds | Good |
| Presentations | 15,000-25,000 | 30-60 seconds | High |
| Publications | 25,000-50,000 | 1-5 minutes | Excellent |

### 4. Power Scale

Controls contrast and visibility of faint features.

```python
# Power scale comparison
power_scales = [0.5, 0.7, 0.9, 0.98]
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

for i, power in enumerate(power_scales):
    row, col = i // 2, i % 2
    
    temp_fig, temp_ax = draw_blackhole(
        power_scale=power,
        inclination=80.0,
        particle_count=10000
    )
    
    axes[row, col].set_title(f'Power Scale = {power}')

plt.tight_layout()
plt.show()
```

**Power Scale Effects:**
- **0.5-0.7**: Low contrast, smooth gradients, faint features visible
- **0.8-0.9**: **Optimal balance**, good contrast with detail preservation
- **0.95-0.98**: High contrast, sharp features, may lose subtle details
- **> 0.98**: Very high contrast, risk of over-enhancement

## Advanced Parameters

### 5. Accretion Rate

Controls the overall brightness and flux distribution.

```python
from eventHorizon import ParticleSystem, PhysicsEngine

# Compare different accretion rates
accretion_rates = [0.1, 0.5, 1.0, 2.0]

for rate in accretion_rates:
    # Manual pipeline for accretion rate control
    particle_system = ParticleSystem(particle_count=10000)
    particles = particle_system.generate_particles()
    
    physics_engine = PhysicsEngine(mass=1.0)
    processed = physics_engine.execute_complete_pipeline(
        particles,
        inclination=80.0,
        accretion_rate=rate
    )
    
    # Count visible particles and average flux
    visible = [p for p in processed if p.is_visible]
    avg_flux = sum(p.flux for p in visible) / len(visible) if visible else 0
    
    print(f"Accretion rate {rate}: {len(visible)} visible particles, avg flux = {avg_flux:.3f}")
```

### 6. Disk Geometry

Control the inner and outer radii of the accretion disk.

```python
# Different disk configurations
disk_configs = [
    {'inner': 6.0, 'outer': 30.0, 'name': 'Compact'},
    {'inner': 6.0, 'outer': 50.0, 'name': 'Standard'},
    {'inner': 6.0, 'outer': 100.0, 'name': 'Extended'},
    {'inner': 10.0, 'outer': 50.0, 'name': 'Truncated Inner'}
]

fig, axes = plt.subplots(2, 2, figsize=(12, 12))

for i, config in enumerate(disk_configs):
    row, col = i // 2, i % 2
    
    particle_system = ParticleSystem(
        particle_count=10000,
        inner_radius=config['inner'],
        outer_radius=config['outer']
    )
    
    particles = particle_system.generate_particles()
    physics_engine = PhysicsEngine(mass=1.0)
    processed = physics_engine.execute_complete_pipeline(
        particles, inclination=80.0
    )
    
    axes[row, col].set_title(f"{config['name']}: {config['inner']}-{config['outer']} M")
    # Render processed particles
```

### 7. Distribution Types

Compare different particle sampling strategies.

```python
# Compare distribution types
distributions = ['uniform', 'biased_center', 'luminet']
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for i, dist_type in enumerate(distributions):
    particle_system = ParticleSystem(
        particle_count=10000,
        distribution_type=dist_type
    )
    
    particles = particle_system.generate_particles()
    
    # Analyze radial distribution
    radii = [p.radius for p in particles]
    
    axes[i].hist(radii, bins=50, alpha=0.7, density=True)
    axes[i].set_title(f'{dist_type.title()} Distribution')
    axes[i].set_xlabel('Radius')
    axes[i].set_ylabel('Density')

plt.tight_layout()
plt.show()
```

**Distribution Characteristics:**
- **Uniform**: Even sampling across disk area, good for general studies
- **Biased Center**: More particles near center, better for inner disk physics
- **Luminet**: Exact algorithm from reference, optimal for authentic reproduction

## Quality Optimization

### Quality Presets

```python
# Compare quality presets
qualities = ['draft', 'standard', 'high', 'publication']

for quality in qualities:
    start_time = time.time()
    
    fig, ax = draw_blackhole(
        inclination=80.0,
        quality=quality
    )
    
    end_time = time.time()
    
    print(f"{quality.capitalize()} quality: {end_time-start_time:.1f} seconds")
    
    # Save with appropriate DPI
    dpi_map = {'draft': 150, 'standard': 300, 'high': 600, 'publication': 1200}
    plt.savefig(f'black_hole_{quality}.png', dpi=dpi_map[quality], bbox_inches='tight')
    plt.close()
```

### Custom Quality Configuration

```python
from eventHorizon.config import RenderConfig

# Create custom quality configuration
custom_config = RenderConfig(
    power_scale=0.92,
    levels=150,  # Contour levels
    quality_level='custom',
    anti_aliasing=True,
    background_color='black'
)

from eventHorizon import ParticleRenderer

renderer = ParticleRenderer(custom_config)
# Use with particle data...
```

## Parameter Optimization Workflows

### 1. Scientific Accuracy Workflow

For reproducing Luminet's results:

```python
def create_luminet_accurate_visualization():
    """Create scientifically accurate Luminet reproduction."""
    
    return draw_blackhole(
        mass=1.0,                    # Standard black hole
        inclination=80.0,            # Luminet's viewing angle
        particle_count=15000,        # Good resolution
        distribution_type='luminet', # Exact algorithm
        power_scale=0.9,            # Luminet's contrast
        enable_ghost_images=True,    # Include secondary images
        quality='high'
    )

fig, ax = create_luminet_accurate_visualization()
plt.title("Scientifically Accurate Luminet Reproduction")
plt.show()
```

### 2. Aesthetic Optimization Workflow

For visually striking results:

```python
def create_aesthetic_visualization():
    """Create visually optimized black hole image."""
    
    return draw_blackhole(
        mass=1.0,
        inclination=85.0,           # Slightly more edge-on
        particle_count=20000,       # High resolution
        power_scale=0.95,          # Enhanced contrast
        enable_ghost_images=True,
        quality='high'
    )

fig, ax = create_aesthetic_visualization()
plt.title("Aesthetically Optimized Visualization")
plt.show()
```

### 3. Performance Optimization Workflow

For interactive use:

```python
def create_fast_preview():
    """Create fast preview for interactive work."""
    
    return draw_blackhole(
        mass=1.0,
        inclination=80.0,
        particle_count=5000,        # Reduced for speed
        power_scale=0.85,
        quality='draft'             # Fast rendering
    )

fig, ax = create_fast_preview()
plt.title("Fast Preview")
plt.show()
```

## Parameter Sensitivity Analysis

### Systematic Parameter Study

```python
import numpy as np

def parameter_sensitivity_study():
    """Analyze sensitivity to key parameters."""
    
    # Base parameters
    base_params = {
        'mass': 1.0,
        'inclination': 80.0,
        'particle_count': 8000,
        'power_scale': 0.9
    }
    
    # Parameter variations
    variations = {
        'mass': [0.5, 1.0, 2.0],
        'inclination': [70, 80, 90],
        'power_scale': [0.7, 0.9, 0.98]
    }
    
    results = {}
    
    for param_name, values in variations.items():
        results[param_name] = []
        
        for value in values:
            # Create modified parameters
            params = base_params.copy()
            params[param_name] = value
            
            # Time the calculation
            start_time = time.time()
            fig, ax = draw_blackhole(**params, quality='draft')
            end_time = time.time()
            
            results[param_name].append({
                'value': value,
                'time': end_time - start_time
            })
            
            plt.close(fig)
    
    # Print results
    for param_name, param_results in results.items():
        print(f"\n{param_name.title()} sensitivity:")
        for result in param_results:
            print(f"  {result['value']}: {result['time']:.2f}s")

parameter_sensitivity_study()
```

## Troubleshooting Parameter Issues

### Common Parameter Problems

#### 1. Visualization Too Dark

```python
# Problem: Can't see disk features
fig, ax = draw_blackhole(power_scale=0.5)  # Too low

# Solution: Increase power scale
fig, ax = draw_blackhole(power_scale=0.9)  # Better contrast
```

#### 2. Calculation Too Slow

```python
# Problem: Takes too long
fig, ax = draw_blackhole(particle_count=50000, quality='publication')

# Solution: Reduce complexity for testing
fig, ax = draw_blackhole(particle_count=8000, quality='standard')
```

#### 3. Missing Ghost Images

```python
# Problem: Only see direct image
fig, ax = draw_blackhole(inclination=45.0)  # Too face-on

# Solution: Increase inclination
fig, ax = draw_blackhole(inclination=85.0, enable_ghost_images=True)
```

#### 4. Pixelated Appearance

```python
# Problem: Blocky, low-resolution look
fig, ax = draw_blackhole(particle_count=2000)  # Too few particles

# Solution: Increase particle count
fig, ax = draw_blackhole(particle_count=15000)
```

## Parameter Presets

### Predefined Configurations

```python
# Scientific presets
LUMINET_ORIGINAL = {
    'mass': 1.0,
    'inclination': 80.0,
    'particle_count': 12000,
    'distribution_type': 'luminet',
    'power_scale': 0.9,
    'quality': 'high'
}

EDUCATIONAL = {
    'mass': 1.0,
    'inclination': 75.0,
    'particle_count': 8000,
    'power_scale': 0.85,
    'quality': 'standard'
}

PRESENTATION = {
    'mass': 1.0,
    'inclination': 85.0,
    'particle_count': 18000,
    'power_scale': 0.95,
    'quality': 'high'
}

PUBLICATION = {
    'mass': 1.0,
    'inclination': 80.0,
    'particle_count': 25000,
    'power_scale': 0.92,
    'quality': 'publication'
}

# Use presets
fig, ax = draw_blackhole(**LUMINET_ORIGINAL)
plt.title("Luminet Original Parameters")
plt.show()
```

## Next Steps

Now that you understand parameter tuning:

1. **[Advanced Techniques](advanced_techniques.md)** - Learn professional features
2. **[Particle to Publication Workflow](particle_to_publication.md)** - Complete workflow guide
3. **[Animation Creation](animation_workflow.md)** - Create parameter animations
4. **[Troubleshooting Guide](troubleshooting.md)** - Solve common issues

Master these parameters, and you'll be creating stunning, scientifically accurate black hole visualizations that rival the original Luminet masterpiece!