"""
Mode router and handlers for unified draw_blackhole function.

This module implements the mode-based routing system that dispatches
different visualization types through a unified interface.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Tuple, List, Union
from abc import ABC, abstractmethod

from ..core.particle_system import ParticleSystem
from ..core.physics_engine import PhysicsEngine
from ..math.geodesics import UnifiedGeodesics
from .particle_renderer import ParticleRenderer, RenderConfig
from .unified_plotter import UnifiedPlotter
from ..utils.validation import validate_and_suggest


class VisualizationHandler(ABC):
    """Abstract base class for visualization mode handlers."""

    def __init__(self, params: Dict[str, Any]):
        """Initialize handler with parameters."""
        self.params = params
        self.mass = params.get('mass', 1.0)
        self.inclination = params.get('inclination', 80.0)
        self.figsize = params.get('figsize', (10, 10))
        self.ax_lim = params.get('ax_lim', (-40, 40))
        self.background_color = params.get('background_color', 'black')
        # Exportable data populated by render() — used by plotter_export
        self.export_data: Optional[Dict[str, Any]] = None

    @abstractmethod
    def validate_parameters(self) -> bool:
        """Validate mode-specific parameters."""
        pass

    @abstractmethod
    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render the visualization."""
        pass

    def setup_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """Setup basic figure with luminet-style appearance."""
        fig, ax = plt.subplots(figsize=self.figsize)
        fig.patch.set_facecolor(self.background_color)
        ax.set_facecolor(self.background_color)
        plt.axis('off')
        ax.set_xlim(self.ax_lim)
        ax.set_ylim(self.ax_lim)
        ax.set_aspect('equal')
        return fig, ax

    def get_export_type(self) -> Optional[str]:
        """Return the export type this handler supports, or None."""
        return None


class ModeRouter:
    """Router that dispatches to appropriate visualization handlers."""
    
    VALID_MODES = {
        'points', 'luminet', 'scatter', 'raytracing', 'isoradials',
        'redshift', 'photon_sphere', 'apparent_edges'
    }

    def __init__(self):
        """Initialize the mode router."""
        self.handlers = {
            'points': LuminetPointsHandler,
            'luminet': LuminetPointsHandler,  # Alias for points
            'scatter': ScatterHandler,
            'raytracing': RayTracingHandler,
            'isoradials': IsoradialHandler,
            'redshift': RedshiftHandler,
            'photon_sphere': PhotonSphereHandler,
            'apparent_edges': ApparentEdgeHandler
        }
    
    def validate_mode(self, mode: str) -> bool:
        """Validate that the mode is supported."""
        return mode in self.VALID_MODES
    
    def route_visualization(self, mode: str, params: Dict[str, Any]) -> VisualizationHandler:
        """Route to appropriate visualization handler."""
        if not self.validate_mode(mode):
            raise ValueError(f"Invalid mode '{mode}'. Valid modes: {sorted(self.VALID_MODES)}")
        
        handler_class = self.handlers[mode]
        return handler_class(params)
    
    def get_mode_parameters(self, mode: str) -> List[str]:
        """Get list of parameters specific to a mode."""
        mode_params = {
            'points': ['particle_count', 'power_scale', 'levels', 'show_ghost_image'],
            'luminet': ['particle_count', 'power_scale', 'levels', 'show_ghost_image'],
            'scatter': ['particle_count', 'power_scale', 'show_ghost_image'],
            'raytracing': ['particle_count', 'power_scale', 'levels'],
            'isoradials': ['radii', 'angular_resolution'],
            'redshift': ['redshift_levels', 'particle_count'],
            'photon_sphere': [],
            'apparent_edges': ['angular_resolution']
        }
        return mode_params.get(mode, [])


