# Implementation Plan

- [x] 1. Set up project structure and placeholder interfaces
  - [x] 1.1 Create modular architecture with placeholder classes
    - Created eventHorizon/ module structure with core, math, visualization, and adapters
    - Set up ParticleSystem, RayTracingEngine, and PhysicsEngine class structures
    - Defined interfaces and data structures for particle-based visualization
    - _Requirements: 2.1, 2.2, 6.3_

  - [x] 1.2 Create configuration and model management system
    - Implemented ModelConfig system for unified parameter management
    - Created VisualizationModel as main interface for particle-based visualization
    - Set up UnifiedPlotter for consistent visualization output
    - _Requirements: 2.1, 2.2, 6.3_

  - [ ] 1.3 Extract and integrate bhsim geodesic algorithms
    - Extract impact_parameter(), simulate_flux(), and lambda_objective() functions from references/bhsim/core/blackhole.py
    - Implement actual geodesic calculations in eventHorizon/math/geodesics.py (currently all placeholder methods)
    - Fill in calculate_impact_parameter(), trace_photon_path(), and calculate_deflection_angle() methods
    - _Requirements: 2.1, 2.2, 2.5_

  - [ ] 1.4 Extract and integrate luminet particle sampling algorithms
    - Extract sample_points() method from references/luminet/core/black_hole.py
    - Implement actual particle physics calculations in eventHorizon/core/physics_engine.py (currently all placeholder methods)
    - Fill in temperature and flux profile calculations using luminet's disk physics
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 2. Fill in particle system with reference implementations
  - [x] 2.1 ParticleSystem structure and distribution algorithms completed
    - ParticleSystem class has complete structure with distribution algorithms
    - Particle data structure includes all necessary physical and visual properties
    - Distribution algorithms (uniform, biased_center, custom) are implemented
    - _Requirements: 3.1, 5.1_

  - [ ] 2.2 Extract and implement luminet physics calculations
    - Extract redshift_factor() and flux_observed() functions from references/luminet/core/black_hole.py
    - Replace placeholder _calculate_temperature() and _calculate_flux() methods in eventHorizon/core/particle_system.py
    - Implement actual Shakura-Sunyaev temperature and flux profiles from luminet reference
    - _Requirements: 3.1, 5.1, 5.2_

  - [ ] 2.3 Complete particle color and brightness mapping from references
    - Extract color mapping techniques from references/luminet/core/black_hole.py plot_points() method
    - Fill in _temperature_to_color(), _redshift_to_color(), _flux_to_color() methods in eventHorizon/core/particle_system.py
    - Implement proper power scaling and normalization from luminet's visualization code
    - _Requirements: 3.1, 3.2, 5.1_

- [ ] 3. Implement ray tracing using reference algorithms
  - [ ] 3.1 Extract and implement bhsim geodesic solver
    - Extract expr_u(), expr_r_inv(), lambdify() functions from references/bhsim/core/blackhole.py
    - Implement actual geodesic solver in eventHorizon/math/geodesics.py trace_photon_path() method (currently placeholder)
    - Replace placeholder methods with working elliptic integral calculations and Jacobi functions
    - _Requirements: 3.2, 3.3, 6.2_

  - [ ] 3.2 Implement bhsim impact parameter calculations
    - Extract impact_parameter() function and lambda_objective() from references/bhsim/core/blackhole.py
    - Fill in eventHorizon/math/geodesics.py calculate_impact_parameter() method (currently placeholder)
    - Add support for multiple image orders (n=0 direct, n>0 ghost) using bhsim's reorient_alpha() function
    - _Requirements: 3.2, 3.3, 6.3_

  - [ ] 3.3 Connect geodesics to particle lensing
    - Extract simulate_flux() function from references/bhsim/core/blackhole.py
    - Implement eventHorizon/core/physics_engine.py apply_relativistic_effects() method (currently placeholder)
    - Connect particle positions to lensed image positions using bhsim's coordinate transformation algorithms
    - _Requirements: 3.2, 3.4, 6.2_

- [ ] 4. Connect particle system to physics calculations
  - [ ] 4.1 Fill in PhysicsEngine with luminet reference implementations
    - Extract calc_impact_parameter() function from references/luminet/core/black_hole.py
    - Implement actual methods in eventHorizon/core/physics_engine.py (currently all placeholder methods)
    - Connect particle properties to realistic accretion disk physics using luminet's disk model
    - _Requirements: 1.1, 1.3, 2.3, 3.1_

  - [ ] 4.2 Integrate particle system with ray tracing
    - Fill in placeholder methods in eventHorizon/core/visualization_model.py (currently empty)
    - Connect ParticleSystem to geodesic calculations for complete particle processing pipeline
    - Implement actual data flow from particle generation → physics → lensing → final coordinates
    - _Requirements: 3.1, 5.1, 5.2_

  - [ ] 4.3 Create working end-to-end particle pipeline
    - Connect particle generation → physics calculation → geodesic ray tracing → visualization coordinates
    - Test complete pipeline against reference data from both bhsim and luminet for validation
    - Ensure performance is acceptable for interactive use with 10k+ particles
    - _Requirements: 3.2, 3.3, 3.4_

