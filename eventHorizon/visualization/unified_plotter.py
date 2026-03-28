"""
Unified plotting interface for eventHorizon framework.

This module provides a unified plotting interface that can handle all types
of black hole visualization data in a consistent, framework-native way.
Includes luminet-style visualization methods extracted from reference implementation.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Union
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle

from ..core.visualization_model import VisualizationResult
from ..config.model_config import ModelConfig


class UnifiedPlotter:
    """Unified plotter for all black hole visualization types."""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize the unified plotter."""
        self.config = config
        self._setup_color_schemes()
        
    def _setup_color_schemes(self):
        """Setup color schemes for different visualization types."""
        self.color_schemes = {
            'plasma': plt.cm.plasma,
            'temperature': plt.cm.hot,
            'redshift': plt.cm.RdYlBu_r,
            'flux': plt.cm.viridis,
            'grayscale': plt.cm.gray
        }
        
    def plot_visualization_result(self, 
                                result: VisualizationResult,
                                plot_type: str = "particles",
                                figsize: Tuple[int, int] = (12, 8),
                                **kwargs) -> plt.Figure:
        """Plot a complete visualization result."""
        if plot_type == "particles":
            return self.plot_particles(result.particles, figsize=figsize, **kwargs)
        elif plot_type == "lensed":
            return self.plot_lensed_particles(result.lensed_positions, figsize=figsize, **kwargs)
        elif plot_type == "flux":
            return self.plot_flux_data(result.flux_data, figsize=figsize, **kwargs)
        elif plot_type == "combined":
            return self.plot_combined_view(result, figsize=figsize, **kwargs)
        elif plot_type == "luminet":
            # Use luminet-style rendering for the complete result
            return self.plot_luminet_style(
                particles_df=result.particles,
                ghost_particles_df=getattr(result, 'ghost_particles', None),
                black_hole_params=result.metadata.get('black_hole_params', {}),
                figsize=figsize,
                **kwargs
            )
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")
    
    def plot_particles(self, 
                      particles: pd.DataFrame,
                      figsize: Tuple[int, int] = (10, 8),
                      color_by: str = "radius",
                      show_disk_edges: bool = True,
                      show_event_horizon: bool = True,
                      **kwargs) -> plt.Figure:
        """Plot particle distribution."""
        fig, ax = plt.subplots(figsize=figsize)
        
        if len(particles) == 0:
            ax.text(0.5, 0.5, "No particles to display", 
                   transform=ax.transAxes, ha='center', va='center')
            return fig
        
        # Determine color mapping
        if color_by in particles.columns:
            colors = particles[color_by]
            colormap = self.color_schemes.get('plasma', plt.cm.plasma)
        else:
            colors = 'blue'
            colormap = None
        
        # Plot particles
        scatter = ax.scatter(
            particles.get('x', particles.get('radius', [])),
            particles.get('y', particles.get('phi', [])),
            c=colors,
            cmap=colormap,
            alpha=0.6,
            s=kwargs.get('point_size', 1),
            **{k: v for k, v in kwargs.items() if k not in ['point_size']}
        )
        
        # Add colorbar if using color mapping
        if colormap is not None and hasattr(scatter, 'get_array'):
            plt.colorbar(scatter, ax=ax, label=color_by)
        
        # Add reference circles
        if show_event_horizon:
            event_horizon = Circle((0, 0), 2.0, fill=False, color='red', 
                                 linestyle='--', alpha=0.7, label='Event Horizon')
            ax.add_patch(event_horizon)
        
        if show_disk_edges and self.config:
            inner_edge = self.config.disk.get_inner_edge(self.config.physics.mass)
            outer_edge = self.config.disk.get_outer_edge(self.config.physics.mass)
            
            inner_circle = Circle((0, 0), inner_edge, fill=False, color='orange',
                                linestyle=':', alpha=0.5, label='Disk Inner Edge')
            outer_circle = Circle((0, 0), outer_edge, fill=False, color='orange',
                                linestyle=':', alpha=0.5, label='Disk Outer Edge')
            ax.add_patch(inner_circle)
            ax.add_patch(outer_circle)
        
        ax.set_xlabel('X (GM/c²)')
        ax.set_ylabel('Y (GM/c²)')
        ax.set_title('Particle Distribution')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        return fig
    
    def plot_lensed_particles(self,
                            lensed_particles: pd.DataFrame,
                            figsize: Tuple[int, int] = (12, 8),
                            color_by: str = "flux",
                            **kwargs) -> plt.Figure:
        """Plot lensed particle positions."""
        fig, ax = plt.subplots(figsize=figsize)
        
        if len(lensed_particles) == 0:
            ax.text(0.5, 0.5, "No lensed particles to display", 
                   transform=ax.transAxes, ha='center', va='center')
            return fig
        
        # Plot lensed positions
        if color_by in lensed_particles.columns:
            colors = lensed_particles[color_by]
            colormap = self.color_schemes.get('flux', plt.cm.viridis)
        else:
            colors = 'blue'
            colormap = None
        
        scatter = ax.scatter(
            lensed_particles.get('alpha', []),
            lensed_particles.get('beta', []),
            c=colors,
            cmap=colormap,
            alpha=0.7,
            s=kwargs.get('point_size', 2),
            **{k: v for k, v in kwargs.items() if k not in ['point_size']}
        )
        
        if colormap is not None and hasattr(scatter, 'get_array'):
            plt.colorbar(scatter, ax=ax, label=color_by)
        
        ax.set_xlabel('α (arcsec)')
        ax.set_ylabel('β (arcsec)')
        ax.set_title('Lensed Particle Positions')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def plot_flux_data(self,
                      flux_data: pd.DataFrame,
                      figsize: Tuple[int, int] = (10, 8),
                      **kwargs) -> plt.Figure:
        """Plot flux and redshift data."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        if len(flux_data) == 0:
            for ax in [ax1, ax2]:
                ax.text(0.5, 0.5, "No flux data to display", 
                       transform=ax.transAxes, ha='center', va='center')
            return fig
        
        # Plot flux distribution
        if 'flux' in flux_data.columns:
            ax1.hist(flux_data['flux'], bins=50, alpha=0.7, color='blue')
            ax1.set_xlabel('Flux')
            ax1.set_ylabel('Count')
            ax1.set_title('Flux Distribution')
            ax1.grid(True, alpha=0.3)
        
        # Plot redshift distribution
        if 'redshift' in flux_data.columns:
            ax2.hist(flux_data['redshift'], bins=50, alpha=0.7, color='red')
            ax2.set_xlabel('Redshift Factor (1+z)')
            ax2.set_ylabel('Count')
            ax2.set_title('Redshift Distribution')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_combined_view(self,
                          result: VisualizationResult,
                          figsize: Tuple[int, int] = (15, 10),
                          **kwargs) -> plt.Figure:
        """Plot combined view of all visualization data."""
        fig = plt.figure(figsize=figsize)
        
        # Create subplot layout
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # Particle distribution
        ax1 = fig.add_subplot(gs[0, 0])
        if len(result.particles) > 0:
            ax1.scatter(result.particles.get('x', []), result.particles.get('y', []),
                       alpha=0.6, s=1, c='blue')
        ax1.set_title('Particle Distribution')
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        
        # Lensed positions
        ax2 = fig.add_subplot(gs[0, 1])
        if len(result.lensed_positions) > 0:
            ax2.scatter(result.lensed_positions.get('alpha', []), 
                       result.lensed_positions.get('beta', []),
                       alpha=0.7, s=2, c='red')
        ax2.set_title('Lensed Positions')
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        
        # Flux histogram
        ax3 = fig.add_subplot(gs[0, 2])
        if len(result.flux_data) > 0 and 'flux' in result.flux_data.columns:
            ax3.hist(result.flux_data['flux'], bins=30, alpha=0.7, color='green')
        ax3.set_title('Flux Distribution')
        ax3.grid(True, alpha=0.3)
        
        # Metadata display
        ax4 = fig.add_subplot(gs[1, :])
        ax4.axis('off')
        
        metadata_text = self._format_metadata(result.metadata)
        ax4.text(0.1, 0.9, metadata_text, transform=ax4.transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        return fig
    
    def plot_partial_isoradial_particles(self, radius: float, segments_per_radius: int = 8, **kwargs) -> plt.Figure:
        """Plot partial isoradial segments as particles at a single radius.
        
        Creates multiple partial segments around the same radial distance,
        each segment represented as a series of particle dots rather than
        continuous lines.
        """
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (10, 10)))
        
        segment_length = kwargs.get('segment_length', 0.3)
        particle_density = kwargs.get('particle_density', 20)
        rotation_direction = kwargs.get('rotation_direction', 'clockwise')
        
        # Create partial segments
        for i in range(segments_per_radius):
            start_angle = 2 * np.pi * i / segments_per_radius
            end_angle = start_angle + segment_length * 2 * np.pi / segments_per_radius
            
            angles = np.linspace(start_angle, end_angle, particle_density)
            x = radius * np.cos(angles)
            y = radius * np.sin(angles)
            
            # Apply Doppler coloring if requested
            if kwargs.get('doppler_coloring', False):
                colors = self._apply_doppler_coloring(angles, rotation_direction)
                ax.scatter(x, y, c=colors, s=kwargs.get('point_size', 2), alpha=0.7)
            else:
                ax.scatter(x, y, c='blue', s=kwargs.get('point_size', 2), alpha=0.7)
        
        ax.set_aspect('equal')
        ax.set_title(f'Partial Isoradial Particles at r={radius}')
        return fig
    
    def plot_multi_radius_partial_isoradials(self, radii_list: List[float], segments_per_radius: int = 8, **kwargs) -> plt.Figure:
        """Plot partial isoradial segments as particles at multiple radii."""
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (12, 12)))
        
        for radius in radii_list:
            # Plot each radius with different color intensity
            color_intensity = 1.0 - (radius - min(radii_list)) / (max(radii_list) - min(radii_list) + 1e-10)
            
            segment_length = kwargs.get('segment_length', 0.3)
            particle_density = kwargs.get('particle_density', 15)
            
            for i in range(segments_per_radius):
                start_angle = 2 * np.pi * i / segments_per_radius
                end_angle = start_angle + segment_length * 2 * np.pi / segments_per_radius
                
                angles = np.linspace(start_angle, end_angle, particle_density)
                x = radius * np.cos(angles)
                y = radius * np.sin(angles)
                
                ax.scatter(x, y, c='blue', alpha=color_intensity * 0.7, 
                          s=kwargs.get('point_size', 2))
        
        ax.set_aspect('equal')
        ax.set_title('Multi-Radius Partial Isoradials')
        return fig
    
    def plot_velocity_field_particles(self, radii_list: List[float], rotation_direction: str = 'clockwise', **kwargs) -> plt.Figure:
        """Plot particles showing velocity field with Doppler shift coloring."""
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (12, 12)))
        
        particle_density = kwargs.get('particle_density', 50)
        
        for radius in radii_list:
            angles = np.linspace(0, 2*np.pi, particle_density, endpoint=False)
            x = radius * np.cos(angles)
            y = radius * np.sin(angles)
            
            # Apply Doppler coloring
            colors = self._apply_doppler_coloring(angles, rotation_direction)
            ax.scatter(x, y, c=colors, s=kwargs.get('point_size', 3), alpha=0.8)
        
        ax.set_aspect('equal')
        ax.set_title('Velocity Field with Doppler Coloring')
        return fig
    
    def _apply_doppler_coloring(self, angles: np.ndarray, rotation_direction: str = 'clockwise') -> np.ndarray:
        """Apply blue/red Doppler shift coloring based on rotation direction."""
        # Simple Doppler coloring: blue for approaching, red for receding
        if rotation_direction == 'clockwise':
            # Right side approaching (blue), left side receding (red)
            colors = np.cos(angles)  # -1 to 1
        else:
            # Left side approaching (blue), right side receding (red)
            colors = -np.cos(angles)  # -1 to 1
        
        # Map to colormap (blue to red)
        return plt.cm.RdBu_r((colors + 1) / 2)  # Normalize to 0-1
    
    def plot_luminet_style(self, particles_df: pd.DataFrame, 
                          ghost_particles_df: Optional[pd.DataFrame] = None,
                          black_hole_params: Dict[str, Any] = None,
                          power_scale: float = 0.9,
                          levels: int = 100,
                          figsize: Tuple[int, int] = (10, 10),
                          **kwargs) -> plt.Figure:
        """
        Plot particles using Luminet's signature dot-based visualization technique.
        
        Extracted from luminet's plot_points() method with tricontourf rendering.
        """
        from .particle_renderer import ParticleRenderer, RenderConfig
        
        # Setup renderer with luminet configuration
        render_config = RenderConfig(
            power_scale=power_scale,
            levels=levels,
            background_color='black',
            brightness_scaling='logarithmic'
        )
        
        renderer = ParticleRenderer(render_config)
        
        # Setup viewport configuration
        viewport_config = {
            'figsize': figsize,
            'ax_lim': kwargs.get('ax_lim', (-40, 40)),
            'show_title': kwargs.get('show_title', False),
            'title': kwargs.get('title', 'Luminet Black Hole Visualization')
        }
        
        # Render using luminet technique
        fig, ax = renderer.render_frame(
            particles_df=particles_df,
            ghost_particles_df=ghost_particles_df,
            black_hole_params=black_hole_params,
            viewport_config=viewport_config
        )
        
        return fig
    
    def plot_isoredshift_contours(self, particles_df: pd.DataFrame,
                                 redshift_levels: List[float] = None,
                                 figsize: Tuple[int, int] = (10, 10),
                                 **kwargs) -> plt.Figure:
        """
        Plot isoredshift contours from particle data using luminet's technique.
        
        Extracted from luminet's plot_isoredshifts_from_points() method.
        """
        if redshift_levels is None:
            redshift_levels = [-0.2, -0.15, -0.1, -0.05, 0., 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75]
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Setup luminet-style figure
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        plt.axis('off')
        
        if particles_df.empty or 'X' not in particles_df.columns or 'Y' not in particles_df.columns:
            return fig
        
        # Setup color map (luminet uses RdBu_r)
        color_map = plt.get_cmap('RdBu_r')
        
        # Extract redshift data
        if 'z_factor' in particles_df.columns:
            redshift_data = particles_df['z_factor'].values
        elif 'redshift' in particles_df.columns:
            redshift_data = particles_df['redshift'].values
        else:
            # Generate dummy redshift data for demonstration
            redshift_data = np.zeros(len(particles_df))
        
        # Create tricontour plot (luminet's technique)
        try:
            # Adjust levels for plotting (add 1 to center around 1)
            plot_levels = [level + 1 for level in redshift_levels]
            
            contour = ax.tricontour(
                particles_df['X'], 
                particles_df['Y'],
                redshift_data,
                cmap=color_map,
                norm=plt.Normalize(0, 2),
                levels=plot_levels,
                nchunk=2,
                linewidths=2
            )
            
            # Add colorbar
            plt.colorbar(contour, ax=ax, label='Redshift Factor (1+z)')
            
        except Exception as e:
            # Fallback to scatter plot
            scatter = ax.scatter(particles_df['X'], particles_df['Y'], 
                               c=redshift_data, cmap=color_map, s=1)
            plt.colorbar(scatter, ax=ax, label='Redshift Factor')
        
        # Fill inner region with black (luminet technique)
        if kwargs.get('fill_inner_region', True):
            # Create a simple circular inner region if no specific coordinates provided
            inner_radius = kwargs.get('inner_radius', 6.0)
            circle = plt.Circle((0, 0), inner_radius, color='black', zorder=2)
            ax.add_patch(circle)
        
        ax.set_xlim(kwargs.get('ax_lim', (-40, 40)))
        ax.set_ylim(kwargs.get('ax_lim', (-40, 40)))
        ax.set_aspect('equal')
        
        if kwargs.get('show_title', True):
            ax.set_title('Isoredshift Contours', color='white')
        
        return fig
    
    def plot_flux_scaling_comparison(self, particles_df: pd.DataFrame,
                                   power_scales: List[float] = None,
                                   figsize: Tuple[int, int] = (15, 5),
                                   **kwargs) -> plt.Figure:
        """
        Compare different power scaling techniques from luminet.
        
        Shows how different power_scale values affect flux visualization.
        """
        if power_scales is None:
            power_scales = [0.5, 0.9, 1.0]
        
        fig, axes = plt.subplots(1, len(power_scales), figsize=figsize)
        if len(power_scales) == 1:
            axes = [axes]
        
        for i, power_scale in enumerate(power_scales):
            ax = axes[i]
            
            # Apply power scaling to flux
            if 'flux_o' in particles_df.columns and not particles_df.empty:
                max_flux = particles_df['flux_o'].max()
                min_flux = 0.0
                
                scaled_flux = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale 
                              for fl in particles_df['flux_o']]
                
                scatter = ax.scatter(particles_df.get('X', []), particles_df.get('Y', []),
                                   c=scaled_flux, cmap='Greys_r', s=1, alpha=0.7)
                
                # Add colorbar
                plt.colorbar(scatter, ax=ax, label=f'Scaled Flux (p={power_scale})')
            
            ax.set_aspect('equal')
            ax.set_title(f'Power Scale = {power_scale}')
            ax.set_facecolor('black')
        
        fig.patch.set_facecolor('black')
        plt.tight_layout()
        
        return fig

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for display."""
        lines = ["Visualization Metadata:"]
        for key, value in metadata.items():
            if isinstance(value, float):
                lines.append(f"  {key}: {value:.3f}")
            else:
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    
    def save_plot(self, fig: plt.Figure, filename: str, **kwargs):
        """Save plot to file."""
        fig.savefig(filename, dpi=kwargs.get('dpi', 300), 
                   bbox_inches='tight', **kwargs)
    
    def render_with_particle_renderer(self, particles_df: pd.DataFrame,
                                     ghost_particles_df: Optional[pd.DataFrame] = None,
                                     render_config: Optional[Dict[str, Any]] = None,
                                     **kwargs) -> plt.Figure:
        """
        Render particles using the dedicated ParticleRenderer with full luminet pipeline.
        
        This method provides direct access to the ParticleRenderer for advanced rendering.
        """
        from .particle_renderer import ParticleRenderer, RenderConfig
        
        # Setup render configuration
        if render_config:
            config = RenderConfig(**render_config)
        else:
            config = RenderConfig(
                power_scale=kwargs.get('power_scale', 0.9),
                levels=kwargs.get('levels', 100),
                background_color=kwargs.get('background_color', 'black'),
                brightness_scaling=kwargs.get('brightness_scaling', 'logarithmic')
            )
        
        # Create renderer
        renderer = ParticleRenderer(config)
        
        # Setup black hole parameters for proper edge handling
        black_hole_params = kwargs.get('black_hole_params', {})
        
        # Setup viewport configuration
        viewport_config = {
            'figsize': kwargs.get('figsize', (10, 10)),
            'ax_lim': kwargs.get('ax_lim', (-40, 40)),
            'show_title': kwargs.get('show_title', False),
            'title': kwargs.get('title', 'Luminet Black Hole Visualization')
        }
        
        # Render the frame
        fig, ax = renderer.render_frame(
            particles_df=particles_df,
            ghost_particles_df=ghost_particles_df,
            black_hole_params=black_hole_params,
            viewport_config=viewport_config
        )
        
        # Apply post-processing if requested
        effects = kwargs.get('post_processing_effects', [])
        if effects:
            fig, ax = renderer.apply_post_processing((fig, ax), effects)
        
        return fig
    
    def create_luminet_animation(self, particle_sequences: List[pd.DataFrame],
                                ghost_sequences: Optional[List[pd.DataFrame]] = None,
                                animation_config: Optional[Dict[str, Any]] = None,
                                **kwargs) -> List[plt.Figure]:
        """
        Create animation sequence using luminet-style rendering.
        
        Returns list of figures that can be exported as animation.
        """
        from .particle_renderer import ParticleRenderer, RenderConfig
        
        # Setup renderer
        config = RenderConfig(
            power_scale=kwargs.get('power_scale', 0.9),
            levels=kwargs.get('levels', 100),
            background_color='black'
        )
        renderer = ParticleRenderer(config)
        
        # Setup animation configuration
        anim_config = animation_config or {}
        anim_config.update(kwargs)
        
        # Render frames
        frames = []
        for i, particles_df in enumerate(particle_sequences):
            ghost_df = ghost_sequences[i] if ghost_sequences else None
            
            # Update frame-specific config
            frame_config = anim_config.copy()
            frame_config['title'] = f"Frame {i+1}/{len(particle_sequences)}"
            
            fig, ax = renderer.render_frame(
                particles_df=particles_df,
                ghost_particles_df=ghost_df,
                viewport_config=frame_config
            )
            
            frames.append(fig)
        
        return frames
    
    def plot_composed_luminet_image(self, direct_particles: pd.DataFrame,
                                   ghost_particles: pd.DataFrame,
                                   black_hole_params: Dict[str, Any] = None,
                                   composition_config: Dict[str, Any] = None,
                                   **kwargs) -> plt.Figure:
        """
        Create a fully composed luminet-style image with proper direct/ghost handling.
        
        Uses the LuminetCompositor for advanced image composition techniques.
        """
        from .luminet_compositor import LuminetCompositor, CompositionConfig
        
        # Setup compositor configuration
        if composition_config:
            config = CompositionConfig(**composition_config)
        else:
            config = CompositionConfig(
                inclination_angle=kwargs.get('inclination', 80.0),
                ghost_image_alpha=kwargs.get('ghost_alpha', 0.5),
                direct_image_alpha=kwargs.get('direct_alpha', 1.0)
            )
        
        # Create compositor
        compositor = LuminetCompositor(config)
        
        # Extract disk boundaries if black hole params provided
        if black_hole_params:
            boundaries = compositor.extract_disk_boundaries(black_hole_params)
            black_hole_params.update(boundaries)
        
        # Create composition
        fig, ax = compositor.compose_images(
            direct_particles=direct_particles,
            ghost_particles=ghost_particles,
            black_hole_params=black_hole_params,
            **kwargs
        )
        
        return fig
    
    def create_inclination_animation(self, direct_particles: pd.DataFrame,
                                   ghost_particles: pd.DataFrame = None,
                                   inclination_range: Tuple[float, float] = (0, 180),
                                   num_frames: int = 36,
                                   **kwargs) -> List[plt.Figure]:
        """
        Create animation showing black hole at different inclination angles.
        
        Uses the LuminetCompositor for proper viewing angle transformations.
        """
        from .luminet_compositor import LuminetCompositor, CompositionConfig
        
        # Generate inclination sequence
        start_incl, end_incl = inclination_range
        inclinations = np.linspace(start_incl, end_incl, num_frames)
        
        # Setup compositor
        config = CompositionConfig()
        compositor = LuminetCompositor(config)
        
        # Create compositions
        compositions = compositor.create_multi_inclination_composition(
            particles=direct_particles,
            ghost_particles=ghost_particles or pd.DataFrame(),
            inclinations=inclinations.tolist(),
            **kwargs
        )
        
        # Extract figures
        return [fig for fig, ax in compositions]

    def set_style(self, style: str = "default"):
        """Set matplotlib style."""
        if style == "dark":
            plt.style.use('dark_background')
        elif style == "publication":
            plt.rcParams.update({
                'font.size': 12,
                'axes.linewidth': 1.5,
                'lines.linewidth': 2,
                'figure.dpi': 150
            })
        elif style == "luminet":
            # Apply luminet-specific styling
            plt.rcParams.update({
                'figure.facecolor': 'black',
                'axes.facecolor': 'black',
                'axes.edgecolor': 'white',
                'axes.labelcolor': 'white',
                'text.color': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white'
            })
        else:
            plt.style.use('default')


def create_unified_plotter(config: Optional[ModelConfig] = None) -> UnifiedPlotter:
    """Create a unified plotter with optional configuration."""
    return UnifiedPlotter(config)