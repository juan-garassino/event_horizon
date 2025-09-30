# Event Horizon - Advanced Black Hole Visualization Framework

Event Horizon is a comprehensive framework for simulating and visualizing black hole physics, combining the best algorithms from bhsim and luminet references with modern particle-based rendering techniques.

## Architecture Overview

The Event Horizon framework is organized into several key modules:

### Core Components (`eventHorizon/core/`)
- **`base_model.py`** - Enhanced base model with backward compatibility
- **`particle_system.py`** - Particle system for dot-based visualization
- **`ray_tracing.py`** - Ray tracing engine for geodesic calculations
- **`luminet_model.py`** - Luminet-style black hole model
- **`isoradial_model.py`** - Isoradial and isoredshift curve models
- **`physics_engine.py`** - Physics calculations and updates (placeholder)
- **`renderer.py`** - Particle renderer for visualization (placeholder)

### Mathematical Foundations (`eventHorizon/math/`)
- **`unified_interface.py`** - Unified interface eliminating code duplication
- **`unified_geodesics.py`** - Unified geodesic calculations
- **`bhsim_*.py`** - Algorithms extracted from bhsim reference
- **`luminet_*.py`** - Algorithms extracted from luminet reference
- **`kerr_geodesics.py`** - Kerr spacetime calculations (placeholder)
- **`relativistic_effects.py`** - Relativistic effects calculations (placeholder)

### Configuration Management (`eventHorizon/config/`)
- **`luminet_config.py`** - Comprehensive configuration schema
- **`presets.py`** - Pre-configured settings for common scenarios
- **`validation.py`** - Configuration validation utilities

### Integration Adapters (`eventHorizon/adapters/`)
- **`bhsim_adapter.py`** - Adapter for bhsim algorithms
- **`luminet_adapter.py`** - Adapter for luminet algorithms  
- **`legacy_adapter.py`** - Backward compatibility adapter

### Visualization (`eventHorizon/visualization/`)
- **`particle_renderer.py`** - Advanced particle rendering
- **`luminet_plotter.py`** - Luminet-style plotting with isoradial support
- **`isoradial_plotter.py`** - Specialized isoradial and isoredshift plotting
- **`interactive_viewer.py`** - Interactive visualization (placeholder)
- **`animation_engine.py`** - Animation creation (placeholder)
- **`export_manager.py`** - Export utilities (placeholder)

### Utilities (`eventHorizon/utils/`)
- **`coordinates.py`** - Coordinate transformations
- **`data_structures.py`** - Optimized data structures
- **`performance.py`** - Performance profiling
- **`validation.py`** - Parameter validation

## Key Features

### 1. Unified Algorithm Interface
- Automatically selects the best algorithm (bhsim vs luminet) based on parameters
- Eliminates code duplication between reference implementations
- Maintains backward compatibility with existing code

### 2. Particle-Based Visualization
- Represents accretion disk matter as individual particles/dots
- Supports multiple distribution strategies (uniform, biased, custom)
- Realistic physical properties (temperature, flux, redshift)

### 3. Isoradial and Isoredshift Curves
- **Isoradial curves**: Constant radius curves showing gravitational lensing effects
- **Isoredshift curves**: Constant redshift curves revealing relativistic effects
- Color-coded redshift visualization along isoradial curves
- Combined grid visualization showing spacetime coordinate system

### 3. Advanced Ray Tracing
- Geodesic calculations in Schwarzschild spacetime
- Support for multiple image orders (direct, ghost images)
- Configurable precision and performance settings

### 4. Comprehensive Configuration
- YAML/JSON configuration files with validation
- Quality presets (draft, standard, high, publication)
- Cross-parameter consistency checking

### 5. Extensible Architecture
- Placeholder implementations for future features
- Clean separation of concerns
- Modular design for easy extension

## Usage Examples

### Basic Usage
```python
from eventHorizon import VisualizationModel, UnifiedPlotter, get_default_config
from eventHorizon import Geodesics, FluxCalculations, NumericalMethods

# Create model with default configuration
config = get_default_config()
model = VisualizationModel(config)

# Generate complete visualization data
result = model.generate_visualization_data()

# Create unified plotter and visualize
plotter = UnifiedPlotter(config)
fig = plotter.plot_visualization_result(result, plot_type="combined")

# Use unified mathematical modules directly
geodesics = Geodesics()
flux_calc = FluxCalculations()
numerical = NumericalMethods()

# Legacy usage (deprecated but supported)
from eventHorizon import LuminetModel  # Shows deprecation warning
legacy_model = LuminetModel(mass=1.0, inclination=80.0)
```

