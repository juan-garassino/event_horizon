"""
Event Horizon - Advanced Black Hole Visualization Framework

A comprehensive framework for simulating and visualizing black hole physics,
combining the best algorithms from bhsim and luminet references with modern
particle-based rendering techniques.
"""

__version__ = "1.0.0"
__author__ = "Event Horizon Development Team"

from .core import VisualizationModel, create_visualization_model, VisualizationResult, ParticleSystem, RayTracingEngine, Isoradial, IsoredshiftModel, IsoGridModel, PartialIsoradialModel, MultiRadiusPartialIsoradialModel, VelocityFieldModel

# Physics imports: prefer new physics/ package, fall back to math/
try:
    from .physics import UnifiedGeodesics, Geodesics, SpacetimeGeometry
    from .physics.geodesics import KerrGeodesics, GeodesicMethod
except ImportError:
    from .math import UnifiedGeodesics, Geodesics, SpacetimeGeometry
    from .math.geodesics import KerrGeodesics, GeodesicMethod

from .math import UnifiedBlackHoleCalculator, FluxCalculations, NumericalMethods, NumericalSolvers, CoordinateSystems
from .math import generate_particles_fast, build_impact_table, redshift_vec, flux_observed_vec, flux_intrinsic_vec

from .config import ModelConfig, get_default_config, get_preset_config
from .adapters import UnifiedReferenceAdapter, ReferenceAdapter
from .visualization import UnifiedPlotter, create_unified_plotter, IsoradialPlotter, IsoredshiftPlotter, CombinedIsoPlotter
from .visualization import ParticleRenderer, RenderConfig, ExportManager, ModeRouter

# Luminet-style visualization functions: prefer new api module, fall back to luminet
try:
    from .api import (
        draw_blackhole,
        plot_points,
        plot_scatter,
        plot_isoradials,
        plot_isoredshifts,
        plot_photon_sphere,
        plot_apparent_inner_edge,
        quick_blackhole,
        high_quality_blackhole,
        compare_inclinations,
        # Quality-enhanced functions
        draw_blackhole_with_quality,
        plot_points_with_quality,
        create_quality_comparison,
        benchmark_quality_levels,
        get_performance_recommendations,
        progressive_enhancement_demo,
        # Animation and multi-inclination functions
        create_inclination_movie,
        create_mass_evolution_movie,
        create_quality_evolution_movie,
        create_luminet_vs_traditional_movie,
        create_multi_method_comparison_movie,
        create_parameter_sweep_movie,
        create_multi_inclination_grid,
        create_parameter_comparison_grid
    )
except ImportError:
    from .luminet import (
        draw_blackhole,
        plot_points,
        plot_scatter,
        plot_isoradials,
        plot_isoredshifts,
        plot_photon_sphere,
        plot_apparent_inner_edge,
        quick_blackhole,
        high_quality_blackhole,
        compare_inclinations,
        draw_blackhole_with_quality,
        plot_points_with_quality,
        create_quality_comparison,
        benchmark_quality_levels,
        get_performance_recommendations,
        progressive_enhancement_demo,
        create_inclination_movie,
        create_mass_evolution_movie,
        create_quality_evolution_movie,
        create_luminet_vs_traditional_movie,
        create_multi_method_comparison_movie,
        create_parameter_sweep_movie,
        create_multi_inclination_grid,
        create_parameter_comparison_grid
    )

# Utility functions for organized results
from .utils.results_organization import (
    create_results_structure,
    save_figure_organized,
    create_session_summary,
    get_organized_path,
    list_generated_files,
    cleanup_old_results,
    start_session,
    end_session,
    get_active_session_path,
    list_sessions,
    archive_loose_files,
)

# Quality and performance utilities
from .config.quality_presets import (
    get_quality_config,
    get_use_case_preset,
    apply_quality_preset,
    apply_use_case_preset
)
from .utils.progress_monitor import (
    create_progress_monitor,
    monitor_visualization_pipeline
)