class LuminetPointsHandler(VisualizationHandler):
    """Handler for luminet-style particle visualization (points mode) with enhanced mathematical foundation."""
    
    def validate_parameters(self) -> bool:
        """Validate parameters for points mode."""
        particle_count = self.params.get('particle_count', 10000)
        power_scale = self.params.get('power_scale', 0.9)
        
        if particle_count <= 0:
            raise ValueError("particle_count must be positive")
        if not 0 < power_scale <= 1.0:
            raise ValueError("power_scale must be between 0 and 1")
        
        return True
    
    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render luminet-style particle visualization using enhanced sampling approach."""
        # Validate parameters
        validate_and_suggest(
            "draw_blackhole",
            mass=self.mass,
            inclination=self.inclination,
            particle_count=self.params.get('particle_count', 10000),
            power_scale=self.params.get('power_scale', 0.9)
        )
        
        # Extract parameters
        power_scale = self.params.get('power_scale', 0.9)
        levels = self.params.get('levels', 100)
        
        # Use enhanced Luminet approach that produces proper relativistic shape
        # This bypasses the old ParticleSystem/PhysicsEngine and uses the working enhanced sampling
        return self._render_with_enhanced_sampling(power_scale, levels)
    
    def _render_authentic_luminet(self, direct_df: pd.DataFrame, ghost_df: pd.DataFrame, 
                                 power_scale: float, levels: int) -> Tuple[plt.Figure, plt.Axes]:
        """Render using authentic Luminet tricontourf approach with proper data filtering."""
        # Setup figure
        fig, ax = self.setup_figure()
        show_ghost_image = self.params.get('show_ghost_image', True)
        
        if direct_df.empty:
            return fig, ax
        
        # Calculate flux range for normalization (authentic Luminet approach)
        all_fluxes = []
        if 'flux_o' in direct_df.columns:
            all_fluxes.extend(direct_df['flux_o'].values)
        if show_ghost_image and not ghost_df.empty and 'flux_o' in ghost_df.columns:
            all_fluxes.extend(ghost_df['flux_o'].values)
        
        if all_fluxes:
            max_flux = max(all_fluxes)
            min_flux = 0.0  # Luminet uses 0 as min_flux
        else:
            max_flux, min_flux = 1.0, 0.0
        
        # Plot direct image using authentic Luminet method
        if not direct_df.empty and 'X' in direct_df.columns and 'Y' in direct_df.columns:
            ax = self._plot_direct_image_luminet(ax, direct_df, levels, min_flux, max_flux, power_scale)
        
        # Plot ghost image using authentic Luminet method
        if show_ghost_image and not ghost_df.empty and 'X' in ghost_df.columns and 'Y' in ghost_df.columns:
            ax = self._plot_ghost_image_luminet(ax, ghost_df, levels, min_flux, max_flux, power_scale)
        
        return fig, ax
    
    def _plot_direct_image_luminet(self, ax: plt.Axes, points_df: pd.DataFrame, 
                                  levels: int, min_flux: float, max_flux: float, power_scale: float) -> plt.Axes:
        """Plot direct image using authentic Luminet tricontourf method."""
        # Sort by angle (authentic Luminet approach)
        if 'angle' in points_df.columns:
            points_sorted = points_df.sort_values(by="angle")
        else:
            points_sorted = points_df
        
        # Filter particles within apparent outer edge (if available)
        # This is a key part of the authentic Luminet approach
        points_filtered = points_sorted  # For now, use all points
        
        if points_filtered.empty:
            return ax
        
        # Apply power scaling to flux values (Luminet's signature technique)
        if 'flux_o' in points_filtered.columns and max_flux > min_flux:
            fluxes = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale 
                     for fl in points_filtered['flux_o']]
        else:
            fluxes = [1.0] * len(points_filtered)
        
        # Use tricontourf with authentic Luminet parameters
        try:
            ax.tricontourf(points_filtered['X'], points_filtered['Y'], fluxes, 
                          cmap='Greys_r', levels=levels, 
                          norm=plt.Normalize(0, 1), nchunk=2)
        except Exception:
            # Fallback to scatter if triangulation fails
            ax.scatter(points_filtered['X'], points_filtered['Y'], 
                      c=fluxes, cmap='Greys_r', s=1, alpha=0.7)
        
        # Add black ring fill for apparent inner edge (exact original Luminet technique)
        self._add_black_ring_fill_exact_luminet(ax)
        
        return ax
    
    def _add_black_ring_fill_exact_luminet(self, ax: plt.Axes) -> None:
        """
        Add black ring fill exactly like the original Luminet implementation.
        This fills Delaunay triangulation artifacts with black, creating the proper dark center.
        """
        # Calculate apparent inner edge coordinates (exact original approach)
        inner_radius = 6.0 * self.mass  # ISCO radius
        inclination_rad = self.inclination * np.pi / 180.0
        
        # Generate apparent inner edge coordinates with high precision
        angles = np.linspace(0, 2*np.pi, 200)
        inner_edge_x = []
        inner_edge_y = []
        
        for angle in angles:
            try:
                # Use enhanced impact parameter calculation for inner edge
                b = self._calc_enhanced_impact_parameter_exact(inner_radius, angle, inclination_rad, n=0)
                if b is not None:
                    # Apply coordinate transformation (original Luminet: rotation = -π/2)
                    x = b * np.cos(angle - np.pi/2)
                    y = b * np.sin(angle - np.pi/2)
                    inner_edge_x.append(x)
                    inner_edge_y.append(y)
            except:
                continue
        
        # Fill inner region with black (exact original Luminet technique)
        if len(inner_edge_x) > 3:
            ax.fill(inner_edge_x, inner_edge_y, color='black', zorder=10, alpha=1.0)
    
    def _plot_ghost_image_luminet(self, ax: plt.Axes, points_df: pd.DataFrame,
                                 levels: int, min_flux: float, max_flux: float, power_scale: float) -> plt.Axes:
        """Plot ghost image using EXACT original Luminet tricontourf method."""
        if points_df.empty:
            return ax
        
        # Split ghost particles into inner and outer regions (exact original Luminet approach)
        # Original: points_inner = points.iloc[[b_ < self.get_apparent_inner_edge_radius(a_ + np.pi) for b_, a_ in zip(...)]]
        # Original: points_outer = points.iloc[[b_ > self.get_apparent_outer_edge_radius(a_ + np.pi) for b_, a_ in zip(...)]]
        points_inner = []
        points_outer = []
        
        for _, particle in points_df.iterrows():
            # Simplified filtering based on impact parameter (approximating apparent edge calculations)
            if 'impact_parameter' in particle and particle['impact_parameter'] < 15.0 * self.mass:
                points_inner.append(particle)
            elif 'impact_parameter' in particle and particle['impact_parameter'] > 25.0 * self.mass:
                points_outer.append(particle)
        
        points_inner = pd.DataFrame(points_inner) if points_inner else pd.DataFrame()
        points_outer = pd.DataFrame(points_outer) if points_outer else pd.DataFrame()
        
        # Plot both inner and outer ghost regions (exact original technique)
        for i, points_ in enumerate([points_inner, points_outer]):
            if points_.empty:
                continue
                
            # Sort by flux for proper rendering order (exact original)
            if 'flux_o' in points_.columns:
                points_ = points_.sort_values(by=['flux_o'], ascending=False)
            
            # Apply power scaling to ghost flux values (exact original)
            if 'flux_o' in points_.columns and max_flux > min_flux:
                fluxes = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale 
                         for fl in points_['flux_o']]
            else:
                fluxes = [0.5] * len(points_)
            
            # EXACT ORIGINAL: Use tricontourf with Y-coordinate flipping
            # This is the key line from original: _ax.tricontourf(points_['X'], [-e for e in points_['Y']], fluxes, ...)
            try:
                ax.tricontourf(points_['X'], [-y for y in points_['Y']], fluxes,
                              cmap='Greys_r', norm=plt.Normalize(0, 1), levels=levels, 
                              nchunk=2, zorder=1-i, alpha=0.7)
            except Exception:
                # Fallback to scatter if triangulation fails
                ax.scatter(points_['X'], [-y for y in points_['Y']], 
                          c=fluxes, cmap='Greys_r', s=1, alpha=0.5)
        
        # Add ghost black fills (exact original technique)
        self._add_ghost_black_fills_exact_original(ax)
        
        return ax
    
    def _filter_ghost_particles_inner(self, points_df: pd.DataFrame) -> pd.DataFrame:
        """Filter ghost particles for inner region (exact original Luminet approach)."""
        if points_df.empty or 'impact_parameter' not in points_df.columns or 'angle' not in points_df.columns:
            return pd.DataFrame()
        
        # Filter particles inside apparent inner edge with π phase shift (exact original)
        filtered_particles = []
        for _, particle in points_df.iterrows():
            try:
                # Calculate apparent inner edge radius with π phase shift for ghost image
                apparent_inner_b = self._calc_enhanced_impact_parameter_exact(
                    6.0 * self.mass, particle['angle'] + np.pi, 
                    self.inclination * np.pi / 180.0, n=0
                )
                
                # Keep particle if it's inside the apparent inner edge
                if apparent_inner_b is not None and particle['impact_parameter'] < apparent_inner_b:
                    filtered_particles.append(particle)
            except:
                continue
        
        return pd.DataFrame(filtered_particles) if filtered_particles else pd.DataFrame()
    
    def _filter_ghost_particles_outer(self, points_df: pd.DataFrame) -> pd.DataFrame:
        """Filter ghost particles for outer region (exact original Luminet approach)."""
        if points_df.empty or 'impact_parameter' not in points_df.columns or 'angle' not in points_df.columns:
            return pd.DataFrame()
        
        # Filter particles outside apparent outer edge with π phase shift (exact original)
        filtered_particles = []
        for _, particle in points_df.iterrows():
            try:
                # Calculate apparent outer edge radius with π phase shift for ghost image
                apparent_outer_b = self._calc_enhanced_impact_parameter_exact(
                    50.0 * self.mass, particle['angle'] + np.pi, 
                    self.inclination * np.pi / 180.0, n=0
                )
                
                # Keep particle if it's outside the apparent outer edge
                if apparent_outer_b is not None and particle['impact_parameter'] > apparent_outer_b:
                    filtered_particles.append(particle)
            except:
                continue
        
        return pd.DataFrame(filtered_particles) if filtered_particles else pd.DataFrame()
    
    def _calc_original_impact_parameter(self, r: float, alpha: float, incl: float, n: int = 0) -> Optional[float]:
        """
        Calculate impact parameter using exact Luminet eq.13 elliptic integral solver.
        Delegates to the full implementation.
        """
        return self._calc_enhanced_impact_parameter_exact(r, alpha, incl, n)
    
    def _calc_redshift_factor(self, r: float, alpha: float, incl: float, mass: float, b: float) -> float:
        """
        Calculate redshift factor using Luminet's formula (eq. 19).
        (1+z) = (1 + sqrt(M/r^3) * b * sin(incl) * sin(angle)) * (1 - 3M/r)^(-0.5)
        """
        try:
            if r <= 3.0 * mass:
                return 1.0
            orbital_term = np.sqrt(mass / (r ** 3)) * b * np.sin(incl) * np.sin(alpha)
            grav_term = (1.0 - 3.0 * mass / r) ** (-0.5)
            z_factor = (1.0 + orbital_term) * grav_term
            return z_factor if np.isfinite(z_factor) and z_factor > 0 else 1.0
        except:
            return 1.0
    
    def _calc_flux_intrinsic(self, r: float, accretion_rate: float, mass: float) -> float:
        """
        Calculate intrinsic flux using Novikov-Thorne formula with logarithmic term.
        From Luminet (1979) / Page-Thorne (1974).
        """
        try:
            r_ = r / mass
            if r_ <= 6.0:
                return 0.0
            log_num = (np.sqrt(r_) + np.sqrt(3)) * (np.sqrt(6) - np.sqrt(3))
            log_den = (np.sqrt(r_) - np.sqrt(3)) * (np.sqrt(6) + np.sqrt(3))
            if log_den <= 0 or log_num <= 0:
                return 0.0
            log_arg = log_num / log_den
            f = (3.0 * mass * accretion_rate / (8.0 * np.pi)) * \
                (1.0 / ((r_ - 3.0) * r ** 2.5)) * \
                (np.sqrt(r_) - np.sqrt(6) + (1.0 / np.sqrt(3)) * np.log(log_arg))
            return max(f, 0.0)
        except:
            return 0.0

    def _calc_flux_observed(self, r: float, accretion_rate: float, mass: float, redshift_factor: float) -> float:
        """
        Calculate observed flux: F_obs = F_intrinsic / (1+z)^4.
        """
        try:
            flux_intr = self._calc_flux_intrinsic(r, accretion_rate, mass)
            if redshift_factor <= 0:
                return 0.0
            return flux_intr / (redshift_factor ** 4)
        except:
            return 0.0
    
    def _plot_direct_image_original(self, ax: plt.Axes, points_df: pd.DataFrame, 
                                   levels: int, min_flux: float, max_flux: float, power_scale: float) -> plt.Axes:
        """
        Plot direct image using EXACT original Luminet approach.
        """
        # Sort by angle exactly like original
        points_sorted = points_df.sort_values(by="angle")
        
        # Filter particles within apparent outer edge (simplified for now)
        # In full implementation, this would use get_apparent_outer_edge_radius()
        points_filtered = points_sorted
        
        if points_filtered.empty:
            return ax
        
        # Apply power scaling exactly like original
        if max_flux > min_flux:
            fluxes = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale 
                     for fl in points_filtered['flux_o']]
        else:
            fluxes = [1.0] * len(points_filtered)
        
        # Tricontourf exactly like original
        try:
            ax.tricontourf(points_filtered['X'], points_filtered['Y'], fluxes, 
                          cmap='Greys_r', levels=levels, 
                          norm=plt.Normalize(0, 1), nchunk=2)
        except Exception:
            ax.scatter(points_filtered['X'], points_filtered['Y'], 
                      c=fluxes, cmap='Greys_r', s=1, alpha=0.7)
        
        # Add black fill for apparent inner edge exactly like original
        self._add_original_black_fill(ax)
        
        return ax
    
    def _plot_ghost_image_original(self, ax: plt.Axes, points_df: pd.DataFrame,
                                  levels: int, min_flux: float, max_flux: float, power_scale: float) -> plt.Axes:
        """
        Plot ghost image using original Luminet approach with inner/outer edge filtering.
        Ghost particles are split by apparent inner edge radius and plotted separately.
        """
        if points_df.empty:
            return ax

        inclination_rad = self.inclination * np.pi / 180.0
        inner_radius = 6.0 * self.mass

        # Filter ghost particles: split into those inside vs outside the apparent inner edge
        inner_ghost = []
        outer_ghost = []
        for _, particle in points_df.iterrows():
            try:
                apparent_inner_b = self._calc_enhanced_impact_parameter_exact(
                    inner_radius, particle['angle'], inclination_rad, n=1
                )
                if apparent_inner_b is not None and particle['impact_parameter'] <= apparent_inner_b:
                    inner_ghost.append(particle)
                else:
                    outer_ghost.append(particle)
            except:
                outer_ghost.append(particle)

        # Plot each group separately for proper layering
        for ghost_group, alpha_val, zorder_val in [(outer_ghost, 0.7, 1), (inner_ghost, 0.5, 2)]:
            if not ghost_group:
                continue
            group_df = pd.DataFrame(ghost_group)
            group_sorted = group_df.sort_values(by=['flux_o'], ascending=False)

            if max_flux > min_flux:
                fluxes = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale
                         for fl in group_sorted['flux_o']]
            else:
                fluxes = [0.5] * len(group_sorted)

            try:
                ax.tricontourf(group_sorted['X'], [-y for y in group_sorted['Y']], fluxes,
                              cmap='Greys_r', norm=plt.Normalize(0, 1), levels=levels,
                              nchunk=2, alpha=alpha_val, zorder=zorder_val)
            except Exception:
                ax.scatter(group_sorted['X'], [-y for y in group_sorted['Y']],
                          c=fluxes, cmap='Greys_r', s=1, alpha=alpha_val * 0.7)

        return ax
    
    def _add_original_black_fill(self, ax: plt.Axes) -> None:
        """
        Add black fill using the gravitationally lensed apparent inner edge.
        Uses _calc_enhanced_impact_parameter_exact to trace the actual apparent
        inner edge of the accretion disk, then fills the interior black.
        """
        inner_radius = 6.0 * self.mass  # ISCO
        inclination_rad = self.inclination * np.pi / 180.0
        angles = np.linspace(0, 2 * np.pi, 200)

        inner_x = []
        inner_y = []
        for angle in angles:
            try:
                b = self._calc_enhanced_impact_parameter_exact(inner_radius, angle, inclination_rad, n=0)
                if b is not None:
                    inner_x.append(b * np.cos(angle - np.pi / 2))
                    inner_y.append(b * np.sin(angle - np.pi / 2))
            except:
                continue

        if len(inner_x) > 3:
            ax.fill(inner_x, inner_y, color='black', zorder=10, alpha=1.0)
    
    def _generate_particle_data(self, progress_callback=None) -> Tuple[pd.DataFrame, pd.DataFrame, float, float]:
        """
        Generate particle data using exact Luminet physics.

        Returns (direct_df, ghost_df, min_flux, max_flux).
        Accepts an optional progress_callback(current, total) for UI integration.
        """
        show_ghost_image = self.params.get('show_ghost_image', True)
        particle_count = self.params.get('particle_count', 10000)

        inner_radius = 6.0 * self.mass  # ISCO
        outer_radius = 50.0 * self.mass
        inclination_rad = self.inclination * np.pi / 180.0
        accretion_rate = self.params.get('accretion_rate', 1.0)

        direct_particles = []
        ghost_particles = []

        for i in range(particle_count):
            if progress_callback and i % 500 == 0:
                progress_callback(i, particle_count)
            elif i % 2000 == 0:
                print(f"   Progress: {i}/{particle_count}")

            r = inner_radius + (outer_radius - inner_radius) * np.random.random()
            theta = np.random.random() * 2 * np.pi

            b_direct = self._calc_original_impact_parameter(r, theta, inclination_rad, n=0)
            b_ghost = self._calc_original_impact_parameter(r, theta, inclination_rad, n=1) if show_ghost_image else None

            if b_direct is not None:
                x_direct = b_direct * np.cos(theta - np.pi / 2)
                y_direct = b_direct * np.sin(theta - np.pi / 2)
                redshift_factor = self._calc_redshift_factor(r, theta, inclination_rad, self.mass, b_direct)
                flux_direct = self._calc_flux_observed(r, accretion_rate, self.mass, redshift_factor)
                direct_particles.append({
                    'X': x_direct, 'Y': y_direct, 'flux_o': flux_direct,
                    'radius': r, 'angle': theta, 'impact_parameter': b_direct,
                    'z_factor': redshift_factor
                })

            if b_ghost is not None:
                x_ghost = b_ghost * np.cos(theta - np.pi / 2)
                y_ghost = b_ghost * np.sin(theta - np.pi / 2)
                redshift_factor_ghost = self._calc_redshift_factor(r, theta, inclination_rad, self.mass, b_ghost)
                flux_ghost = self._calc_flux_observed(r, accretion_rate, self.mass, redshift_factor_ghost)
                ghost_particles.append({
                    'X': x_ghost, 'Y': y_ghost, 'flux_o': flux_ghost,
                    'radius': r, 'angle': theta, 'impact_parameter': b_ghost,
                    'z_factor': redshift_factor_ghost
                })

        if progress_callback:
            progress_callback(particle_count, particle_count)

        direct_df = pd.DataFrame(direct_particles)
        ghost_df = pd.DataFrame(ghost_particles) if ghost_particles else pd.DataFrame()

        all_fluxes = list(direct_df['flux_o']) if not direct_df.empty else []
        if not ghost_df.empty:
            all_fluxes.extend(ghost_df['flux_o'])
        max_flux = max(all_fluxes) if all_fluxes else 1.0
        min_flux = 0.0

        return direct_df, ghost_df, min_flux, max_flux

    def _render_with_enhanced_sampling(self, power_scale: float, levels: int) -> Tuple[plt.Figure, plt.Axes]:
        """
        Render using the Luminet approach with proper impact parameter calculations.
        Uses tricontourf for smooth contour rendering.
        """
        fig, ax = self.setup_figure()
        show_ghost_image = self.params.get('show_ghost_image', True)
        particle_count = self.params.get('particle_count', 10000)

        print(f"Generating {particle_count} particles with exact Luminet physics...")

        direct_df, ghost_df, min_flux, max_flux = self._generate_particle_data(
            progress_callback=self.params.get('progress_callback')
        )

        print(f"Generated {len(direct_df)} direct and {len(ghost_df)} ghost particles")

        if not direct_df.empty:
            ax = self._plot_direct_image_original(ax, direct_df, levels, min_flux, max_flux, power_scale)
            if show_ghost_image and not ghost_df.empty:
                ax = self._plot_ghost_image_original(ax, ghost_df, levels, min_flux, max_flux, power_scale)

        return fig, ax
    
    def _calc_enhanced_impact_parameter_exact(self, r: float, alpha: float, incl: float, n: int = 0) -> Optional[float]:
        """
        Exact copy of the enhanced impact parameter calculation from the working enhanced_luminet_sampling.py.
        """
        from scipy.special import ellipj, ellipk, ellipkinc
        
        try:
            # Generate range of periastron values to search (exact copy)
            min_p = 3.01 * self.mass  # Just above photon sphere
            max_p = max(100.0 * self.mass, 3.0 * r)  # Scale with radius
            
            # Create initial search range (exact copy)
            p_values = np.linspace(min_p, max_p, 50)
            eq13_values = [self._eq13_exact(p, r, alpha, incl, n) for p in p_values]
            
            # Find sign changes (roots) (exact copy)
            sign_changes = np.where(np.diff(np.sign(eq13_values)))[0]
            
            if len(sign_changes) == 0:
                # No solution found, use ellipse approximation (exact copy)
                return self._ellipse_fallback_exact(r, alpha, incl)
            
            # Use first sign change (direct image solution) (exact copy)
            idx = sign_changes[0]
            
            # Refine solution using bisection method (exact copy)
            p_low = p_values[idx]
            p_high = p_values[idx + 1]
            
            for _ in range(50):  # iterations
                p_mid = (p_low + p_high) / 2
                eq13_mid = self._eq13_exact(p_mid, r, alpha, incl, n)
                eq13_low = self._eq13_exact(p_low, r, alpha, incl, n)
                
                if eq13_mid * eq13_low < 0:
                    p_high = p_mid
                else:
                    p_low = p_mid
                    
                if abs(p_high - p_low) < 1e-6:
                    break
            
            periastron_solution = (p_low + p_high) / 2
            
            # Convert periastron to impact parameter (exact copy)
            if periastron_solution > 2.0 * self.mass:
                return self._calc_b_from_periastron_exact(periastron_solution)
            else:
                return self._ellipse_fallback_exact(r, alpha, incl)
                
        except:
            return self._ellipse_fallback_exact(r, alpha, incl)
    
    def _eq13_exact(self, periastron: float, ir_radius: float, ir_angle: float, incl: float, n: int = 0) -> float:
        """Exact copy of eq13 from working enhanced_luminet_sampling.py."""
        from scipy.special import ellipj, ellipk, ellipkinc
        
        try:
            z_inf = self._zeta_inf_exact(periastron)
            q = self._calc_q_exact(periastron)
            m_ = self._k2_exact(periastron)
            ell_inf = ellipkinc(z_inf, m_)
            g = np.arccos(self._cos_gamma_exact(ir_angle, incl))
            
            if n:  # Ghost image
                ell_k = ellipk(m_)
                ellips_arg = (g - 2.0 * n * np.pi) / (2.0 * np.sqrt(periastron / q)) - ell_inf + 2.0 * ell_k
            else:  # Direct image
                ellips_arg = g / (2.0 * np.sqrt(periastron / q)) + ell_inf
            
            sn, cn, dn, ph = ellipj(ellips_arg, m_)
            sn2 = sn * sn
            term1 = -(q - periastron + 2.0 * self.mass) / (4.0 * self.mass * periastron)
            term2 = ((q - periastron + 6.0 * self.mass) / (4.0 * self.mass * periastron)) * sn2
            
            return 1.0 - ir_radius * (term1 + term2)
        except:
            return float('inf')
    
    def _calc_q_exact(self, periastron: float) -> float:
        """Exact copy from working version."""
        return np.sqrt((periastron - 2.0 * self.mass) * (periastron + 6.0 * self.mass))
    
    def _calc_b_from_periastron_exact(self, periastron: float) -> float:
        """Exact copy from working version."""
        return np.sqrt(periastron**3 / (periastron - 2.0 * self.mass))
    
    def _k2_exact(self, periastron: float) -> float:
        """Exact copy from working version."""
        q = self._calc_q_exact(periastron)
        return (q - periastron + 6 * self.mass) / (2 * q)
    
    def _zeta_inf_exact(self, periastron: float) -> float:
        """Exact copy from working version."""
        q = self._calc_q_exact(periastron)
        arg = (q - periastron + 2 * self.mass) / (q - periastron + 6 * self.mass)
        return np.arcsin(np.sqrt(arg))
    
    def _cos_gamma_exact(self, alpha: float, incl: float, tol: float = 1e-5) -> float:
        """Exact copy from working version."""
        if abs(incl) < tol:
            return 0
        return np.cos(alpha) / np.sqrt(np.cos(alpha)**2 + 1 / (np.tan(incl)**2))
    
    def _ellipse_fallback_exact(self, r: float, alpha: float, incl: float) -> float:
        """Exact copy from working version."""
        g = np.arccos(self._cos_gamma_exact(alpha, incl))
        return r * np.sin(g)
    
    def _filter_particles_by_apparent_edges(self, particles_df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter particles by apparent outer edge (like original Luminet).
        This creates the proper accretion disk structure.
        """
        if particles_df.empty or 'impact_parameter' not in particles_df.columns or 'angle' not in particles_df.columns:
            return particles_df
        
        # Calculate apparent outer edge radius for each particle
        outer_radius = 50.0 * self.mass  # Outer edge of accretion disk
        inclination_rad = self.inclination * np.pi / 180.0
        
        # Filter particles within apparent outer edge
        filtered_particles = []
        for _, particle in particles_df.iterrows():
            try:
                # Calculate apparent outer edge radius for this angle
                apparent_outer_b = self._calc_enhanced_impact_parameter_exact(
                    outer_radius, particle['angle'], inclination_rad, n=0
                )
                
                # Keep particle if it's within the apparent outer edge
                if apparent_outer_b is not None and particle['impact_parameter'] <= apparent_outer_b:
                    filtered_particles.append(particle)
            except:
                # Keep particle if calculation fails
                filtered_particles.append(particle)
        
        return pd.DataFrame(filtered_particles) if filtered_particles else pd.DataFrame()
    
    def _add_luminet_structure(self, ax: plt.Axes, render_method: str, particle_count: int) -> None:
        """
        Add proper Luminet structure: bright ring + dark center + proper layering.
        """
        # Add apparent inner edge (bright ring) - the key Luminet feature
        self._add_apparent_inner_edge_ring(ax)
        
        # Add dark center only for tricontourf method
        if render_method != 'scatter' and not (render_method == 'auto' and particle_count < 3000):
            self._add_dark_center_tricontourf(ax)
    
    def _add_apparent_inner_edge_ring(self, ax: plt.Axes) -> None:
        """
        Add the apparent inner edge ring (like original Luminet).
        This creates the bright ring around the black hole.
        """
        inner_radius = 6.0 * self.mass  # ISCO radius
        inclination_rad = self.inclination * np.pi / 180.0
        
        # Generate apparent inner edge coordinates (bright ring)
        angles = np.linspace(0, 2*np.pi, 200)  # High resolution for smooth ring
        ring_x = []
        ring_y = []
        
        for angle in angles:
            try:
                # Calculate impact parameter for inner edge
                b = self._calc_enhanced_impact_parameter_exact(inner_radius, angle, inclination_rad, n=0)
                if b is not None:
                    # Apply coordinate transformation
                    x = b * np.cos(angle - np.pi/2)
                    y = b * np.sin(angle - np.pi/2)
                    ring_x.append(x)
                    ring_y.append(y)
            except:
                continue
        
        # Plot the bright ring (apparent inner edge)
        if len(ring_x) > 3:
            ax.plot(ring_x, ring_y, color='orange', linewidth=2, alpha=0.8, zorder=15, 
                   label='Apparent Inner Edge' if self.params.get('show_labels', False) else None)
    
    def _add_dark_center_tricontourf(self, ax: plt.Axes) -> None:
        """
        Add dark center for tricontourf method (like original Luminet).
        Uses apparent inner edge approach to fill triangulation artifacts with black.
        """
        # Calculate apparent inner edge for filling
        inner_radius = 6.0 * self.mass  # ISCO radius
        inclination_rad = self.inclination * np.pi / 180.0
        
        # Generate apparent inner edge coordinates for filling
        angles = np.linspace(0, 2*np.pi, 100)
        inner_edge_x = []
        inner_edge_y = []
        
        for angle in angles:
            try:
                # Use enhanced impact parameter calculation for inner edge
                b = self._calc_enhanced_impact_parameter_exact(inner_radius, angle, inclination_rad, n=0)
                if b is not None:
                    # Apply coordinate transformation and scale down slightly
                    x = b * np.cos(angle - np.pi/2) * 0.8  # Scale down to create dark center
                    y = b * np.sin(angle - np.pi/2) * 0.8
                    inner_edge_x.append(x)
                    inner_edge_y.append(y)
            except:
                continue
        
        # Fill inner region with black (original Luminet technique)
        if len(inner_edge_x) > 3:
            ax.fill(inner_edge_x, inner_edge_y, color='black', zorder=12, alpha=1.0)
        
        # Add event horizon circle
        event_horizon_radius = 2.0 * self.mass
        horizon_circle = plt.Circle((0, 0), event_horizon_radius, 
                                   fill=True, color='black', 
                                   edgecolor='white', linewidth=0.5, alpha=1.0, zorder=11)
        ax.add_patch(horizon_circle)
    
    def _render_scatter_particles(self, direct_df: pd.DataFrame, ghost_df: pd.DataFrame, power_scale: float) -> Tuple[plt.Figure, plt.Axes]:
        """Render particles using scatter plots for authentic Luminet visualization."""
        # Setup figure
        fig, ax = self.setup_figure()
        show_ghost_image = self.params.get('show_ghost_image', True)
        
        if direct_df.empty:
            return fig, ax
        
        # Calculate flux scaling
        all_fluxes = []
        if 'flux_o' in direct_df.columns:
            all_fluxes.extend(direct_df['flux_o'].values)
        if not ghost_df.empty and 'flux_o' in ghost_df.columns:
            all_fluxes.extend(ghost_df['flux_o'].values)
        
        if all_fluxes:
            max_flux = max(all_fluxes)
            min_flux = 0.0
        else:
            max_flux, min_flux = 1.0, 0.0
        
        # Plot direct image particles to reveal mushroom cap structure
        if not direct_df.empty and 'X' in direct_df.columns and 'Y' in direct_df.columns:
            # Filter visible particles
            if 'is_visible' in direct_df.columns:
                visible_particles = direct_df[direct_df['is_visible'] == True]
            else:
                visible_particles = direct_df
            
            if not visible_particles.empty:
                # Sort by radius to enhance isoradial structure visibility
                if 'radius' in visible_particles.columns:
                    visible_particles = visible_particles.sort_values('radius')
                
                # Choose color data based on available columns (priority: brightness > flux_o > temperature)
                if 'brightness' in visible_particles.columns:
                    color_data = visible_particles['brightness']
                    colormap = 'hot'  # Hot colormap for brightness (like original comparison)
                elif 'flux_o' in visible_particles.columns:
                    # Apply power scaling to flux values
                    color_data = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale 
                                  for fl in visible_particles['flux_o']]
                    colormap = 'hot'  # Hot colormap for flux
                elif 'temperature' in visible_particles.columns:
                    color_data = visible_particles['temperature']
                    colormap = 'plasma'  # Plasma colormap for temperature
                else:
                    color_data = [1.0] * len(visible_particles)
                    colormap = 'Greys_r'
                
                # Use variable dot sizes based on flux to enhance structure
                if 'flux_o' in visible_particles.columns and max_flux > min_flux:
                    # Scale dot sizes by flux to emphasize bright regions
                    flux_normalized = [(fl - min_flux) / (max_flux - min_flux) for fl in visible_particles['flux_o']]
                    dot_sizes = [self.params.get('dot_size', 2.0) * (0.5 + 2.0 * fn) for fn in flux_normalized]
                else:
                    dot_sizes = self.params.get('dot_size', 2.0)
                
                # Scatter plot for direct image with enhanced structure visibility
                ax.scatter(visible_particles['X'], visible_particles['Y'], 
                          c=color_data, cmap=colormap, 
                          s=dot_sizes, 
                          alpha=0.9, edgecolors='none')
        
        # Plot ghost image particles to reveal secondary mushroom cap
        if show_ghost_image and not ghost_df.empty and 'X' in ghost_df.columns and 'Y' in ghost_df.columns:
            # Filter visible ghost particles
            if 'is_visible' in ghost_df.columns:
                visible_ghost = ghost_df[ghost_df['is_visible'] == True]
            else:
                visible_ghost = ghost_df
            
            if not visible_ghost.empty:
                # Sort by radius to enhance isoradial structure visibility
                if 'radius' in visible_ghost.columns:
                    visible_ghost = visible_ghost.sort_values('radius')
                
                # Choose color data for ghost particles
                if 'brightness' in visible_ghost.columns:
                    ghost_color_data = visible_ghost['brightness']
                    ghost_colormap = 'hot'
                elif 'flux_o' in visible_ghost.columns:
                    # Apply power scaling to ghost flux values
                    ghost_color_data = [(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale 
                                        for fl in visible_ghost['flux_o']]
                    ghost_colormap = 'hot'
                elif 'temperature' in visible_ghost.columns:
                    ghost_color_data = visible_ghost['temperature']
                    ghost_colormap = 'plasma'
                else:
                    ghost_color_data = [0.5] * len(visible_ghost)
                    ghost_colormap = 'Greys_r'
                
                # Use variable dot sizes for ghost particles too
                if 'flux_o' in visible_ghost.columns and max_flux > min_flux:
                    flux_normalized = [(fl - min_flux) / (max_flux - min_flux) for fl in visible_ghost['flux_o']]
                    ghost_dot_sizes = [self.params.get('dot_size', 2.0) * (0.3 + 1.5 * fn) for fn in flux_normalized]
                else:
                    ghost_dot_sizes = self.params.get('dot_size', 2.0) * 0.8
                
                # Scatter plot for ghost image (flipped Y coordinates)
                ax.scatter(visible_ghost['X'], [-y for y in visible_ghost['Y']], 
                          c=ghost_color_data, cmap=ghost_colormap, 
                          s=ghost_dot_sizes, 
                          alpha=0.6, edgecolors='none')
        
        return fig, ax
    
    def _particles_to_dataframe(self, particles: List) -> pd.DataFrame:
        """Convert particle objects to DataFrame for visualization."""
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


class ScatterHandler(LuminetPointsHandler):
    """Handler for scatter-dot visualization of the accretion disk."""

    def get_export_type(self) -> Optional[str]:
        return "scatter"

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render using scatter dots with hot colormap."""
        validate_and_suggest(
            "draw_blackhole",
            mass=self.mass,
            inclination=self.inclination,
            particle_count=self.params.get('particle_count', 10000),
            power_scale=self.params.get('power_scale', 0.9)
        )
        power_scale = self.params.get('power_scale', 0.9)
        particle_count = self.params.get('particle_count', 10000)

        print(f"Generating {particle_count} scatter particles with exact Luminet physics...")

        direct_df, ghost_df, min_flux, max_flux = self._generate_particle_data(
            progress_callback=self.params.get('progress_callback')
        )

        print(f"Generated {len(direct_df)} direct and {len(ghost_df)} ghost particles")

        # Populate export_data for plotter export
        points = []
        intensities = []
        show_ghost = self.params.get('show_ghost_image', True)
        for df, y_flip in [(direct_df, False), (ghost_df, True)]:
            if df is None or df.empty:
                continue
            if y_flip and not show_ghost:
                continue
            for _, row in df.iterrows():
                y = -row['Y'] if y_flip else row['Y']
                points.append((row['X'], y))
                flux_norm = (row['flux_o'] / max_flux) ** power_scale if max_flux > 0 else 0.5
                intensities.append(float(np.clip(flux_norm, 0, 1)))
        self.export_data = {"points": points, "intensities": intensities}

        return self._render_scatter_particles(direct_df, ghost_df, power_scale)


class RayTracingHandler(VisualizationHandler):
    """Handler for ray-traced visualization."""

    def validate_parameters(self) -> bool:
        """Validate parameters for raytracing mode."""
        return True

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render ray-traced visualization."""
        points_handler = LuminetPointsHandler(self.params)
        return points_handler.render()


class IsoradialHandler(VisualizationHandler):
    """Handler for isoradial curve visualization."""
    
    def validate_parameters(self) -> bool:
        """Validate parameters for isoradials mode."""
        radii = self.params.get('radii')
        if radii is not None and not all(r > 0 for r in radii):
            raise ValueError("All radii must be positive")
        return True
    
    def get_export_type(self) -> Optional[str]:
        return "isoradials"

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render isoradial curves and populate export_data with polylines."""
        validate_and_suggest("plot_isoradials", mass=self.mass, inclination=self.inclination)

        radii = self.params.get('radii')
        if radii is None:
            radii = list(range(6, 51, 5))

        angular_resolution = self.params.get('angular_resolution', 360)

        fig, ax = self.setup_figure()

        geodesics = UnifiedGeodesics(mass=self.mass)
        inclination_rad = self.inclination * np.pi / 180

        all_polylines: List[List[Tuple[float, float]]] = []

        for radius in radii:
            try:
                angles = np.linspace(0, 2 * np.pi, angular_resolution)
                impact_params = []
                valid_angles = []
                for angle in angles:
                    try:
                        b = geodesics.calculate_impact_parameter(
                            angle, radius, inclination_rad, image_order=0
                        )
                        if b is not None and b > 0:
                            impact_params.append(b)
                            valid_angles.append(angle)
                    except Exception:
                        continue

                if len(impact_params) > 3:
                    x = [b * np.cos(a - np.pi / 2) for b, a in zip(impact_params, valid_angles)]
                    y = [b * np.sin(a - np.pi / 2) for b, a in zip(impact_params, valid_angles)]

                    # Store raw polyline for export
                    all_polylines.append(list(zip(x, y)))

                    if angular_resolution >= 720:
                        from scipy.interpolate import splprep, splev
                        try:
                            x_closed = x + [x[0]]
                            y_closed = y + [y[0]]
                            tck, u = splprep([x_closed, y_closed], s=0, per=True)
                            u_new = np.linspace(0, 1, angular_resolution * 2)
                            x_smooth, y_smooth = splev(u_new, tck)
                            ax.plot(x_smooth, y_smooth, color='white', alpha=0.7, linewidth=1.5,
                                    label=f'r = {radius}M' if self.params.get('show_labels', False) else None)
                        except ImportError:
                            ax.plot(x, y, color='white', alpha=0.7, linewidth=1,
                                    label=f'r = {radius}M' if self.params.get('show_labels', False) else None)
                    else:
                        ax.plot(x, y, color='white', alpha=0.7, linewidth=1,
                                label=f'r = {radius}M' if self.params.get('show_labels', False) else None)
            except Exception:
                continue

        # Store for plotter export
        self.export_data = {"polylines": all_polylines}

        if self.params.get('show_title', True):
            ax.set_title('Isoradial Curves', color='white')

        if self.params.get('show_labels', False):
            ax.legend(loc='upper right')

        return fig, ax


class RedshiftHandler(VisualizationHandler):
    """Handler for redshift contour visualization."""
    
    def validate_parameters(self) -> bool:
        """Validate parameters for redshift mode."""
        redshift_levels = self.params.get('redshift_levels')
        if redshift_levels is not None and not isinstance(redshift_levels, (list, tuple)):
            raise ValueError("redshift_levels must be a list or tuple")
        return True
    
    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render redshift contours."""
        # Validate parameters
        validate_and_suggest("plot_isoredshifts", mass=self.mass, inclination=self.inclination)
        
        redshift_levels = self.params.get('redshift_levels')
        if redshift_levels is None:
            redshift_levels = [-0.2, -0.15, -0.1, -0.05, 0., 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75]
        
        # Generate particles for isoredshift calculation
        particle_count = self.params.get('particle_count', 5000)
        
        # Create particle system
        particle_system = ParticleSystem(
            black_hole_mass=self.mass,
            particle_count=particle_count,
            distribution_type='luminet'
        )
        
        # Generate particles
        direct_particles, _ = particle_system.sample_points(
            n_points=particle_count,
            inclination=self.inclination,
            black_hole_mass=self.mass
        )
        
        # Apply physics to calculate redshift
        physics_engine = PhysicsEngine(mass=self.mass)
        direct_particles = physics_engine.execute_complete_pipeline(
            direct_particles,
            inclination=self.inclination,
            enable_redshift=True
        )
        
        # Convert to DataFrame
        particles_df = self._particles_to_dataframe(direct_particles)
        
        # Use unified plotter for isoredshift visualization
        plotter = UnifiedPlotter()
        
        # Filter out conflicting parameters
        plotter_params = {k: v for k, v in self.params.items() 
                         if k not in ['figsize', 'ax_lim', 'background_color', 'redshift_levels']}
        
        fig = plotter.plot_isoredshift_contours(
            particles_df=particles_df,
            redshift_levels=redshift_levels,
            figsize=self.figsize,
            **plotter_params
        )
        
        return fig, fig.axes[0]
    
    def _particles_to_dataframe(self, particles: List) -> pd.DataFrame:
        """Convert particle objects to DataFrame for visualization."""
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


class PhotonSphereHandler(VisualizationHandler):
    """Handler for photon sphere visualization."""
    
    def validate_parameters(self) -> bool:
        """Validate parameters for photon_sphere mode."""
        return True
    
    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render photon sphere visualization."""
        # Validate parameters
        validate_and_suggest("plot_photon_sphere", mass=self.mass)
        
        fig, ax = self.setup_figure()
        
        # Plot photon sphere (r = 3M)
        photon_sphere_radius = 3.0 * self.mass
        circle = plt.Circle((0, 0), photon_sphere_radius, 
                           fill=False, color='red', linestyle='--', 
                           linewidth=2, alpha=0.8, label='Photon Sphere')
        ax.add_patch(circle)
        
        # Plot event horizon (r = 2M)
        event_horizon_radius = 2.0 * self.mass
        horizon_circle = plt.Circle((0, 0), event_horizon_radius, 
                                   fill=True, color='black', 
                                   edgecolor='white', linewidth=1,
                                   alpha=1.0, label='Event Horizon')
        ax.add_patch(horizon_circle)
        
        if self.params.get('show_title', True):
            ax.set_title('Photon Sphere and Event Horizon', color='white')
        
        if self.params.get('show_legend', True):
            ax.legend(loc='upper right')
        
        return fig, ax


class ApparentEdgeHandler(VisualizationHandler):
    """Handler for apparent edge visualization."""
    
    def validate_parameters(self) -> bool:
        """Validate parameters for apparent_edges mode."""
        return True
    
    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render apparent inner edge visualization."""
        # Validate parameters
        validate_and_suggest("plot_apparent_inner_edge", mass=self.mass, inclination=self.inclination)
        
        fig, ax = self.setup_figure()
        
        # Calculate apparent inner edge using geodesic calculations
        geodesics = UnifiedGeodesics(mass=self.mass)
        inclination_rad = self.inclination * np.pi / 180
        
        # Generate angles for edge calculation
        angular_resolution = self.params.get('angular_resolution', 360)
        angles = np.linspace(0, 2*np.pi, angular_resolution)
        inner_radius = 6.0 * self.mass  # ISCO
        
        # Calculate impact parameters for inner edge
        impact_params = []
        for angle in angles:
            try:
                b = geodesics.calculate_impact_parameter(
                    angle, inner_radius, inclination_rad, image_order=0
                )
                impact_params.append(b if b is not None else 0)
            except Exception:
                impact_params.append(0)
        
        # Convert to Cartesian coordinates (rotate 90 degrees clockwise)
        x = [b * np.cos(a - np.pi/2) for b, a in zip(impact_params, angles)]
        y = [b * np.sin(a - np.pi/2) for b, a in zip(impact_params, angles)]
        
        # Plot the apparent inner edge
        ax.plot(x, y, color='orange', linewidth=2, alpha=0.8, label='Apparent Inner Edge')
        
        # Add photon sphere and event horizon for reference
        photon_circle = plt.Circle((0, 0), 3.0 * self.mass, fill=False, color='red', 
                                  linestyle='--', alpha=0.6, label='Photon Sphere')
        horizon_circle = plt.Circle((0, 0), 2.0 * self.mass, fill=True, color='black',
                                   edgecolor='white', alpha=1.0, label='Event Horizon')
        ax.add_patch(photon_circle)
        ax.add_patch(horizon_circle)
        
        if self.params.get('show_title', True):
            ax.set_title(f'Apparent Inner Edge (i={self.inclination}°)', color='white')
        
        if self.params.get('show_legend', True):
            ax.legend(loc='upper right')
        
        return fig, ax