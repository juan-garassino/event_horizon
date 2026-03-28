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
        """Plot direct image — delegates to _plot_direct_image_original which has the correct logic."""
        return self._plot_direct_image_original(ax, points_df, levels, min_flux, max_flux, power_scale)
    
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
        """Plot ghost image — delegates to _plot_ghost_image_original which has the correct logic."""
        return self._plot_ghost_image_original(ax, points_df, levels, min_flux, max_flux, power_scale)
    
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
    
    def _compute_apparent_edge_b(self, r_edge: float, angles: np.ndarray) -> np.ndarray:
        """
        Vectorized computation of apparent edge impact parameters b(angle) for a given radius.
        Returns array of b values (NaN where computation fails).
        """
        inclination_rad = self.inclination * np.pi / 180.0

        # Try Cython table (fastest)
        try:
            from ..math._fast_geodesics_cy import cy_build_impact_table
            table, alpha_g, r_g = cy_build_impact_table(
                self.mass, inclination_rad, n=0,
                n_alpha=len(angles), n_r=1,
                r_min=r_edge, r_max=r_edge,
            )
            b_arr = table[:, 0]
            return b_arr
        except ImportError:
            pass

        # Try vectorized geodesics
        try:
            from ..math.geodesics import impact_parameter, lambda_objective
            obj_func = lambda_objective()
            b_arr = impact_parameter(angles, r_edge, inclination_rad, 0, self.mass,
                                     objective_func=obj_func)
            return b_arr
        except Exception:
            pass

        # Fallback: per-angle solver
        b_arr = np.full(len(angles), np.nan)
        for i, angle in enumerate(angles):
            try:
                b = self._calc_enhanced_impact_parameter_exact(r_edge, angle, inclination_rad, n=0)
                if b is not None:
                    b_arr[i] = b
            except:
                continue
        return b_arr

    def _plot_direct_image_original(self, ax: plt.Axes, points_df: pd.DataFrame,
                                   levels: int, min_flux: float, max_flux: float, power_scale: float) -> plt.Axes:
        """
        Plot direct image matching reference: tricontourf + inner disk edge black fill (zorder=1).
        """
        # Sort by angle like reference
        points_sorted = points_df.sort_values(by="angle")
        points_filtered = points_sorted

        if points_filtered.empty:
            return ax

        # Power-scale flux like reference
        if max_flux > min_flux:
            fluxes = ((points_filtered['flux_o'].abs() + min_flux) / (max_flux + min_flux)).values ** power_scale
        else:
            fluxes = np.ones(len(points_filtered))

        # tricontourf (no explicit zorder = default 0, like reference)
        try:
            ax.tricontourf(points_filtered['X'].values, points_filtered['Y'].values, fluxes,
                          cmap='Greys_r', levels=levels,
                          norm=plt.Normalize(0, 1), nchunk=2)
        except Exception:
            ax.scatter(points_filtered['X'], points_filtered['Y'],
                      c=fluxes, cmap='Greys_r', s=1, alpha=0.7)

        # Black fill for apparent inner disk edge (zorder=1, like reference)
        self._add_inner_disk_edge_fill(ax, zorder=1)

        return ax
    
    def _plot_ghost_image_original(self, ax: plt.Axes, points_df: pd.DataFrame,
                                  levels: int, min_flux: float, max_flux: float, power_scale: float) -> plt.Axes:
        """
        Plot ghost image matching reference: split into inner/outer by apparent edges,
        render at different zorders, add two black fills.
        """
        if points_df.empty:
            return ax

        # --- Split ghost particles into inner and outer (like reference) ---
        # Reference: points_inner = b < apparent_inner_edge_radius(angle + pi)
        #            points_outer = b > apparent_outer_edge_radius(angle + pi)
        inner_radius = 6.0 * self.mass
        outer_radius = 50.0 * self.mass

        # Compute apparent edge b-values for all unique angles (vectorized)
        angles = points_df['angle'].values
        b_vals = points_df['impact_parameter'].values

        # Build lookup: apparent edges at angle+π (the ghost sees the back of the disk)
        unique_angles = np.unique(angles)
        shifted_angles = np.mod(unique_angles + np.pi, 2 * np.pi)

        inner_edge_b = self._compute_apparent_edge_b(inner_radius, shifted_angles)
        outer_edge_b = self._compute_apparent_edge_b(outer_radius, shifted_angles)

        # Map each particle's angle to its edge b-value
        angle_to_inner = dict(zip(unique_angles, inner_edge_b))
        angle_to_outer = dict(zip(unique_angles, outer_edge_b))

        inner_edge_per_particle = np.array([angle_to_inner.get(a, np.nan) for a in angles])
        outer_edge_per_particle = np.array([angle_to_outer.get(a, np.nan) for a in angles])

        mask_inner = b_vals < inner_edge_per_particle
        mask_outer = b_vals > outer_edge_per_particle

        points_inner = points_df[mask_inner]
        points_outer = points_df[mask_outer]

        # --- Render inner (zorder=1) and outer (zorder=0) like reference ---
        for i, points_ in enumerate([points_inner, points_outer]):
            if points_.empty:
                continue

            points_ = points_.sort_values(by=['flux_o'], ascending=False)

            if max_flux > min_flux:
                fluxes = ((points_['flux_o'].abs() + min_flux) / (max_flux + min_flux)).values ** power_scale
            else:
                fluxes = np.full(len(points_), 0.5)

            try:
                ax.tricontourf(points_['X'].values, -points_['Y'].values, fluxes,
                              cmap='Greys_r', norm=plt.Normalize(0, 1), levels=levels,
                              nchunk=2, zorder=1 - i)
            except Exception:
                ax.scatter(points_['X'].values, -points_['Y'].values,
                          c=fluxes, cmap='Greys_r', s=1, alpha=0.4)

        # --- Ghost black fill: apparent inner edge (black hole silhouette) ---
        # Y-flipped to match ghost position, covers ghost triangulation artifacts
        self._add_apparent_inner_edge_fill(ax, zorder=1, y_flip=True)

        return ax
    
    def _add_original_black_fill(self, ax: plt.Axes) -> None:
        """
        Add black fill using the gravitationally lensed apparent inner edge.
        Traces the lensed ISCO boundary and fills the interior black.
        Uses the vectorized geodesics when available for speed.
        """
        inner_radius = 6.0 * self.mass  # ISCO
        inclination_rad = self.inclination * np.pi / 180.0
        n_angles = 400

        angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=True)

        # Try Cython-accelerated path first (fastest)
        try:
            from ..math._fast_geodesics_cy import cy_build_impact_table
            from scipy.interpolate import RegularGridInterpolator
            # Build a tiny 1-row table at r=inner_radius only
            table, alpha_g, r_g = cy_build_impact_table(
                self.mass, inclination_rad, n=0,
                n_alpha=n_angles, n_r=1,
                r_min=inner_radius, r_max=inner_radius,
            )
            b_arr = table[:, 0]
            inner_x = b_arr * np.cos(alpha_g - np.pi / 2)
            inner_y = b_arr * np.sin(alpha_g - np.pi / 2)
            valid = np.isfinite(inner_x) & np.isfinite(inner_y)
            if valid.sum() > 3:
                # Close the polygon
                xs = np.append(inner_x[valid], inner_x[valid][0])
                ys = np.append(inner_y[valid], inner_y[valid][0])
                ax.fill(xs, ys, color='black', zorder=10, alpha=1.0)
            return
        except ImportError:
            pass

        # Try vectorized geodesics path
        try:
            from ..math.geodesics import impact_parameter, lambda_objective
            obj_func = lambda_objective()
            b_arr = impact_parameter(angles, inner_radius, inclination_rad, 0, self.mass,
                                     objective_func=obj_func)
            inner_x = b_arr * np.cos(angles - np.pi / 2)
            inner_y = b_arr * np.sin(angles - np.pi / 2)
            valid = np.isfinite(inner_x) & np.isfinite(inner_y)
            if valid.sum() > 3:
                ax.fill(inner_x[valid], inner_y[valid], color='black', zorder=10, alpha=1.0)
            return
        except Exception:
            pass

        # Fallback: per-angle solver
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

    def _add_inner_disk_edge_fill(self, ax: plt.Axes, zorder: int = 1) -> None:
        """
        Black fill for apparent inner disk edge (direct image).
        Reference: calc_apparent_inner_disk_edge() + fill_between, zorder=1.
        """
        n_angles = 400
        angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=True)
        b_arr = self._compute_apparent_edge_b(6.0 * self.mass, angles)
        valid = np.isfinite(b_arr)
        if valid.sum() < 3:
            return
        x = b_arr[valid] * np.cos(angles[valid] - np.pi / 2) * 0.99  # scale slightly like reference
        y = b_arr[valid] * np.sin(angles[valid] - np.pi / 2) * 0.99
        ax.fill(np.append(x, x[0]), np.append(y, y[0]), color='black', zorder=zorder, alpha=1.0)

    def _add_apparent_inner_edge_fill(self, ax: plt.Axes, zorder: int = 1, y_flip: bool = False) -> None:
        """
        Black fill for apparent inner edge of the black hole (silhouette).
        Reference: apparent_inner_edge() + fill_between.
        This is the black hole silhouette — min(critical_b, inner_disk_edge_b).
        When y_flip=True, renders in the ghost (negative Y) region.
        """
        n_angles = 400
        angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=True)
        inner_b = self._compute_apparent_edge_b(6.0 * self.mass, angles)
        critical_b = np.sqrt(27.0) * self.mass  # 3√3 M for Schwarzschild

        # Reference logic: for back side (π/2 < α < 3π/2), use critical_b;
        # otherwise use min(critical_b, inner_disk_edge_b)
        b_arr = np.where(
            (angles > np.pi / 2) & (angles < 3 * np.pi / 2),
            critical_b * 0.99,
            np.minimum(critical_b, np.where(np.isfinite(inner_b), inner_b, critical_b)) * 0.99
        )

        x = b_arr * np.cos(angles - np.pi / 2)
        y = b_arr * np.sin(angles - np.pi / 2)
        if y_flip:
            y = -y
        ax.fill(np.append(x, x[0]), np.append(y, y[0]), color='black', zorder=zorder, alpha=1.0)

    def _add_outer_disk_edge_fill(self, ax: plt.Axes, zorder: int = 0) -> None:
        """
        Black fill for apparent outer disk edge (ghost image).
        Reference: calc_apparent_outer_disk_edge() + fill_between, zorder=0.
        """
        n_angles = 400
        angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=True)
        b_arr = self._compute_apparent_edge_b(50.0 * self.mass, angles)
        valid = np.isfinite(b_arr)
        if valid.sum() < 3:
            return
        x = b_arr[valid] * np.cos(angles[valid] - np.pi / 2)
        y = b_arr[valid] * np.sin(angles[valid] - np.pi / 2)
        ax.fill(np.append(x, x[0]), np.append(y, y[0]), color='black', zorder=zorder, alpha=1.0)

    def _add_scatter_black_fill(self, ax: plt.Axes) -> None:
        """
        Black fill for scatter mode — shrunk inward so the photon ring
        (ghost particles at the inner edge) shows around the top AND bottom.
        """
        n_angles = 400
        angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=True)
        b_arr = self._compute_apparent_edge_b(6.0 * self.mass, angles)
        valid = np.isfinite(b_arr)
        if valid.sum() < 3:
            return

        x = b_arr[valid] * np.cos(angles[valid] - np.pi / 2)
        y = b_arr[valid] * np.sin(angles[valid] - np.pi / 2)

        # Clip bottom at y=0 so ghost crescent below is not covered
        y_clipped = np.maximum(y, 0.0)

        xs = np.append(x, x[0])
        ys = np.append(y_clipped, y_clipped[0])
        # zorder=2: above ghost (1) but BELOW direct (3) so photon ring particles show
        ax.fill(xs, ys, color='black', zorder=2, alpha=1.0)

    def _add_photon_ring(self, ax: plt.Axes, colormap_name: str = 'hot', zorder: int = 11) -> None:
        """
        Draw the photon ring (apparent inner disk edge) as a bright line
        on top of the black fill. This is the lensed ISCO boundary.
        """
        n_angles = 400
        angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=True)
        b_arr = self._compute_apparent_edge_b(6.0 * self.mass, angles)
        valid = np.isfinite(b_arr)
        if valid.sum() < 3:
            return

        x = b_arr[valid] * np.cos(angles[valid] - np.pi / 2)
        y = b_arr[valid] * np.sin(angles[valid] - np.pi / 2)

        # Pick ring color based on palette
        if colormap_name in ('white', 'Greys_r', 'bone'):
            ring_color = 'white'
        elif colormap_name == 'hot':
            ring_color = '#FF6600'  # warm orange
        elif colormap_name in ('inferno', 'magma'):
            ring_color = '#FF8800'
        elif colormap_name == 'plasma':
            ring_color = '#CC44FF'
        elif colormap_name == 'viridis':
            ring_color = '#44DD88'
        elif colormap_name == 'cividis':
            ring_color = '#DDCC44'
        elif colormap_name == 'copper':
            ring_color = '#CC8844'
        else:
            ring_color = 'white'

        # Close the curve
        xs = np.append(x, x[0])
        ys = np.append(y, y[0])
        ax.plot(xs, ys, color=ring_color, linewidth=1.5, alpha=0.8, zorder=zorder)

    def _generate_particle_data(self, progress_callback=None) -> Tuple[pd.DataFrame, pd.DataFrame, float, float]:
        """
        Generate particle data using exact Luminet physics.

        Returns (direct_df, ghost_df, min_flux, max_flux).
        Accepts an optional progress_callback(current, total) for UI integration.

        Tries fast vectorized path first (lookup table + interpolation),
        falls back to per-particle bisection if unavailable.
        """
        show_ghost_image = self.params.get('show_ghost_image', True)
        particle_count = self.params.get('particle_count', 10000)
        inclination_rad = self.inclination * np.pi / 180.0
        accretion_rate = self.params.get('accretion_rate', 1.0)

        # --- Fast path: vectorized lookup table ---
        try:
            from ..math.fast_geodesics import generate_particles_fast, build_impact_table
            from scipy.interpolate import RegularGridInterpolator

            # Try Cython-accelerated table builder first
            table_direct = None
            table_ghost = None
            try:
                from ..math._fast_geodesics_cy import cy_build_impact_table

                def _cy_interp(mass, incl, n):
                    table, alpha_g, r_g = cy_build_impact_table(
                        mass, incl, n, n_alpha=200, n_r=100,
                    )
                    return RegularGridInterpolator(
                        (alpha_g, r_g), table,
                        method='linear', bounds_error=False, fill_value=np.nan,
                    )

                table_direct = _cy_interp(self.mass, inclination_rad, 0)
                table_ghost = _cy_interp(self.mass, inclination_rad, 1) if show_ghost_image else None
            except ImportError:
                pass  # Will use NumPy table builder in generate_particles_fast

            return generate_particles_fast(
                particle_count, self.mass, inclination_rad,
                accretion_rate=accretion_rate,
                ghost=show_ghost_image,
                table_direct=table_direct,
                table_ghost=table_ghost,
                progress_callback=progress_callback,
            )
        except ImportError:
            pass

        # --- Fallback: per-particle bisection loop ---
        return self._generate_particle_data_legacy(progress_callback)

    def _generate_particle_data_legacy(self, progress_callback=None) -> Tuple[pd.DataFrame, pd.DataFrame, float, float]:
        """Original per-particle bisection loop (fallback)."""
        show_ghost_image = self.params.get('show_ghost_image', True)
        particle_count = self.params.get('particle_count', 10000)
        inner_radius = 6.0 * self.mass
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
    
    # Available scatter colormaps
    SCATTER_COLORMAPS = {
        'hot': 'hot',
        'white': None,          # Pure white dots, alpha/size encode flux
        'Greys_r': 'Greys_r',  # White-to-black grayscale (Luminet style)
        'inferno': 'inferno',
        'magma': 'magma',
        'plasma': 'plasma',
        'viridis': 'viridis',
        'cividis': 'cividis',
        'copper': 'copper',
        'bone': 'bone',
    }

    def _render_scatter_particles(self, direct_df: pd.DataFrame, ghost_df: pd.DataFrame, power_scale: float) -> Tuple[plt.Figure, plt.Axes]:
        """Render particles using scatter plots for authentic Luminet visualization."""
        fig, ax = self.setup_figure()
        show_ghost_image = self.params.get('show_ghost_image', True)
        colormap_name = self.params.get('colormap', 'hot')
        dot_size = self.params.get('dot_size', 2.0)
        use_white = (colormap_name == 'white')
        cmap = None if use_white else self.SCATTER_COLORMAPS.get(colormap_name, colormap_name)

        if direct_df.empty:
            return fig, ax

        # Flux scaling
        all_fluxes = []
        if 'flux_o' in direct_df.columns:
            all_fluxes.extend(direct_df['flux_o'].values)
        if not ghost_df.empty and 'flux_o' in ghost_df.columns:
            all_fluxes.extend(ghost_df['flux_o'].values)
        max_flux = max(all_fluxes) if all_fluxes else 1.0
        min_flux = 0.0

        # --- Layer 1 (back): Ghost image ---
        if show_ghost_image and not ghost_df.empty and 'X' in ghost_df.columns:
            visible_ghost = ghost_df[ghost_df['is_visible'] == True] if 'is_visible' in ghost_df.columns else ghost_df
            if not visible_ghost.empty:
                g_flux_norm = ((visible_ghost['flux_o'].abs() + min_flux) / (max_flux + min_flux)).values ** power_scale if 'flux_o' in visible_ghost.columns else np.full(len(visible_ghost), 0.5)
                g_sizes = dot_size * (0.3 + 1.5 * np.clip(g_flux_norm, 0, 1))

                if use_white:
                    ax.scatter(visible_ghost['X'].values, -visible_ghost['Y'].values,
                              c='white', s=g_sizes, alpha=g_flux_norm * 0.5,
                              edgecolors='none', zorder=1)
                else:
                    ax.scatter(visible_ghost['X'].values, -visible_ghost['Y'].values,
                              c=g_flux_norm, cmap=cmap, s=g_sizes,
                              alpha=0.6, edgecolors='none', zorder=1)

        # --- Layer 2 (front): Direct image ---
        if not direct_df.empty and 'X' in direct_df.columns:
            visible = direct_df[direct_df['is_visible'] == True] if 'is_visible' in direct_df.columns else direct_df
            if not visible.empty:
                d_flux_norm = ((visible['flux_o'].abs() + min_flux) / (max_flux + min_flux)).values ** power_scale if 'flux_o' in visible.columns else np.ones(len(visible))
                d_sizes = dot_size * (0.5 + 2.0 * np.clip(d_flux_norm, 0, 1))

                if use_white:
                    ax.scatter(visible['X'].values, visible['Y'].values,
                              c='white', s=d_sizes, alpha=d_flux_norm * 0.9,
                              edgecolors='none', zorder=2)
                else:
                    ax.scatter(visible['X'].values, visible['Y'].values,
                              c=d_flux_norm, cmap=cmap, s=d_sizes,
                              alpha=0.9, edgecolors='none', zorder=2)

        return fig, ax

    def _add_scatter_photon_ring(self, ax, max_flux, min_flux, power_scale,
                                  colormap_name, dot_size, use_white, cmap):
        """Add dense particles at r≈6M to form the visible photon ring."""
        inclination_rad = self.inclination * np.pi / 180.0
        accretion_rate = self.params.get('accretion_rate', 1.0)
        n_ring = 500  # Dense sampling around the inner edge

        angles = np.linspace(0, 2 * np.pi, n_ring, endpoint=False)
        # Sample at r = 6.01M (just outside ISCO)
        r_ring = np.full(n_ring, 6.01 * self.mass)

        b_arr = self._compute_apparent_edge_b(6.01 * self.mass, angles)
        valid = np.isfinite(b_arr)
        if valid.sum() < 3:
            return

        ring_x = b_arr[valid] * np.cos(angles[valid] - np.pi / 2)
        ring_y = b_arr[valid] * np.sin(angles[valid] - np.pi / 2)

        # Compute flux for ring particles
        from ..math.fast_geodesics import redshift_vec, flux_observed_vec
        z = redshift_vec(r_ring[valid], angles[valid], inclination_rad, self.mass, b_arr[valid])
        flux = flux_observed_vec(r_ring[valid], self.mass, z, accretion_rate)

        if max_flux > min_flux:
            flux_norm = ((np.abs(flux) + min_flux) / (max_flux + min_flux)) ** power_scale
        else:
            flux_norm = np.full(valid.sum(), 0.8)

        ring_sizes = dot_size * (0.8 + 2.5 * np.clip(flux_norm, 0, 1))

        if use_white:
            ax.scatter(ring_x, ring_y, c='white', s=ring_sizes,
                      alpha=flux_norm * 0.9, edgecolors='none', zorder=4)
        else:
            ax.scatter(ring_x, ring_y, c=flux_norm, cmap=cmap,
                      s=ring_sizes, alpha=0.9, edgecolors='none', zorder=4)
    
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

        # Populate export_data for plotter export (vectorized)
        all_x, all_y, all_intens = [], [], []
        show_ghost = self.params.get('show_ghost_image', True)
        for df, y_flip in [(direct_df, False), (ghost_df, True)]:
            if df is None or df.empty:
                continue
            if y_flip and not show_ghost:
                continue
            xs = df['X'].values
            ys = -df['Y'].values if y_flip else df['Y'].values
            if max_flux > 0:
                intens = np.clip((df['flux_o'].values / max_flux) ** power_scale, 0, 1)
            else:
                intens = np.full(len(df), 0.5)
            all_x.append(xs)
            all_y.append(ys)
            all_intens.append(intens)
        if all_x:
            xs_cat = np.concatenate(all_x)
            ys_cat = np.concatenate(all_y)
            intens_cat = np.concatenate(all_intens)
            self.export_data = {
                "points": list(zip(xs_cat.tolist(), ys_cat.tolist())),
                "intensities": intens_cat.tolist(),
            }
        else:
            self.export_data = {"points": [], "intensities": []}

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