# Legacy aliases for backward compatibility (deprecated)
from .core import LuminetModel, LuminetConfig
from .config import LuminetConfiguration

# Clean framework-native aliases
ParticleModel = VisualizationModel
ParticlePlotter = UnifiedPlotter
ParticleConfig = ModelConfig
ClassicalAdapter = UnifiedReferenceAdapter
ParticleAdapter = UnifiedReferenceAdapter

# Legacy reference-specific aliases (deprecated)
LuminetModel = ParticleModel
LuminetPlotter = ParticlePlotter
LuminetConfiguration = ParticleConfig
BhsimAdapter = ClassicalAdapter
LuminetAdapter = ParticleAdapter

__all__ = [
    # Primary unified interfaces
    'VisualizationModel',
    'create_visualization_model',
    'VisualizationResult',
    'ParticleSystem', 
    'RayTracingEngine',
    'Isoradial',
    'IsoredshiftModel', 
    'IsoGridModel',
    'PartialIsoradialModel',
    'MultiRadiusPartialIsoradialModel',
    'VelocityFieldModel',
    'UnifiedBlackHoleCalculator',
    'UnifiedGeodesics',
    'GeodesicMethod',
    'Geodesics',
    'FluxCalculations',
    'NumericalMethods',
    'NumericalSolvers',
    'CoordinateSystems',
    'SpacetimeGeometry',
    'KerrGeodesics',
    'ModelConfig',
    'get_default_config',
    'get_preset_config',
    'UnifiedReferenceAdapter',
    'ReferenceAdapter',
    'generate_particles_fast',
    'build_impact_table',
    'redshift_vec',
    'flux_observed_vec',
    'flux_intrinsic_vec',
    'UnifiedPlotter',
    'create_unified_plotter',
    'IsoradialPlotter',
    'IsoredshiftPlotter',
    'CombinedIsoPlotter',
    'ParticleRenderer',
    'RenderConfig',
    'ExportManager',
    'ModeRouter',

    # Luminet-style visualization functions (main entry points)
    'draw_blackhole',
    'plot_points',
    'plot_scatter',
    'plot_isoradials',
    'plot_isoredshifts',
    'plot_photon_sphere',
    'plot_apparent_inner_edge',
    'quick_blackhole',
    'high_quality_blackhole',
    'compare_inclinations',
    # Quality-enhanced functions
    'draw_blackhole_with_quality',
    'plot_points_with_quality',
    'create_quality_comparison',
    'benchmark_quality_levels',
    'get_performance_recommendations',
    'progressive_enhancement_demo',
    # Animation and multi-inclination functions
    'create_inclination_movie',
    'create_mass_evolution_movie',
    'create_quality_evolution_movie',
    'create_luminet_vs_traditional_movie',
    'create_multi_method_comparison_movie',
    'create_parameter_sweep_movie',
    'create_multi_inclination_grid',
    'create_parameter_comparison_grid',
    
    # Utility functions for organized results
    'create_results_structure',
    'save_figure_organized',
    'create_session_summary',
    'get_organized_path',
    'list_generated_files',
    'cleanup_old_results',
    'start_session',
    'end_session',
    'get_active_session_path',
    'list_sessions',
    'archive_loose_files',
    
    # Quality and performance utilities
    'get_quality_config',
    'get_use_case_preset',
    'apply_quality_preset',
    'apply_use_case_preset',
    'create_progress_monitor',
    'monitor_visualization_pipeline',
    
    # Clean framework-native aliases
    'ParticleModel',
    'ParticlePlotter', 
    'ParticleConfig',
    'ClassicalAdapter',
    'ParticleAdapter',
    
    # Legacy compatibility (deprecated)
    'LuminetModel',
    'LuminetConfiguration',
    'BhsimAdapter',
    'LuminetAdapter',
    'LuminetPlotter'
]