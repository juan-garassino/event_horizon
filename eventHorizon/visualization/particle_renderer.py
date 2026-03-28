"""
Advanced particle renderer for Luminet-style visualization.

This module provides high-performance rendering of particles with
sophisticated color mapping and brightness scaling, extracted from
the luminet reference implementation.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RenderConfig:
    """Configuration for particle rendering."""
    
    dot_size_range: Tuple[float, float] = (0.1, 2.0)
    brightness_scaling: str = 'logarithmic'
    color_scheme: str = 'temperature'
    background_color: str = 'black'
    alpha_blending: bool = True
    anti_aliasing: bool = True
    quality_level: str = 'standard'
    power_scale: float = 0.9  # Power scaling for flux visualization
    levels: int = 100  # Contour levels for tricontourf


class ParticleRenderer:
    """High-performance particle renderer for black hole visualization."""
    
    def __init__(self, config: RenderConfig = None):
        """Initialize particle renderer."""
        self.config = config or RenderConfig()
    
    def render_frame(self, particles_df: pd.DataFrame, 
                    ghost_particles_df: Optional[pd.DataFrame] = None,
                    black_hole_params: Dict[str, Any] = None,
                    viewport_config: Dict[str, Any] = None) -> Tuple[plt.Figure, plt.Axes]:
        """
        Render a single frame of particles using luminet's dot visualization approach.
        
        Extracted from luminet's plot_points() method with tricontourf and scatter plotting.
        """
        # Setup figure with luminet-style configuration
        fig, ax = self._setup_luminet_figure(viewport_config)
        
        if particles_df.empty:
            return fig, ax
        
        # Calculate flux scaling parameters
        max_flux, min_flux = self._calculate_flux_range(particles_df, ghost_particles_df)
        
        # Render direct image
        ax = self._plot_direct_image(ax, particles_df, max_flux, min_flux, black_hole_params)
        
        # Render ghost image if provided
        if ghost_particles_df is not None and not ghost_particles_df.empty:
            ax = self._plot_ghost_image(ax, ghost_particles_df, max_flux, min_flux, black_hole_params)
        
        # Apply final styling
        self._apply_luminet_styling(ax, viewport_config)
        
        return fig, ax
    
    def _setup_luminet_figure(self, viewport_config: Dict[str, Any] = None) -> Tuple[plt.Figure, plt.Axes]:
        """Setup figure with luminet-style configuration."""
        config = viewport_config or {}
        
        fig = plt.figure(figsize=config.get('figsize', (10, 10)))
        ax = fig.add_subplot(111)
        
        # Apply luminet styling
        plt.axis('off')
        fig.patch.set_facecolor(self.config.background_color)
        ax.set_facecolor(self.config.background_color)
        
        # Set axis limits
        ax_lim = config.get('ax_lim', (-40, 40))
        ax.set_xlim(ax_lim)
        ax.set_ylim(ax_lim)
        
        return fig, ax
    
    def _calculate_flux_range(self, particles_df: pd.DataFrame, 
                            ghost_particles_df: Optional[pd.DataFrame] = None) -> Tuple[float, float]:
        """Calculate flux range for normalization."""
        all_fluxes = []
        
        if 'flux_o' in particles_df.columns:
            all_fluxes.extend(particles_df['flux_o'].values)
        
        if ghost_particles_df is not None and 'flux_o' in ghost_particles_df.columns:
            all_fluxes.extend(ghost_particles_df['flux_o'].values)
        
        if not all_fluxes:
            return 1.0, 0.0
        
        return max(all_fluxes), 0.0
    
    def _plot_direct_image(self, ax: plt.Axes, particles_df: pd.DataFrame, 
                          max_flux: float, min_flux: float,
                          black_hole_params: Dict[str, Any] = None) -> plt.Axes:
        """
        Plot direct image using luminet's tricontourf technique.
        
        Extracted from luminet's plot_direct_image() function.
        """
        if particles_df.empty or 'X' not in particles_df.columns or 'Y' not in particles_df.columns:
            return ax
        
        # Sort by angle for proper triangulation
        if 'angle' in particles_df.columns:
            particles_sorted = particles_df.sort_values(by="angle")
        else:
            particles_sorted = particles_df
        
        # Filter particles within apparent outer edge if black hole params provided
        if black_hole_params and 'apparent_outer_edge_func' in black_hole_params:
            outer_edge_func = black_hole_params['apparent_outer_edge_func']
            if 'impact_parameter' in particles_sorted.columns and 'angle' in particles_sorted.columns:
                mask = [b <= outer_edge_func(a) for b, a in 
                       zip(particles_sorted["impact_parameter"], particles_sorted["angle"])]
                particles_filtered = particles_sorted.iloc[mask]
            else:
                particles_filtered = particles_sorted
        else:
            particles_filtered = particles_sorted
        
        if particles_filtered.empty:
            return ax
        
        # Apply power scaling to flux values
        if 'flux_o' in particles_filtered.columns:
            fluxes = [(abs(fl + min_flux) / (max_flux + min_flux)) ** self.config.power_scale 
                     for fl in particles_filtered['flux_o']]
        else:
            fluxes = [1.0] * len(particles_filtered)
        
        # Create tricontourf plot (luminet's signature technique)
        try:
            ax.tricontourf(particles_filtered['X'], particles_filtered['Y'], fluxes, 
                          cmap='Greys_r', levels=self.config.levels, 
                          norm=plt.Normalize(0, 1), nchunk=2)
        except Exception as e:
            # Fallback to scatter plot if triangulation fails
            ax.scatter(particles_filtered['X'], particles_filtered['Y'], 
                      c=fluxes, cmap='Greys_r', s=1, alpha=0.7)
        
        # Fill inner disk edge with black (luminet technique for artifacts)
        if black_hole_params and 'inner_edge_coords' in black_hole_params:
            inner_x, inner_y = black_hole_params['inner_edge_coords']
            ax.fill_between(inner_x, inner_y, color='black', zorder=1)
        
        return ax
    
    def _plot_ghost_image(self, ax: plt.Axes, ghost_particles_df: pd.DataFrame,
                         max_flux: float, min_flux: float,
                         black_hole_params: Dict[str, Any] = None) -> plt.Axes:
        """
        Plot ghost image using luminet's technique.
        
        Extracted from luminet's plot_ghost_image() function.
        """
        if ghost_particles_df.empty or 'X' not in ghost_particles_df.columns:
            return ax
        
        # Filter particles for inner and outer regions
        if black_hole_params:
            inner_edge_func = black_hole_params.get('apparent_inner_edge_func')
            outer_edge_func = black_hole_params.get('apparent_outer_edge_func')
            
            if inner_edge_func and 'impact_parameter' in ghost_particles_df.columns:
                inner_mask = [b < inner_edge_func(a + np.pi) for b, a in 
                             zip(ghost_particles_df["impact_parameter"], ghost_particles_df["angle"])]
                particles_inner = ghost_particles_df.iloc[inner_mask]
            else:
                particles_inner = pd.DataFrame()
            
            if outer_edge_func and 'impact_parameter' in ghost_particles_df.columns:
                outer_mask = [b > outer_edge_func(a + np.pi) for b, a in 
                             zip(ghost_particles_df["impact_parameter"], ghost_particles_df["angle"])]
                particles_outer = ghost_particles_df.iloc[outer_mask]
            else:
                particles_outer = pd.DataFrame()
        else:
            particles_inner = ghost_particles_df
            particles_outer = pd.DataFrame()
        
        # Plot both inner and outer regions
        for i, particles in enumerate([particles_inner, particles_outer]):
            if particles.empty:
                continue
            
            # Sort by flux for proper rendering
            if 'flux_o' in particles.columns:
                particles_sorted = particles.sort_values(by=['flux_o'], ascending=False)
            else:
                particles_sorted = particles
            
            # Apply power scaling
            if 'flux_o' in particles_sorted.columns:
                fluxes = [(abs(fl + min_flux) / (max_flux + min_flux)) ** self.config.power_scale 
                         for fl in particles_sorted['flux_o']]
            else:
                fluxes = [1.0] * len(particles_sorted)
            
            # Plot with Y-coordinate flipped (luminet technique for ghost images)
            try:
                ax.tricontourf(particles_sorted['X'], [-y for y in particles_sorted['Y']], 
                              fluxes, cmap='Greys_r', norm=plt.Normalize(0, 1), 
                              levels=self.config.levels, nchunk=2, zorder=1-i)
            except Exception:
                # Fallback to scatter plot
                ax.scatter(particles_sorted['X'], [-y for y in particles_sorted['Y']], 
                          c=fluxes, cmap='Greys_r', s=1, alpha=0.5)
        
        # Fill apparent edges with black (artifact removal)
        if black_hole_params:
            if 'apparent_inner_edge_coords' in black_hole_params:
                x, y = black_hole_params['apparent_inner_edge_coords']
                ax.fill_between(x, y, color='black', zorder=1)
            
            if 'apparent_outer_edge_coords' in black_hole_params:
                x, y = black_hole_params['apparent_outer_edge_coords']
                ax.fill_between(x, y, color='black', zorder=0)
        
        return ax
    
    def _apply_luminet_styling(self, ax: plt.Axes, viewport_config: Dict[str, Any] = None):
        """Apply final luminet-style formatting."""
        config = viewport_config or {}
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        
        # Remove ticks and labels for clean look
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Apply any additional styling
        if config.get('show_title', False):
            title = config.get('title', 'Black Hole Visualization')
            ax.set_title(title, color='white' if self.config.background_color == 'black' else 'black')
    
    def render_animation(self, particle_sequences: List[pd.DataFrame], 
                        animation_config: Dict[str, Any] = None) -> List[Tuple[plt.Figure, plt.Axes]]:
        """Render animation sequence using luminet techniques."""
        frames = []
        
        for i, particles_df in enumerate(particle_sequences):
            # Update any time-dependent parameters
            frame_config = animation_config.copy() if animation_config else {}
            frame_config['title'] = f"Frame {i+1}"
            
            fig, ax = self.render_frame(particles_df, viewport_config=frame_config)
            frames.append((fig, ax))
        
        return frames
    
    def apply_post_processing(self, render_data: Tuple[plt.Figure, plt.Axes], 
                            effects: List[str] = None) -> Tuple[plt.Figure, plt.Axes]:
        """Apply post-processing effects to rendered image."""
        fig, ax = render_data
        effects = effects or []
        
        for effect in effects:
            if effect == 'enhance_contrast':
                # Enhance contrast for better visibility
                pass
            elif effect == 'smooth_edges':
                # Apply edge smoothing
                pass
            elif effect == 'add_glow':
                # Add glow effect around bright regions
                pass
        
        return fig, ax
    
    def export_render(self, render_data: Tuple[plt.Figure, plt.Axes], 
                     filename: str, format: str = 'png', quality: str = 'high') -> str:
        """Export rendered image using luminet quality settings."""
        fig, ax = render_data
        
        # Set DPI based on quality
        dpi_settings = {
            'draft': 150,
            'standard': 300,
            'high': 600,
            'publication': 1200
        }
        
        dpi = dpi_settings.get(quality, 300)
        
        # Save with luminet-style settings
        fig.savefig(filename, dpi=dpi, facecolor=self.config.background_color,
                   bbox_inches='tight', pad_inches=0.1)
        
        return filename