- [ ] 5. Implement Luminet-style visualization using reference techniques
  - [ ] 5.1 Fill in ParticleRenderer with luminet rendering logic
    - Extract tricontourf() and scatter plotting techniques from references/luminet/core/black_hole.py plot_points() method
    - Implement actual rendering methods in eventHorizon/visualization/particle_renderer.py (currently all placeholder methods)
    - Replace placeholder render_frame() method with working dot visualization code using matplotlib
    - _Requirements: 3.1, 4.1, 4.3_

  - [ ] 5.2 Complete UnifiedPlotter with luminet visualization methods
    - Extract plot_direct_image() and plot_ghost_image() functions from references/luminet/core/black_hole.py
    - Fill in particle plotting methods in eventHorizon/visualization/unified_plotter.py (currently placeholder methods)
    - Implement actual Luminet-style contour plotting with proper flux scaling and color mapping
    - _Requirements: 3.1, 4.3, 5.3_

  - [ ] 5.3 Create working Luminet visualization pipeline
    - Connect particle data to actual dot visualization output using luminet's tricontourf approach
    - Test visualization against reference luminet results for accuracy (compare with plot_points() output)
    - Ensure output matches the characteristic Luminet black hole appearance with proper flux gradients
    - _Requirements: 3.1, 4.1, 4.2_

- [ ] 6. Add quality enhancement and validation
  - [ ] 6.1 Implement configurable quality levels
    - Add quality level parameters to ModelConfig system
    - Create presets for different particle counts and precision levels
    - Connect quality settings to particle generation and rendering
    - _Requirements: 4.1, 4.2, 5.3_

  - [ ] 6.2 Create validation against reference implementations
    - Write comparison tools to validate output against references/bhsim and references/luminet results
    - Implement automated testing that compares key metrics (flux, positions, colors)
    - Create visual comparison tools for debugging differences
    - _Requirements: 4.2, 4.3, 4.4_

  - [ ] 6.3 Add performance optimization and monitoring
    - Profile particle generation and rendering performance
    - Implement efficient batch processing for large particle counts
    - Add progress monitoring for long-running calculations
    - _Requirements: 4.4, 6.1, 6.2_

- [ ] 7. Create comprehensive testing framework
  - [ ] 7.1 Write unit tests for extracted reference algorithms
    - Create tests for impact_parameter() and simulate_flux() functions extracted from bhsim reference
    - Test redshift_factor() and flux_observed() functions extracted from luminet reference
    - Validate that extracted algorithms produce identical results to original reference implementations
    - _Requirements: 2.1, 2.2, 6.3_

  - [ ] 7.2 Implement integration tests for complete pipeline
    - Test end-to-end particle generation → physics → geodesic ray tracing → visualization
    - Create regression tests comparing output with references/bhsim and references/luminet results
    - Validate that modular architecture preserves all original functionality from both references
    - _Requirements: 2.1, 2.2, 6.3_

  - [ ] 7.3 Add performance and accuracy benchmarks
    - Benchmark performance against original bhsim and luminet reference implementations
    - Create accuracy metrics for visual output comparison (flux values, particle positions, colors)
    - Implement automated testing that catches regressions when algorithms are modified
    - _Requirements: 2.1, 2.2, 2.5, 6.3_

- [ ] 8. Create working demonstration and examples
  - [ ] 8.1 Create example scripts using filled-in implementations
    - Write example scripts that demonstrate working particle-based visualization using extracted algorithms
    - Create examples that show the complete pipeline from particle generation to final Luminet-style image
    - Compare output with references/bhsim and references/luminet results to validate accuracy
    - _Requirements: 6.1, 6.2, 6.4_

  - [ ] 8.2 Update main.py with working Luminet functionality
    - Integrate working particle system with main.py interface using eventHorizon module
    - Add command-line options for particle-based visualization modes (--luminet, --particles)
    - Ensure new Luminet functionality works alongside existing isoradial/isoredshift features
    - _Requirements: 1.1, 1.3, 6.1, 6.5_

  - [ ] 8.3 Create documentation and usage guides
    - Document the new particle-based visualization capabilities and extracted algorithms
    - Create tutorials showing how to use the Luminet-style features with examples
    - Write troubleshooting guides for common issues with geodesic calculations and particle rendering
    - _Requirements: 4.4, 6.2, 6.3, 6.4_