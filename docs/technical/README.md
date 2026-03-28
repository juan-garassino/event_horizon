# EventHorizon Technical Documentation

This directory contains comprehensive technical documentation for the EventHorizon black hole visualization system, focusing on the particle-based visualization capabilities and extracted algorithms from reference implementations.

## Documentation Structure

- **[Particle System Architecture](particle_system_architecture.md)** - Core particle-based visualization system
- **[Physics Engine](physics_engine.md)** - Physical calculations and relativistic effects
- **[Particle Renderer](particle_renderer.md)** - Advanced rendering and visualization techniques
- **[Mathematical Foundations](mathematical_foundations.md)** - Mathematical algorithms from bhsim and luminet references
- **[API Reference](api_reference.md)** - Complete API documentation
- **[Developer Guide](developer_guide.md)** - Guide for extending the particle visualization system

## Quick Start for Developers

The EventHorizon system implements Jean-Pierre Luminet's iconic 1979 black hole visualization using a particle-based approach. The system extracts and consolidates algorithms from both bhsim and luminet reference implementations.

### Core Components

1. **ParticleSystem** - Manages discrete matter representation in the accretion disk
2. **PhysicsEngine** - Handles physical calculations and relativistic effects
3. **ParticleRenderer** - Provides Luminet-style dot visualization with tricontourf rendering
4. **Mathematical Modules** - Extracted geodesic calculations and flux computations

### Key Features

- **Extracted Algorithms**: Direct implementation of bhsim geodesic calculations and luminet physics
- **Modular Architecture**: Clean separation between mathematical computations, physics, and visualization
- **Progressive Quality**: Configurable quality levels from draft to publication-ready
- **Backward Compatibility**: Maintains all existing visualization capabilities

## Getting Started

```python
from eventHorizon import draw_blackhole, ParticleSystem, PhysicsEngine

# Basic luminet-style visualization
fig, ax = draw_blackhole(
    mass=1.0,
    inclination=80.0,
    particle_count=10000,
    quality='standard'
)

# Advanced usage with custom particle system
particle_system = ParticleSystem(
    particle_count=20000,
    distribution_type='luminet'
)
particles = particle_system.generate_particles()

physics_engine = PhysicsEngine(mass=1.0)
processed_particles = physics_engine.execute_complete_pipeline(
    particles, inclination=80.0
)
```

## Architecture Overview

The system follows a modular pipeline architecture:

```
Particle Generation → Physics Calculations → Geodesic Ray Tracing → Lensing Effects → Visualization
```

Each component is designed to be independently testable and extensible while maintaining the scientific accuracy of the original reference implementations.