"""
Luminet-style black hole visualization functions.

This module provides the main entry points for luminet-style black hole visualization,
implementing the key functions from the luminet reference with enhanced capabilities.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Tuple, List, Union

from .core.particle_system import ParticleSystem
from .core.physics_engine import PhysicsEngine
from .core.visualization_model import VisualizationModel
from .visualization.particle_renderer import ParticleRenderer, RenderConfig
from .visualization.luminet_compositor import LuminetCompositor, CompositionConfig
from .visualization.unified_plotter import UnifiedPlotter
from .config.model_config import get_default_config, ModelConfig
from .utils.results_organization import save_figure_organized, create_results_structure
from .utils.validation import validate_and_suggest, validate_basic_params, validate_advanced_params
from .config.quality_presets import (
    quality_manager, get_quality_config, get_use_case_preset, 
    apply_quality_preset, apply_use_case_preset, QualityLevel
)
from .utils.progress_monitor import monitor_visualization_pipeline, create_progress_monitor


def draw_blackhole(
    mass: float = 1.0,
    inclination: float = 80.0,
    mode: str = 'points',
    particle_count: int = 10000,
    power_scale: float = 0.9,
    levels: int = 100,
    figsize: Tuple[int, int] = (10, 10),
    ax_lim: Tuple[float, float] = (-40, 40),
    background_color: str = 'black',
    show_ghost_image: bool = True,
    accretion_rate: float = 1.0,
    # Mode-specific parameters
    radii: List[float] = None,
    redshift_levels: List[float] = None,
    angular_resolution: int = 360,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Main entry point for unified black hole visualization.
    
    This function provides a unified interface to create different types of
    black hole visualizations through mode selection.
    
    Parameters
    ----------
    mass : float, default=1.0
        Black hole mass in geometric units
    inclination : float, default=80.0
        Observer inclination angle in degrees
    mode : str, default='points'
        Visualization mode: 'points', 'luminet', 'raytracing', 'isoradials', 
        'redshift', 'photon_sphere', 'apparent_edges'
    particle_count : int, default=10000
        Number of particles to generate for visualization
    power_scale : float, default=0.9
        Power scaling factor for flux visualization (luminet technique)
    levels : int, default=100
        Number of contour levels for tricontourf rendering
    figsize : Tuple[int, int], default=(10, 10)
        Figure size in inches
    ax_lim : Tuple[float, float], default=(-40, 40)
        Axis limits for the plot
    background_color : str, default='black'
        Background color for the plot
    show_ghost_image : bool, default=True
        Whether to include ghost image in visualization
    accretion_rate : float, default=1.0
        Mass accretion rate (normalized)
    radii : List[float], optional
        List of radii for isoradials mode
    redshift_levels : List[float], optional
        List of redshift levels for redshift mode
    angular_resolution : int, default=360
        Angular resolution for curve-based modes
    **kwargs
        Additional parameters passed to visualization components
        
    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes objects
        
    Examples
    --------
    >>> import eventHorizon
    >>> # Points/luminet visualization
    >>> fig, ax = eventHorizon.draw_blackhole(mass=1.0, inclination=80.0, mode='points')
    >>> plt.show()
    
    >>> # Isoradial curves
    >>> fig, ax = eventHorizon.draw_blackhole(
    ...     mass=1.0, inclination=80.0, mode='isoradials', 
    ...     radii=[10, 20, 30], angular_resolution=720
    ... )
    
    >>> # Redshift contours
    >>> fig, ax = eventHorizon.draw_blackhole(
    ...     mass=1.0, inclination=80.0, mode='redshift',
    ...     redshift_levels=[-0.1, 0, 0.1, 0.2]
    ... )
    
    >>> # Photon sphere
    >>> fig, ax = eventHorizon.draw_blackhole(mass=1.0, mode='photon_sphere')
    """
    from .visualization.mode_router import ModeRouter

    # Create mode router
    router = ModeRouter()

    # Validate mode
    if not router.validate_mode(mode):
        raise ValueError(f"Invalid mode '{mode}'. Valid modes: {sorted(router.VALID_MODES)}")

    # Pop export-related kwargs before passing to handler
    export_formats = kwargs.pop('export', None)  # e.g. ['svg', 'gcode'] or 'svg'
    export_dir = kwargs.pop('export_dir', None)
    export_bed_kwargs = kwargs.pop('export_bed_kwargs', None)

    # Normalize export_formats to list
    if isinstance(export_formats, str):
        export_formats = [export_formats]

    # Prepare parameters for handler
    params = {
        'mass': mass,
        'inclination': inclination,
        'particle_count': particle_count,
        'power_scale': power_scale,
        'levels': levels,
        'figsize': figsize,
        'ax_lim': ax_lim,
        'background_color': background_color,
        'show_ghost_image': show_ghost_image,
        'accretion_rate': accretion_rate,
        'radii': radii,
        'redshift_levels': redshift_levels,
        'angular_resolution': angular_resolution,
        **kwargs
    }

    # Route to appropriate handler
    handler = router.route_visualization(mode, params)

    # Validate parameters for the specific mode
    handler.validate_parameters()

    # Render visualization
    fig, ax = handler.render()

    # Plotter export (SVG / G-code) if requested and handler supports it
    if export_formats and handler.get_export_type() and handler.export_data:
        from .visualization.plotter_export import export_render_data
        out_dir = export_dir or "results"
        exported = export_render_data(
            render_type=handler.get_export_type(),
            data=handler.export_data,
            output_dir=out_dir,
            formats=export_formats,
            bed_kwargs=export_bed_kwargs,
        )
        if exported:
            print(f"Exported: {', '.join(exported)}")

    return fig, ax


