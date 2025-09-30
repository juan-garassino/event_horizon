# Event Horizon - Advanced Black Hole Visualization Framework

A comprehensive, unified framework for simulating and visualizing black hole physics, combining state-of-the-art algorithms with modern particle-based rendering techniques.

## Overview

Event Horizon is a professional-grade framework that provides:
- **Unified Mathematical Engine** - Advanced geodesic calculations and flux modeling
- **Flexible Visualization System** - From particle-based rendering to isoradial analysis
- **Modular Architecture** - Clean, extensible design for research and education
- **Legacy Compatibility** - Seamless integration with existing black hole simulation code

## Features

### 🔬 **Physics Engine**
- Schwarzschild and Kerr black hole spacetimes
- Gravitational lensing calculations
- Accretion disk modeling with realistic flux profiles
- Doppler shift and redshift effects

### 🎨 **Visualization Capabilities**
- Particle-based black hole images (Luminet-style)
- Isoradial and isoredshift curve analysis
- Interactive velocity field visualization
- Publication-quality rendering

### ⚙️ **Framework Features**
- Unified configuration system
- Multiple quality presets (draft to publication)
- Extensible adapter system for reference implementations
- Comprehensive validation and error handling

## Quick Start

### Installation

```bash
git clone https://github.com/your-repo/eventHorizon.git
cd eventHorizon
pip install -r requirements.txt
```

### Basic Usage

```python
from eventHorizon import VisualizationModel, UnifiedPlotter, get_default_config
# Or use clean framework-native aliases:
# from eventHorizon import ParticleModel, ParticlePlotter, get_default_config

# Create model with default configuration
config = get_default_config()
model = VisualizationModel(config)  # or ParticleModel(config)

# Generate visualization data
result = model.generate_visualization_data()

# Create and display plot
plotter = UnifiedPlotter(config)  # or ParticlePlotter(config)
fig = plotter.plot_visualization_result(result, plot_type="combined")
fig.show()
```

### Advanced Configuration

```python
from eventHorizon.config import ModelConfig, PhysicsConfig, get_preset_config

# Use high-quality preset
config = get_preset_config('high_quality')

# Or create custom configuration
config = ModelConfig(
    physics=PhysicsConfig(
        mass=1.0,
        inclination_deg=80.0,
        accretion_rate=1e-8
    )
)

model = VisualizationModel(config)
```

## Project Structure

```
eventHorizon/                    # Main framework package
├── core/                        # Core models and physics engines
│   ├── visualization_model.py   # Unified visualization model
│   ├── particle_system.py       # Particle sampling and management
│   ├── physics_engine.py        # Physics calculations
│   └── isoradial_model.py       # Isoradial analysis tools
├── math/                        # Mathematical foundations
│   ├── geodesics.py             # Geodesic calculations
│   ├── flux_calculations.py     # Flux and redshift modeling
│   ├── numerical_solvers.py     # Numerical methods
│   └── spacetime_geometry.py    # Coordinate transformations
├── config/                      # Configuration management
│   ├── model_config.py          # Unified configuration classes
│   └── presets.py               # Quality and use-case presets
├── visualization/               # Plotting and rendering
│   ├── unified_plotter.py       # Main plotting interface
│   └── isoradial_plotter.py     # Specialized isoradial plots
├── adapters/                    # Reference implementation adapters
│   └── reference_adapter.py     # Unified adapter interface
└── utils/                       # Utilities and helpers

examples/                        # Usage examples and demos
tests/                          # Test suite
references/                     # Reference papers and implementations
```

## Configuration Presets

Event Horizon includes several built-in quality presets:

- **`draft_quality`** - Fast preview rendering
- **`standard_quality`** - Balanced quality and performance
- **`high_quality`** - Detailed analysis and visualization
- **`publication_quality`** - Maximum quality for research papers
- **`animation_preset`** - Optimized for video generation
- **`interactive_preset`** - Real-time exploration

## Mathematical Modules

### Geodesics
```python
from eventHorizon.math import Geodesics

geodesics = Geodesics()
impact_param = geodesics.calculate_impact_parameter(radius, angle, mass)
```

### Flux Calculations
```python
from eventHorizon.math import FluxCalculations

flux_calc = FluxCalculations()
observed_flux = flux_calc.observed_flux(radius, accretion_rate, mass, redshift)
```

### Numerical Methods
```python
from eventHorizon.math import NumericalSolvers

solver = NumericalSolvers(tolerance=1e-10)
roots = solver.find_roots(equation, search_range)
```

## Visualization Examples

### Basic Black Hole Image
```python
from eventHorizon import create_visualization_model, create_unified_plotter

model = create_visualization_model('standard')
result = model.generate_visualization_data(particle_count=10000)

plotter = create_unified_plotter()
fig = plotter.plot_visualization_result(result, plot_type="lensed")
```

### Isoradial Analysis
```python
from eventHorizon.visualization import IsoradialPlotter

plotter = IsoradialPlotter()
fig = plotter.plot_isoradial_curves(radii=[6, 10, 20, 50], mass=1.0)
```

### Velocity Field Visualization
```python
plotter = UnifiedPlotter()
fig = plotter.plot_velocity_field_particles(
    radii_list=[6, 10, 15, 20], 
    rotation_direction='clockwise',
    doppler_coloring=True
)
```

## Framework-Native Aliases

Event Horizon provides clean, framework-native class names:

```python
# Clean framework-native names (recommended)
from eventHorizon import ParticleModel, ParticlePlotter, ParticleConfig
from eventHorizon.adapters import ClassicalAdapter, ParticleAdapter
from eventHorizon.math import ClassicalGeodesics, ParticleMath

# Or use the unified approach
from eventHorizon import VisualizationModel, UnifiedPlotter, ModelConfig
```

## Legacy Compatibility

Event Horizon maintains compatibility with existing code:

```python
# Legacy reference-specific imports still work (with deprecation warnings)
from eventHorizon import LuminetModel, LuminetPlotter
from eventHorizon.adapters import BhsimAdapter, LuminetAdapter
from eventHorizon.math import BhsimGeodesics, LuminetMath

# These now point to clean framework-native implementations
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Research Applications

Event Horizon has been designed for:
- **Astrophysics Research** - Black hole shadow modeling and analysis
- **Educational Visualization** - Teaching general relativity concepts
- **Computational Physics** - Algorithm development and testing
- **Scientific Publication** - High-quality figure generation

## Citation

If you use Event Horizon in your research, please cite:

```bibtex
@software{eventhorizon2024,
  title={Event Horizon: Advanced Black Hole Visualization Framework},
  author={Event Horizon Development Team},
  year={2024},
  url={https://github.com/your-repo/eventHorizon}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on foundational work by Luminet (1979) and subsequent researchers
- Incorporates algorithms from bhsim and luminet reference implementations
- Built with modern Python scientific computing stack

---

**Event Horizon** - *Visualizing the invisible, one photon at a time* 🌌