### Advanced Configuration
```python
from eventHorizon.config import get_config_preset, ConfigurationManager

# Use publication quality preset
config = get_config_preset('publication')
config.particle_system.particle_count = 200000
config.visualization.color_scheme = 'redshift'

# Validate configuration
manager = ConfigurationManager()
validation = manager.validate_configuration(config)
```

### Using Adapters
```python
from eventHorizon.adapters import BhsimAdapter, LuminetAdapter

# Use specific algorithm
bhsim = BhsimAdapter(mass=1.0)
impact_params = bhsim.calculate_impact_parameter(alpha_values, radius, inclination)

luminet = LuminetAdapter(mass=1.0, inclination=80.0)
particles_direct, particles_ghost = luminet.sample_particles(n_points=10000)
```

### Isoradial and Isoredshift Visualization
```python
from eventHorizon import Isoradial, IsoredshiftModel, IsoradialPlotter

# Create isoradial curves
isoradial_10M = Isoradial(mass=1.0, inclination=80.0, radius=10.0)
isoradial_20M = Isoradial(mass=1.0, inclination=80.0, radius=20.0)

# Create isoredshift curves
isoredshift_0 = IsoredshiftModel(mass=1.0, inclination=80.0, redshift_value=0.0)
isoredshift_pos = IsoredshiftModel(mass=1.0, inclination=80.0, redshift_value=0.2)

# Plot with specialized plotter
plotter = IsoradialPlotter()
plotter.plot_multiple_isoradials([isoradial_10M, isoradial_20M])
plotter.plot_isoradial_with_redshift_coloring(isoradial_10M)
```

### Partial Isoradial Particles with Velocity Field
```python
from eventHorizon import PartialIsoradialModel, MultiRadiusPartialIsoradialModel, LuminetPlotter

# Create partial isoradial segments as particles
partial_iso = PartialIsoradialModel(
    mass=1.0, inclination=80.0, radius=15.0, 
    n_segments=8, segment_length=0.3
)

# Multiple radii with partial segments
multi_radius = MultiRadiusPartialIsoradialModel(
    mass=1.0, inclination=80.0,
    radii_list=[6.0, 10.0, 15.0, 20.0, 30.0],
    segments_per_radius=8
)

# Plot with Doppler shift coloring
plotter = LuminetPlotter()
plotter.plot_partial_isoradial_particles(
    radius=15.0, segments_per_radius=8,
    rotation_direction='clockwise', doppler_coloring=True
)
plotter.plot_multi_radius_partial_isoradials(
    radii_list=[6.0, 10.0, 15.0, 20.0, 30.0],
    rotation_direction='clockwise', speed_scaling=True
)
plotter.plot_velocity_field_particles(
    radii_list=[6.0, 10.0, 15.0, 20.0, 30.0],
    rotation_direction='clockwise'
)
```

## Development Status

### Completed ✅
- Core architecture and module structure
- Configuration management system
- Adapter interfaces for reference implementations
- Basic particle system framework
- Ray tracing engine structure

### In Progress 🚧
- Full implementation of mathematical algorithms
- Particle physics calculations
- Rendering and visualization components

### Planned 📋
- Kerr spacetime support (rotating black holes)
- Interactive visualization tools
- Animation creation capabilities
- Performance optimizations
- 3D visualization support

## Migration from Legacy Code

The Event Horizon framework maintains backward compatibility through the `LegacyAdapter`. Existing code can be gradually migrated:

1. **Phase 1**: Use `LegacyAdapter` for immediate compatibility
2. **Phase 2**: Migrate to unified interfaces (`UnifiedBlackHoleCalculator`)
3. **Phase 3**: Adopt full Event Horizon architecture

## Contributing

When contributing to Event Horizon:

1. Follow the modular architecture principles
2. Add comprehensive docstrings and type hints
3. Include unit tests for new functionality
4. Update configuration schemas as needed
5. Maintain backward compatibility where possible

## References

- Luminet, J.-P. (1979). "Image of a spherical black hole with thin accretion disk"
- bhsim reference implementation
- luminet reference implementation

---

*Event Horizon Framework - Advancing Black Hole Visualization*