def plot_points(
    mass: float = 1.0,
    inclination: float = 80.0,
    particle_count: int = 10000,
    power_scale: float = 0.9,
    levels: int = 100,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Luminet's plot_points() function - create dot-based black hole visualization.
    
    This function replicates luminet's signature plot_points() method with
    tricontourf rendering and power scaling for flux visualization.
    
    Parameters
    ----------
    mass : float, default=1.0
        Black hole mass
    inclination : float, default=80.0
        Observer inclination angle in degrees
    particle_count : int, default=10000
        Number of particles to sample
    power_scale : float, default=0.9
        Power scaling factor for flux (luminet's signature technique)
    levels : int, default=100
        Number of contour levels for tricontourf
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes
        
    Examples
    --------
    >>> fig, ax = plot_points(mass=1.0, inclination=80.0, particle_count=5000)
    >>> plt.show()
    """
    # Validate parameters
    validate_basic_params(mass, inclination, particle_count)
    
    return draw_blackhole(
        mass=mass,
        inclination=inclination,
        particle_count=particle_count,
        power_scale=power_scale,
        levels=levels,
        show_ghost_image=True,
        **kwargs
    )


def plot_scatter(
    mass: float = 1.0,
    inclination: float = 80.0,
    particle_count: int = 10000,
    power_scale: float = 0.9,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Scatter-dot visualization of the accretion disk with hot colormap.

    Parameters
    ----------
    mass : float, default=1.0
        Black hole mass
    inclination : float, default=80.0
        Observer inclination angle in degrees
    particle_count : int, default=10000
        Number of particles to sample
    power_scale : float, default=0.9
        Power scaling factor for flux
    **kwargs
        Additional visualization parameters

    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes
    """
    validate_basic_params(mass, inclination, particle_count)
    return draw_blackhole(
        mass=mass,
        inclination=inclination,
        mode='scatter',
        particle_count=particle_count,
        power_scale=power_scale,
        show_ghost_image=True,
        **kwargs
    )


def plot_isoradials(
    mass: float = 1.0,
    inclination: float = 80.0,
    radii: List[float] = None,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Luminet's plot_isoradials() function - plot constant radius curves.
    
    This function creates isoradial curves showing constant radius lines
    in the observer's frame, accounting for gravitational lensing.
    
    This is now a wrapper around draw_blackhole with mode='isoradials'
    to maintain backward compatibility while using the unified interface.
    
    Parameters
    ----------
    mass : float, default=1.0
        Black hole mass
    inclination : float, default=80.0
        Observer inclination angle in degrees
    radii : List[float], optional
        List of radii to plot. If None, uses default range
    **kwargs
        Additional plotting parameters
        
    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes
        
    Examples
    --------
    >>> fig, ax = plot_isoradials(mass=1.0, inclination=80.0, radii=[10, 20, 30])
    >>> plt.show()
    """
    # Validate parameters
    validate_and_suggest("plot_isoradials", mass=mass, inclination=inclination)
    
    if radii is None:
        radii = list(range(6, 51, 5))  # Default radii from 6M to 50M
    
    # Call draw_blackhole with isoradials mode, forwarding all parameters
    return draw_blackhole(
        mass=mass,
        inclination=inclination,
        mode='isoradials',
        radii=radii,
        **kwargs
    )


def plot_isoredshifts(
    mass: float = 1.0,
    inclination: float = 80.0,
    redshift_levels: List[float] = None,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Luminet's plot_isoredshifts() function - plot constant redshift curves.
    
    This function creates isoredshift curves showing constant redshift lines
    in the observer's frame, useful for understanding Doppler effects.
    
    This is now a wrapper around draw_blackhole with mode='redshift'
    to maintain backward compatibility while using the unified interface.
    
    Parameters
    ----------
    mass : float, default=1.0
        Black hole mass
    inclination : float, default=80.0
        Observer inclination angle in degrees
    redshift_levels : List[float], optional
        List of redshift values to plot. If None, uses default range
    **kwargs
        Additional plotting parameters
        
    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes
        
    Examples
    --------
    >>> fig, ax = plot_isoredshifts(mass=1.0, inclination=80.0)
    >>> plt.show()
    """
    # Validate parameters
    validate_and_suggest("plot_isoredshifts", mass=mass, inclination=inclination)
    
    if redshift_levels is None:
        redshift_levels = [-0.2, -0.15, -0.1, -0.05, 0., 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75]
    
    # Call draw_blackhole with redshift mode, forwarding all parameters
    return draw_blackhole(
        mass=mass,
        inclination=inclination,
        mode='redshift',
        redshift_levels=redshift_levels,
        **kwargs
    )


def plot_photon_sphere(
    mass: float = 1.0,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Luminet's plot_photon_sphere() function - plot the photon sphere boundary.
    
    This function plots the photon sphere at r = 3M, which represents the
    boundary where photons can orbit the black hole.
    
    This is now a wrapper around draw_blackhole with mode='photon_sphere'
    to maintain backward compatibility while using the unified interface.
    
    Parameters
    ----------
    mass : float, default=1.0
        Black hole mass
    **kwargs
        Additional plotting parameters
        
    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes
        
    Examples
    --------
    >>> fig, ax = plot_photon_sphere(mass=1.0)
    >>> plt.show()
    """
    # Validate parameters
    validate_and_suggest("plot_photon_sphere", mass=mass)
    
    # Call draw_blackhole with photon_sphere mode, forwarding all parameters
    return draw_blackhole(
        mass=mass,
        mode='photon_sphere',
        **kwargs
    )


def plot_apparent_inner_edge(
    mass: float = 1.0,
    inclination: float = 80.0,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot the apparent inner edge of the accretion disk.
    
    This function shows how the inner edge of the accretion disk appears
    to the observer due to gravitational lensing effects.
    
    This is now a wrapper around draw_blackhole with mode='apparent_edges'
    to maintain backward compatibility while using the unified interface.
    
    Parameters
    ----------
    mass : float, default=1.0
        Black hole mass
    inclination : float, default=80.0
        Observer inclination angle in degrees
    **kwargs
        Additional plotting parameters
        
    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes
    """
    # Validate parameters
    validate_and_suggest("plot_apparent_inner_edge", mass=mass, inclination=inclination)
    
    # Call draw_blackhole with apparent_edges mode, forwarding all parameters
    return draw_blackhole(
        mass=mass,
        inclination=inclination,
        mode='apparent_edges',
        **kwargs
    )


def _particles_to_dataframe(particles: List) -> pd.DataFrame:
    """
    Convert particle objects to DataFrame for visualization.
    
    Parameters
    ----------
    particles : List
        List of Particle objects
        
    Returns
    -------
    pd.DataFrame
        DataFrame with particle data
    """
    if not particles:
        return pd.DataFrame()
    
    data = []
    for particle in particles:
        data.append({
            'X': particle.observed_x,
            'Y': particle.observed_y,
            'radius': particle.radius,
            'angle': particle.angle,
            'flux_o': particle.flux,
            'z_factor': particle.redshift_factor,
            'impact_parameter': particle.impact_parameter,
            'brightness': particle.brightness,
            'temperature': particle.temperature,
            'is_visible': particle.is_visible
        })
    
    return pd.DataFrame(data)


# Convenience functions for quick access
def quick_blackhole(inclination: float = 80.0, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
    """Quick black hole visualization with default parameters."""
    return draw_blackhole(inclination=inclination, **kwargs)


def high_quality_blackhole(inclination: float = 80.0, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
    """High-quality black hole visualization with enhanced parameters."""
    return draw_blackhole(
        inclination=inclination,
        particle_count=50000,
        power_scale=0.8,
        levels=200,
        **kwargs
    )


def compare_inclinations(inclinations: List[float] = None, **kwargs) -> List[Tuple[plt.Figure, plt.Axes]]:
    """
    Create multiple black hole visualizations at different inclination angles.
    
    Parameters
    ----------
    inclinations : List[float], optional
        List of inclination angles. If None, uses [30, 60, 80, 90]
    **kwargs
        Additional parameters passed to draw_blackhole
        
    Returns
    -------
    List[Tuple[plt.Figure, plt.Axes]]
        List of figure and axes tuples
    """
    if inclinations is None:
        inclinations = [30, 60, 80, 90]
    
    results = []
    for inclination in inclinations:
        fig, ax = draw_blackhole(inclination=inclination, **kwargs)
        ax.set_title(f'Inclination = {inclination}°', color='white')
        results.append((fig, ax))
    
    return results

# Quality-enhanced visualization functions
def draw_blackhole_with_quality(
    quality_level: str = "standard",
    use_case: Optional[str] = None,
    show_progress: bool = True,
    **override_params
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create black hole visualization with specified quality level.
    
    Parameters
    ----------
    quality_level : str, default="standard"
        Quality level: "draft", "standard", "high", "publication"
    use_case : str, optional
        Use case preset: "interactive", "batch_processing", "publication", "education", "research"
    show_progress : bool, default=True
        Whether to show progress information
    **override_params
        Parameters to override from quality preset
        
    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes objects
        
    Examples
    --------
    >>> # Quick draft for interactive use
    >>> fig, ax = draw_blackhole_with_quality("draft")
    
    >>> # High-quality for research
    >>> fig, ax = draw_blackhole_with_quality("high", use_case="research")
    
    >>> # Publication quality with custom inclination
    >>> fig, ax = draw_blackhole_with_quality("publication", inclination=85.0)
    """
    # Apply quality preset
    if use_case is not None:
        params = apply_use_case_preset(use_case, **override_params)
        show_progress = params.pop('show_progress', show_progress)
    else:
        params = apply_quality_preset(quality_level, **override_params)
    
    # Monitor performance if requested
    if show_progress:
        quality_config = get_quality_config(quality_level)
        print(f"\n🎯 Quality Level: {quality_level.upper()}")
        print(f"   {quality_config.description}")
        print(f"   Particles: {params['particle_count']:,}")
        print(f"   Expected time: ~{quality_config.expected_time_seconds:.1f}s")
        
        # Use performance monitoring
        result, metrics = quality_manager.monitor_performance(
            draw_blackhole,
            QualityLevel(quality_level),
            params['particle_count'],
            **params
        )
        
        if metrics.success:
            print(f"✅ Completed in {metrics.execution_time:.1f}s")
            if metrics.memory_used_mb:
                print(f"   Memory used: {metrics.memory_used_mb:.1f} MB")
        else:
            print(f"❌ Failed: {metrics.error_message}")
            raise RuntimeError(f"Visualization failed: {metrics.error_message}")
        
        return result
    else:
        return draw_blackhole(**params)


def plot_points_with_quality(
    quality_level: str = "standard",
    show_progress: bool = True,
    **override_params
) -> Tuple[plt.Figure, plt.Axes]:
    """Plot points with specified quality level."""
    params = apply_quality_preset(quality_level, **override_params)
    
    if show_progress:
        quality_config = get_quality_config(quality_level)
        print(f"\n🎯 Plot Points - Quality: {quality_level.upper()}")
        print(f"   Particles: {params['particle_count']:,}")
    
    return plot_points(**params)


def create_quality_comparison(
    inclination: float = 80.0,
    quality_levels: List[str] = None,
    **kwargs
) -> List[Tuple[plt.Figure, plt.Axes]]:
    """
    Create comparison of different quality levels.
    
    Parameters
    ----------
    inclination : float, default=80.0
        Viewing angle in degrees
    quality_levels : List[str], optional
        Quality levels to compare. If None, uses ["draft", "standard", "high"]
    **kwargs
        Additional parameters
        
    Returns
    -------
    List[Tuple[plt.Figure, plt.Axes]]
        List of figure and axes tuples for each quality level
        
    Examples
    --------
    >>> results = create_quality_comparison(inclination=80.0)
    >>> for i, (fig, ax) in enumerate(results):
    ...     plt.figure(fig.number)
    ...     plt.show()
    """
    if quality_levels is None:
        quality_levels = ["draft", "standard", "high"]
    
    results = []
    
    print(f"\n🔍 Creating quality comparison for {len(quality_levels)} levels...")
    
    for i, quality in enumerate(quality_levels):
        print(f"\n   [{i+1}/{len(quality_levels)}] Generating {quality} quality...")
        
        fig, ax = draw_blackhole_with_quality(
            quality_level=quality,
            inclination=inclination,
            show_progress=False,
            **kwargs
        )
        
        # Add quality level to title
        quality_config = get_quality_config(quality)
        ax.set_title(
            f'{quality.title()} Quality ({quality_config.particle_count:,} particles)',
            color='white',
            fontsize=12
        )
        
        results.append((fig, ax))
    
    print(f"✅ Quality comparison completed!")
    return results


def benchmark_quality_levels(
    inclination: float = 80.0,
    runs_per_level: int = 3
) -> Dict[str, Any]:
    """
    Benchmark different quality levels for performance analysis.
    
    Parameters
    ----------
    inclination : float, default=80.0
        Viewing angle for benchmark
    runs_per_level : int, default=3
        Number of runs per quality level
        
    Returns
    -------
    Dict[str, Any]
        Benchmark results with timing and performance data
        
    Examples
    --------
    >>> results = benchmark_quality_levels()
    >>> print(f"Standard quality average: {results['standard']['avg_time']:.2f}s")
    """
    quality_levels = ["draft", "standard", "high"]
    results = {}
    
    print(f"\n⏱️  Benchmarking {len(quality_levels)} quality levels...")
    print(f"   Runs per level: {runs_per_level}")
    
    for quality in quality_levels:
        print(f"\n   Benchmarking {quality} quality...")
        
        times = []
        memory_usage = []
        
        for run in range(runs_per_level):
            print(f"     Run {run + 1}/{runs_per_level}...", end=' ')
            
            result, metrics = quality_manager.monitor_performance(
                draw_blackhole_with_quality,
                QualityLevel(quality),
                get_quality_config(quality).particle_count,
                quality_level=quality,
                inclination=inclination,
                show_progress=False
            )
            
            if metrics.success:
                times.append(metrics.execution_time)
                if metrics.memory_used_mb:
                    memory_usage.append(metrics.memory_used_mb)
                print(f"{metrics.execution_time:.2f}s")
                plt.close(result[0])  # Close figure to save memory
            else:
                print(f"FAILED: {metrics.error_message}")
        
        # Calculate statistics
        if times:
            results[quality] = {
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'particle_count': get_quality_config(quality).particle_count,
                'successful_runs': len(times),
                'total_runs': runs_per_level
            }
            
            if memory_usage:
                results[quality]['avg_memory_mb'] = sum(memory_usage) / len(memory_usage)
                results[quality]['max_memory_mb'] = max(memory_usage)
    
    # Print summary
    print(f"\n📊 Benchmark Summary:")
    for quality, data in results.items():
        print(f"   {quality.title():10} | "
              f"{data['avg_time']:6.2f}s avg | "
              f"{data['particle_count']:6,} particles | "
              f"{data['successful_runs']}/{data['total_runs']} success")
    
    return results


def get_performance_recommendations(target_time: float = 10.0) -> Dict[str, Any]:
    """
    Get performance recommendations based on target execution time.
    
    Parameters
    ----------
    target_time : float, default=10.0
        Target execution time in seconds
        
    Returns
    -------
    Dict[str, Any]
        Recommendations for achieving target performance
        
    Examples
    --------
    >>> recommendations = get_performance_recommendations(target_time=5.0)
    >>> print(recommendations['suggestion'])
    """
    return quality_manager.suggest_quality_optimization(target_time)


def progressive_enhancement_demo(
    inclination: float = 80.0,
    enhancement_steps: int = 3
) -> List[Tuple[plt.Figure, plt.Axes]]:
    """
    Demonstrate progressive quality enhancement.
    
    Parameters
    ----------
    inclination : float, default=80.0
        Viewing angle in degrees
    enhancement_steps : int, default=3
        Number of enhancement steps to show
        
    Returns
    -------
    List[Tuple[plt.Figure, plt.Axes]]
        List of progressively enhanced visualizations
        
    Examples
    --------
    >>> results = progressive_enhancement_demo()
    >>> for i, (fig, ax) in enumerate(results):
    ...     plt.figure(fig.number)
    ...     plt.show()
    """
    results = []
    base_quality = QualityLevel.DRAFT
    
    print(f"\n🚀 Progressive Enhancement Demo ({enhancement_steps} steps)")
    
    for step in range(enhancement_steps):
        enhancement_factor = 1.0 + (step * 0.5)  # 1.0, 1.5, 2.0, etc.
        
        print(f"\n   Step {step + 1}: Enhancement factor {enhancement_factor:.1f}x")
        
        # Create enhanced configuration
        enhanced_config = quality_manager.create_progressive_config(
            base_quality, enhancement_factor
        )
        
        # Generate visualization
        fig, ax = draw_blackhole(
            inclination=inclination,
            particle_count=enhanced_config.particle_count,
            power_scale=enhanced_config.power_scale,
            levels=enhanced_config.levels,
            figsize=enhanced_config.figsize
        )
        
        # Add enhancement info to title
        ax.set_title(
            f'Enhancement Step {step + 1} ({enhanced_config.particle_count:,} particles)',
            color='white',
            fontsize=12
        )
        
        results.append((fig, ax))
        
        print(f"     Particles: {enhanced_config.particle_count:,}")
        print(f"     Expected time: {enhanced_config.expected_time_seconds:.1f}s")
    
    print(f"\n✅ Progressive enhancement demo completed!")
    return results
# Animation and multi-inclination support functions
def create_inclination_movie(
    inclination_range: Tuple[float, float] = (10, 170),
    num_frames: int = 36,
    quality_level: str = "standard",
    output_format: str = "mp4",
    **kwargs
) -> str:
    """
    Create movie showing black hole appearance at different inclination angles.
    
    Parameters
    ----------
    inclination_range : Tuple[float, float], default=(10, 170)
        Range of inclination angles in degrees
    num_frames : int, default=36
        Number of frames in the movie
    quality_level : str, default="standard"
        Quality level: "draft", "standard", "high", "publication"
    output_format : str, default="mp4"
        Output format: "mp4", "gif", "frames"
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated movie file
        
    Examples
    --------
    >>> movie_path = create_inclination_movie(
    ...     inclination_range=(30, 150),
    ...     num_frames=24,
    ...     quality_level="high"
    ... )
    >>> print(f"Movie saved to: {movie_path}")
    """
    from .visualization.animation_engine import AnimationEngine, AnimationConfig
    
    config = AnimationConfig(
        quality_level=quality_level,
        output_format=output_format,
        fps=kwargs.pop('fps', 10),
        show_progress=kwargs.pop('show_progress', True)
    )
    
    engine = AnimationEngine(config)
    return engine.create_inclination_sweep(inclination_range, num_frames, **kwargs)


def create_mass_evolution_movie(
    mass_range: Tuple[float, float] = (0.5, 5.0),
    num_frames: int = 30,
    quality_level: str = "standard",
    output_format: str = "mp4",
    **kwargs
) -> str:
    """
    Create movie showing effect of different black hole masses.
    
    Parameters
    ----------
    mass_range : Tuple[float, float], default=(0.5, 5.0)
        Range of black hole masses
    num_frames : int, default=30
        Number of frames in the movie
    quality_level : str, default="standard"
        Quality level for visualization
    output_format : str, default="mp4"
        Output format: "mp4", "gif", "frames"
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated movie file
        
    Examples
    --------
    >>> movie_path = create_mass_evolution_movie(
    ...     mass_range=(1.0, 10.0),
    ...     num_frames=20
    ... )
    """
    from .visualization.animation_engine import AnimationEngine, AnimationConfig
    
    config = AnimationConfig(
        quality_level=quality_level,
        output_format=output_format,
        fps=kwargs.pop('fps', 10),
        show_progress=kwargs.pop('show_progress', True)
    )
    
    engine = AnimationEngine(config)
    return engine.create_mass_sweep(mass_range, num_frames, **kwargs)


def create_quality_evolution_movie(
    inclination: float = 80.0,
    particle_counts: List[int] = None,
    quality_level: str = "standard",
    output_format: str = "mp4",
    **kwargs
) -> str:
    """
    Create movie showing effect of particle count on visualization quality.
    
    Parameters
    ----------
    inclination : float, default=80.0
        Fixed inclination angle for comparison
    particle_counts : List[int], optional
        List of particle counts. If None, uses logarithmic range
    quality_level : str, default="standard"
        Base quality level (particle count will be overridden)
    output_format : str, default="mp4"
        Output format: "mp4", "gif", "frames"
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated movie file
        
    Examples
    --------
    >>> movie_path = create_quality_evolution_movie(
    ...     inclination=85.0,
    ...     particle_counts=[1000, 5000, 15000, 50000]
    ... )
    """
    from .visualization.animation_engine import AnimationEngine, AnimationConfig
    
    if particle_counts is None:
        # Default logarithmic range
        particle_counts = [int(10**x) for x in np.linspace(3, 4.7, 20)]  # 1k to ~50k
    
    config = AnimationConfig(
        quality_level=quality_level,
        output_format=output_format,
        fps=kwargs.pop('fps', 8),  # Slower for quality comparison
        show_progress=kwargs.pop('show_progress', True)
    )
    
    engine = AnimationEngine(config)
    return engine.create_particle_count_sweep(
        (min(particle_counts), max(particle_counts)),
        len(particle_counts),
        inclination=inclination,
        **kwargs
    )


def create_luminet_vs_traditional_movie(
    inclination_range: Tuple[float, float] = (30, 150),
    num_frames: int = 24,
    quality_level: str = "standard",
    output_format: str = "mp4",
    **kwargs
) -> str:
    """
    Create side-by-side comparison movie of luminet vs traditional methods.
    
    Parameters
    ----------
    inclination_range : Tuple[float, float], default=(30, 150)
        Range of inclination angles
    num_frames : int, default=24
        Number of frames in the movie
    quality_level : str, default="standard"
        Quality level for visualization
    output_format : str, default="mp4"
        Output format: "mp4", "gif", "frames"
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated movie file
        
    Examples
    --------
    >>> movie_path = create_luminet_vs_traditional_movie(
    ...     inclination_range=(45, 135),
    ...     num_frames=18
    ... )
    """
    from .visualization.animation_engine import AnimationEngine, AnimationConfig
    
    config = AnimationConfig(
        quality_level=quality_level,
        output_format=output_format,
        fps=kwargs.pop('fps', 10),
        show_progress=kwargs.pop('show_progress', True),
        figsize=(20, 10)  # Wide format for side-by-side
    )
    
    engine = AnimationEngine(config)
    return engine.create_comparison_animation(
        visualization_types=["luminet", "isoradials"],
        inclination_range=inclination_range,
        num_frames=num_frames,
        **kwargs
    )


def create_multi_method_comparison_movie(
    visualization_types: List[str] = None,
    inclination_range: Tuple[float, float] = (30, 150),
    num_frames: int = 24,
    quality_level: str = "standard",
    output_format: str = "mp4",
    **kwargs
) -> str:
    """
    Create comparison movie showing multiple visualization methods.
    
    Parameters
    ----------
    visualization_types : List[str], optional
        Methods to compare: ["luminet", "isoradials", "isoredshifts", "photon_sphere"]
        If None, uses ["luminet", "isoradials", "isoredshifts"]
    inclination_range : Tuple[float, float], default=(30, 150)
        Range of inclination angles
    num_frames : int, default=24
        Number of frames in the movie
    quality_level : str, default="standard"
        Quality level for visualization
    output_format : str, default="mp4"
        Output format: "mp4", "gif", "frames"
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated movie file
        
    Examples
    --------
    >>> movie_path = create_multi_method_comparison_movie(
    ...     visualization_types=["luminet", "isoradials", "isoredshifts"],
    ...     inclination_range=(60, 120)
    ... )
    """
    from .visualization.animation_engine import AnimationEngine, AnimationConfig
    
    if visualization_types is None:
        visualization_types = ["luminet", "isoradials", "isoredshifts"]
    
    # Adjust figure size based on number of methods
    figsize = (10 * len(visualization_types), 10)
    
    config = AnimationConfig(
        quality_level=quality_level,
        output_format=output_format,
        fps=kwargs.pop('fps', 8),  # Slower for detailed comparison
        show_progress=kwargs.pop('show_progress', True),
        figsize=figsize
    )
    
    engine = AnimationEngine(config)
    return engine.create_comparison_animation(
        visualization_types=visualization_types,
        inclination_range=inclination_range,
        num_frames=num_frames,
        **kwargs
    )


def create_parameter_sweep_movie(
    parameter_name: str,
    parameter_values: List[float],
    quality_level: str = "standard",
    output_format: str = "mp4",
    **kwargs
) -> str:
    """
    Create movie sweeping through values of a specific parameter.
    
    Parameters
    ----------
    parameter_name : str
        Name of parameter to sweep: "mass", "inclination", "power_scale", etc.
    parameter_values : List[float]
        Values of parameter for each frame
    quality_level : str, default="standard"
        Quality level for visualization
    output_format : str, default="mp4"
        Output format: "mp4", "gif", "frames"
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated movie file
        
    Examples
    --------
    >>> power_scales = [0.3, 0.5, 0.7, 0.9, 1.1, 1.3]
    >>> movie_path = create_parameter_sweep_movie("power_scale", power_scales)
    """
    from .visualization.animation_engine import AnimationEngine, AnimationConfig
    
    config = AnimationConfig(
        quality_level=quality_level,
        output_format=output_format,
        fps=kwargs.pop('fps', 10),
        show_progress=kwargs.pop('show_progress', True)
    )
    
    engine = AnimationEngine(config)
    return engine.create_parameter_evolution_animation(parameter_name, parameter_values, **kwargs)


def create_multi_inclination_grid(
    inclinations: List[float] = None,
    grid_size: Tuple[int, int] = None,
    quality_level: str = "standard",
    **kwargs
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create grid showing black hole appearance at multiple inclination angles.
    
    Parameters
    ----------
    inclinations : List[float], optional
        List of inclination angles. If None, uses evenly spaced angles
    grid_size : Tuple[int, int], optional
        Grid dimensions (rows, cols). If None, calculated automatically
    quality_level : str, default="standard"
        Quality level for visualization
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    Tuple[plt.Figure, np.ndarray]
        Figure and array of axes objects
        
    Examples
    --------
    >>> fig, axes = create_multi_inclination_grid(
    ...     inclinations=[30, 45, 60, 75, 85, 90],
    ...     grid_size=(2, 3)
    ... )
    >>> plt.show()
    """
    if inclinations is None:
        inclinations = [30, 45, 60, 75, 85, 90]
    
    if grid_size is None:
        # Calculate optimal grid size
        n = len(inclinations)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        grid_size = (rows, cols)
    
    print(f"\n🎯 Creating multi-inclination grid...")
    print(f"   Inclinations: {inclinations}")
    print(f"   Grid size: {grid_size[0]}×{grid_size[1]}")
    
    # Apply quality preset
    params = apply_quality_preset(quality_level, **kwargs)
    
    # Create figure
    fig, axes = plt.subplots(grid_size[0], grid_size[1], 
                           figsize=(grid_size[1] * 8, grid_size[0] * 8))
    fig.patch.set_facecolor('black')
    
    # Handle single subplot case
    if grid_size[0] * grid_size[1] == 1:
        axes = np.array([axes])
    elif grid_size[0] == 1 or grid_size[1] == 1:
        axes = axes.reshape(grid_size)
    
    # Create visualizations
    for i, inclination in enumerate(inclinations):
        row, col = i // grid_size[1], i % grid_size[1]
        
        print(f"   Creating visualization {i+1}/{len(inclinations)}: i={inclination}°")
        
        # Create individual visualization
        temp_fig, temp_ax = draw_blackhole(inclination=inclination, **params)
        
        # Copy to grid subplot
        axes[row, col].clear()
        axes[row, col].set_facecolor('black')
        
        for collection in temp_ax.collections:
            axes[row, col].add_collection(collection)
        
        axes[row, col].set_xlim(temp_ax.get_xlim())
        axes[row, col].set_ylim(temp_ax.get_ylim())
        axes[row, col].set_aspect('equal')
        axes[row, col].set_title(f'i = {inclination}°', color='white', fontsize=14)
        axes[row, col].axis('off')
        
        plt.close(temp_fig)
    
    # Hide unused subplots
    for i in range(len(inclinations), grid_size[0] * grid_size[1]):
        row, col = i // grid_size[1], i % grid_size[1]
        axes[row, col].axis('off')
    
    plt.tight_layout()
    
    print(f"✅ Multi-inclination grid completed!")
    return fig, axes


def create_parameter_comparison_grid(
    parameter_name: str,
    parameter_values: List[float],
    grid_size: Tuple[int, int] = None,
    quality_level: str = "standard",
    **kwargs
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create grid comparing different values of a parameter.
    
    Parameters
    ----------
    parameter_name : str
        Name of parameter to compare
    parameter_values : List[float]
        Values of parameter to show
    grid_size : Tuple[int, int], optional
        Grid dimensions. If None, calculated automatically
    quality_level : str, default="standard"
        Quality level for visualization
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    Tuple[plt.Figure, np.ndarray]
        Figure and array of axes objects
        
    Examples
    --------
    >>> masses = [0.5, 1.0, 2.0, 5.0]
    >>> fig, axes = create_parameter_comparison_grid("mass", masses)
    >>> plt.show()
    """
    if grid_size is None:
        # Calculate optimal grid size
        n = len(parameter_values)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n / cols))
        grid_size = (rows, cols)
    
    print(f"\n🎯 Creating {parameter_name} comparison grid...")
    print(f"   Values: {parameter_values}")
    print(f"   Grid size: {grid_size[0]}×{grid_size[1]}")
    
    # Apply quality preset
    params = apply_quality_preset(quality_level, **kwargs)
    
    # Create figure
    fig, axes = plt.subplots(grid_size[0], grid_size[1], 
                           figsize=(grid_size[1] * 8, grid_size[0] * 8))
    fig.patch.set_facecolor('black')
    
    # Handle single subplot case
    if grid_size[0] * grid_size[1] == 1:
        axes = np.array([axes])
    elif grid_size[0] == 1 or grid_size[1] == 1:
        axes = axes.reshape(grid_size)
    
    # Create visualizations
    for i, param_value in enumerate(parameter_values):
        row, col = i // grid_size[1], i % grid_size[1]
        
        print(f"   Creating visualization {i+1}/{len(parameter_values)}: {parameter_name}={param_value}")
        
        # Set parameter value
        current_params = params.copy()
        current_params[parameter_name] = param_value
        
        # Create individual visualization
        temp_fig, temp_ax = draw_blackhole(**current_params)
        
        # Copy to grid subplot
        axes[row, col].clear()
        axes[row, col].set_facecolor('black')
        
        for collection in temp_ax.collections:
            axes[row, col].add_collection(collection)
        
        axes[row, col].set_xlim(temp_ax.get_xlim())
        axes[row, col].set_ylim(temp_ax.get_ylim())
        axes[row, col].set_aspect('equal')
        axes[row, col].set_title(f'{parameter_name} = {param_value}', color='white', fontsize=14)
        axes[row, col].axis('off')
        
        plt.close(temp_fig)
    
    # Hide unused subplots
    for i in range(len(parameter_values), grid_size[0] * grid_size[1]):
        row, col = i // grid_size[1], i % grid_size[1]
        axes[row, col].axis('off')
    
    plt.tight_layout()
    
    print(f"✅ {parameter_name.title()} comparison grid completed!")
    return fig, axes