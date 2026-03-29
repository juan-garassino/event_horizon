"""
RedshiftHandler -- redshift contour visualization.

Rewritten to use generate_particles_fast() from physics.fast_geodesics
instead of the legacy ParticleSystem / PhysicsEngine pipeline.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Tuple, List

from .base import VisualizationHandler
from ..physics.fast_geodesics import generate_particles_fast
from ..visualization.unified_plotter import UnifiedPlotter
from ..utils.validation import validate_and_suggest


class RedshiftHandler(VisualizationHandler):
    """Handler for redshift contour visualization."""

    def validate_parameters(self) -> bool:
        """Validate parameters for redshift mode."""
        redshift_levels = self.params.get('redshift_levels')
        if redshift_levels is not None and not isinstance(redshift_levels, (list, tuple)):
            raise ValueError("redshift_levels must be a list or tuple")
        return True

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render redshift contours using fast vectorized particle generation."""
        validate_and_suggest("plot_isoredshifts", mass=self.mass, inclination=self.inclination)

        redshift_levels = self.params.get('redshift_levels')
        if redshift_levels is None:
            redshift_levels = [-0.2, -0.15, -0.1, -0.05, 0., 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75]

        particle_count = self.params.get('particle_count', 5000)
        inclination_rad = self.inclination * np.pi / 180.0
        accretion_rate = self.params.get('accretion_rate', 1.0)

        # Generate particles using the fast vectorized path
        direct_df, ghost_df, min_flux, max_flux = generate_particles_fast(
            particle_count,
            self.mass,
            inclination_rad,
            accretion_rate=accretion_rate,
            ghost=False,  # Redshift contours typically use direct image only
        )

        # Combine into a single DataFrame for the plotter
        particles_df = direct_df.copy() if not direct_df.empty else pd.DataFrame()

        # Use unified plotter for isoredshift visualization
        plotter = UnifiedPlotter()

        # Filter out parameters that conflict with plot_isoredshift_contours signature
        plotter_params = {
            k: v for k, v in self.params.items()
            if k not in {
                'figsize', 'ax_lim', 'background_color', 'redshift_levels',
                'mass', 'inclination', 'particle_count', 'accretion_rate',
                'mode', 'show_ghost_image', 'progress_callback',
                'power_scale', 'levels', 'colormap', 'dot_size',
            }
        }

        fig = plotter.plot_isoredshift_contours(
            particles_df=particles_df,
            redshift_levels=redshift_levels,
            figsize=self.figsize,
            **plotter_params,
        )

        return fig, fig.axes[0]
