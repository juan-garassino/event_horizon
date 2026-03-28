"""
Luminet-style image composition module.

This module handles the composition of direct and ghost images,
disk edge handling, and viewing perspective transformations
extracted from the luminet reference implementation.
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class CompositionConfig:
    """Configuration for image composition."""
    
    inclination_angle: float = 80.0  # degrees
    viewing_distance: float = 1000.0  # in units of M
    disk_inner_edge: float = 6.0  # in units of M
    disk_outer_edge: float = 50.0  # in units of M
    ghost_image_alpha: float = 0.5  # transparency for ghost images
    direct_image_alpha: float = 1.0  # transparency for direct images
    fill_artifacts: bool = True  # fill triangulation artifacts with black


class LuminetCompositor:
    """
    Image compositor for luminet-style black hole visualizations.
    
    Handles composition of direct and ghost images with proper edge handling
    and viewing perspective transformations.
    """
    
    def __init__(self, config: CompositionConfig = None):
        """Initialize the compositor."""
        self.config = config or CompositionConfig()
    
    def compose_images(self, direct_particles: pd.DataFrame,
                      ghost_particles: pd.DataFrame,
                      black_hole_params: Dict[str, Any] = None,
                      **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """
        Compose direct and ghost images using luminet's technique.
        
        Extracted from luminet's image composition approach with proper
        handling of disk edges and black hole boundaries.
        """
        # Setup figure
        fig, ax = self._setup_composition_figure(**kwargs)
        
        # Calculate flux normalization parameters
        max_flux, min_flux = self._calculate_global_flux_range(direct_particles, ghost_particles)
        
        # Compose ghost image first (background layer)
        if not ghost_particles.empty:
            ax = self._compose_ghost_image(ax, ghost_particles, max_flux, min_flux, 
                                         black_hole_params, **kwargs)
        
        # Compose direct image (foreground layer)
        if not direct_particles.empty:
            ax = self._compose_direct_image(ax, direct_particles, max_flux, min_flux,
                                          black_hole_params, **kwargs)
        
        # Apply final composition effects
        ax = self._apply_composition_effects(ax, black_hole_params, **kwargs)
        
        return fig, ax
    
    def _setup_composition_figure(self, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Setup figure for image composition."""
        figsize = kwargs.get('figsize', (10, 10))
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        
        # Apply luminet-style setup
        plt.axis('off')
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        # Set viewing limits
        ax_lim = kwargs.get('ax_lim', (-40, 40))
        ax.set_xlim(ax_lim)
        ax.set_ylim(ax_lim)
        ax.set_aspect('equal')
        
        return fig, ax
    
    def _calculate_global_flux_range(self, direct_particles: pd.DataFrame,
                                   ghost_particles: pd.DataFrame) -> Tuple[float, float]:
        """Calculate global flux range for consistent normalization."""
        all_fluxes = []
        
        for df in [direct_particles, ghost_particles]:
            if not df.empty and 'flux_o' in df.columns:
                all_fluxes.extend(df['flux_o'].values)
        
        if not all_fluxes:
            return 1.0, 0.0
        
        return max(all_fluxes), 0.0
    
    def _compose_direct_image(self, ax: plt.Axes, particles: pd.DataFrame,
                            max_flux: float, min_flux: float,
                            black_hole_params: Dict[str, Any] = None,
                            **kwargs) -> plt.Axes:
        """
        Compose direct image with proper disk edge handling.
        
        Extracted from luminet's direct image composition technique.
        """
        if particles.empty or 'X' not in particles.columns or 'Y' not in particles.columns:
            return ax
        
        # Filter particles within apparent outer edge
        filtered_particles = self._filter_particles_by_disk_edge(
            particles, black_hole_params, 'outer', direct_image=True
        )
        
        if filtered_particles.empty:
            return ax
        
        # Apply flux scaling
        power_scale = kwargs.get('power_scale', 0.9)
        levels = kwargs.get('levels', 100)
        
        if 'flux_o' in filtered_particles.columns:
            scaled_flux = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale 
                          for fl in filtered_particles['flux_o']]
        else:
            scaled_flux = [1.0] * len(filtered_particles)
        
        # Create tricontourf plot with direct image alpha
        try:
            contour = ax.tricontourf(
                filtered_particles['X'], 
                filtered_particles['Y'], 
                scaled_flux,
                cmap='Greys_r',
                levels=levels,
                norm=plt.Normalize(0, 1),
                nchunk=2,
                alpha=self.config.direct_image_alpha
            )
        except Exception:
            # Fallback to scatter plot
            ax.scatter(filtered_particles['X'], filtered_particles['Y'],
                      c=scaled_flux, cmap='Greys_r', s=1, 
                      alpha=self.config.direct_image_alpha)
        
        return ax
    
    def _compose_ghost_image(self, ax: plt.Axes, particles: pd.DataFrame,
                           max_flux: float, min_flux: float,
                           black_hole_params: Dict[str, Any] = None,
                           **kwargs) -> plt.Axes:
        """
        Compose ghost image with coordinate transformation and edge handling.
        
        Extracted from luminet's ghost image composition with Y-coordinate flipping.
        """
        if particles.empty or 'X' not in particles.columns or 'Y' not in particles.columns:
            return ax
        
        # Split ghost particles into inner and outer regions
        inner_particles = self._filter_particles_by_disk_edge(
            particles, black_hole_params, 'inner', direct_image=False
        )
        outer_particles = self._filter_particles_by_disk_edge(
            particles, black_hole_params, 'outer', direct_image=False
        )
        
        power_scale = kwargs.get('power_scale', 0.9)
        levels = kwargs.get('levels', 100)
        
        # Render both inner and outer regions
        for i, region_particles in enumerate([inner_particles, outer_particles]):
            if region_particles.empty:
                continue
            
            # Sort by flux for proper layering
            if 'flux_o' in region_particles.columns:
                sorted_particles = region_particles.sort_values(by=['flux_o'], ascending=False)
                scaled_flux = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale 
                              for fl in sorted_particles['flux_o']]
            else:
                sorted_particles = region_particles
                scaled_flux = [1.0] * len(sorted_particles)
            
            # Apply Y-coordinate transformation for ghost image (luminet technique)
            y_coords = [-y for y in sorted_particles['Y']]
            
            try:
                ax.tricontourf(
                    sorted_particles['X'], 
                    y_coords,
                    scaled_flux,
                    cmap='Greys_r',
                    norm=plt.Normalize(0, 1),
                    levels=levels,
                    nchunk=2,
                    alpha=self.config.ghost_image_alpha,
                    zorder=1-i  # Layer ordering
                )
            except Exception:
                # Fallback to scatter plot
                ax.scatter(sorted_particles['X'], y_coords,
                          c=scaled_flux, cmap='Greys_r', s=1,
                          alpha=self.config.ghost_image_alpha)
        
        return ax
    
    def _filter_particles_by_disk_edge(self, particles: pd.DataFrame,
                                     black_hole_params: Dict[str, Any] = None,
                                     edge_type: str = 'outer',
                                     direct_image: bool = True) -> pd.DataFrame:
        """
        Filter particles based on disk edge boundaries.
        
        Implements luminet's edge filtering for proper image composition.
        """
        if particles.empty:
            return particles
        
        if not black_hole_params:
            return particles
        
        # Get edge function based on type
        if edge_type == 'outer':
            edge_func = black_hole_params.get('apparent_outer_edge_func')
            comparison = lambda b, edge: b <= edge
        else:  # inner
            edge_func = black_hole_params.get('apparent_inner_edge_func')
            comparison = lambda b, edge: b < edge
        
        if not edge_func or 'impact_parameter' not in particles.columns or 'angle' not in particles.columns:
            return particles
        
        # Apply angle offset for ghost images (luminet technique)
        angle_offset = 0 if direct_image else np.pi
        
        # Filter based on edge function
        mask = []
        for b, a in zip(particles['impact_parameter'], particles['angle']):
            edge_value = edge_func(a + angle_offset)
            mask.append(comparison(b, edge_value))
        
        return particles.iloc[mask] if any(mask) else pd.DataFrame()
    
    def _apply_composition_effects(self, ax: plt.Axes, 
                                 black_hole_params: Dict[str, Any] = None,
                                 **kwargs) -> plt.Axes:
        """
        Apply final composition effects including artifact filling.
        
        Implements luminet's artifact removal and edge enhancement techniques.
        """
        if not self.config.fill_artifacts or not black_hole_params:
            return ax
        
        # Fill inner disk edge with black (artifact removal)
        if 'inner_edge_coords' in black_hole_params:
            inner_x, inner_y = black_hole_params['inner_edge_coords']
            ax.fill_between(inner_x, inner_y, color='black', zorder=2)
        
        # Fill apparent edges for ghost image artifact removal
        if 'apparent_inner_edge_coords' in black_hole_params:
            x, y = black_hole_params['apparent_inner_edge_coords']
            ax.fill_between(x, y, color='black', zorder=1)
        
        if 'apparent_outer_edge_coords' in black_hole_params:
            x, y = black_hole_params['apparent_outer_edge_coords']
            ax.fill_between(x, y, color='black', zorder=0)
        
        return ax
    
    def apply_inclination_transformation(self, particles: pd.DataFrame,
                                       inclination: float = None) -> pd.DataFrame:
        """
        Apply inclination angle transformation to particle coordinates.
        
        Implements luminet's viewing perspective transformation.
        """
        if particles.empty:
            return particles
        
        inclination = inclination or self.config.inclination_angle
        inclination_rad = np.radians(inclination)
        
        # Create copy to avoid modifying original
        transformed = particles.copy()
        
        # Apply inclination transformation to Y coordinates
        if 'Y' in transformed.columns:
            transformed['Y'] = transformed['Y'] * np.cos(inclination_rad)
        
        # Apply transformation to angles if present
        if 'angle' in transformed.columns:
            # Adjust angles based on inclination
            transformed['angle'] = transformed['angle'] + inclination_rad
        
        return transformed
    
    def create_multi_inclination_composition(self, particles: pd.DataFrame,
                                           ghost_particles: pd.DataFrame = None,
                                           inclinations: List[float] = None,
                                           **kwargs) -> List[Tuple[plt.Figure, plt.Axes]]:
        """
        Create compositions at multiple inclination angles.
        
        Useful for creating animation sequences showing different viewing angles.
        """
        if inclinations is None:
            inclinations = [0, 30, 60, 80, 90]
        
        compositions = []
        
        for inclination in inclinations:
            # Transform particles for this inclination
            transformed_direct = self.apply_inclination_transformation(particles, inclination)
            transformed_ghost = None
            if ghost_particles is not None:
                transformed_ghost = self.apply_inclination_transformation(ghost_particles, inclination)
            
            # Update configuration
            original_inclination = self.config.inclination_angle
            self.config.inclination_angle = inclination
            
            # Create composition
            fig, ax = self.compose_images(
                transformed_direct, 
                transformed_ghost or pd.DataFrame(),
                **kwargs
            )
            
            # Add inclination info to title
            if kwargs.get('show_title', False):
                ax.set_title(f'Inclination = {inclination}°', color='white')
            
            compositions.append((fig, ax))
            
            # Restore original configuration
            self.config.inclination_angle = original_inclination
        
        return compositions
    
    def extract_disk_boundaries(self, black_hole_params: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Extract disk boundary coordinates for composition.
        
        Converts luminet's boundary functions to coordinate arrays.
        """
        boundaries = {}
        
        # Generate angle array for boundary calculation
        angles = np.linspace(0, 2*np.pi, 360)
        
        # Extract inner edge boundary
        if 'apparent_inner_edge_func' in black_hole_params:
            inner_func = black_hole_params['apparent_inner_edge_func']
            inner_radii = [inner_func(a) for a in angles]
            inner_x = [r * np.cos(a) for r, a in zip(inner_radii, angles)]
            inner_y = [r * np.sin(a) for r, a in zip(inner_radii, angles)]
            boundaries['inner_edge_coords'] = (inner_x, inner_y)
        
        # Extract outer edge boundary
        if 'apparent_outer_edge_func' in black_hole_params:
            outer_func = black_hole_params['apparent_outer_edge_func']
            outer_radii = [outer_func(a) for a in angles]
            outer_x = [r * np.cos(a) for r, a in zip(outer_radii, angles)]
            outer_y = [r * np.sin(a) for r, a in zip(outer_radii, angles)]
            boundaries['outer_edge_coords'] = (outer_x, outer_y)
        
        return boundaries


def create_luminet_compositor(config: CompositionConfig = None) -> LuminetCompositor:
    """Create a luminet compositor with optional configuration."""
    return LuminetCompositor(config)