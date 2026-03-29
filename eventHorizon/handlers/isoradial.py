"""
IsoradialHandler -- isoradial curve visualization.

Renders isoradial curves (constant-radius contours) for both direct and
ghost images, including the black hole shadow outline.
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Tuple, List

from .base import VisualizationHandler
from ..physics.geodesics import UnifiedGeodesics
from ..utils.validation import validate_and_suggest


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

    def _compute_isoradial(self, geodesics, radius, inclination_rad, angular_resolution, image_order=0):
        """Compute isoradial curve for a given radius and image order.
        Returns (impact_params, valid_angles) or ([], []) on failure."""
        angles = np.linspace(0, 2 * np.pi, angular_resolution)
        impact_params = []
        valid_angles = []
        for angle in angles:
            try:
                b = geodesics.calculate_impact_parameter(
                    angle, radius, inclination_rad, image_order=image_order,
                )
                if b is not None and b > 0:
                    impact_params.append(b)
                    valid_angles.append(angle)
            except Exception:
                continue
        return impact_params, valid_angles

    def _plot_isoradial(self, ax, x, y, angular_resolution, **plot_kwargs):
        """Plot an isoradial curve, using spline smoothing if resolution is high enough."""
        if angular_resolution >= 720:
            try:
                from scipy.interpolate import splprep, splev
                x_closed = x + [x[0]]
                y_closed = y + [y[0]]
                tck, u = splprep([x_closed, y_closed], s=0, per=True)
                u_new = np.linspace(0, 1, angular_resolution * 2)
                x_smooth, y_smooth = splev(u_new, tck)
                ax.plot(x_smooth, y_smooth, **plot_kwargs)
                return
            except (ImportError, Exception):
                pass
        ax.plot(x, y, **plot_kwargs)

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render isoradial curves (direct + ghost) and populate export_data with polylines."""
        validate_and_suggest("plot_isoradials", mass=self.mass, inclination=self.inclination)

        radii = self.params.get('radii')
        if radii is None:
            radii = list(range(6, 51, 5))

        angular_resolution = self.params.get('angular_resolution', 360)
        show_ghost = self.params.get('show_ghost_image', True)

        fig, ax = self.setup_figure()

        geodesics = UnifiedGeodesics(mass=self.mass)
        inclination_rad = self.inclination * np.pi / 180

        all_polylines: List[List[Tuple[float, float]]] = []

        # --- Direct isoradials (image_order=0, solid white) ---
        for radius in radii:
            try:
                impact_params, valid_angles = self._compute_isoradial(
                    geodesics, radius, inclination_rad, angular_resolution, image_order=0,
                )
                if len(impact_params) > 3:
                    x = [b * np.cos(a - np.pi / 2) for b, a in zip(impact_params, valid_angles)]
                    y = [b * np.sin(a - np.pi / 2) for b, a in zip(impact_params, valid_angles)]

                    all_polylines.append(list(zip(x, y)))

                    label = f'r = {radius}M' if self.params.get('show_labels', False) else None
                    self._plot_isoradial(
                        ax, x, y, angular_resolution,
                        color='white', alpha=0.7, linewidth=1, label=label,
                    )
            except Exception:
                continue

        # --- Ghost isoradials (image_order=1, dashed, Y-flipped) ---
        if show_ghost:
            for radius in radii:
                try:
                    impact_params, valid_angles = self._compute_isoradial(
                        geodesics, radius, inclination_rad, angular_resolution, image_order=1,
                    )
                    if len(impact_params) > 3:
                        x = [b * np.cos(a - np.pi / 2) for b, a in zip(impact_params, valid_angles)]
                        y = [-b * np.sin(a - np.pi / 2) for b, a in zip(impact_params, valid_angles)]

                        all_polylines.append(list(zip(x, y)))

                        ax.plot(x, y, color='white', alpha=0.4, linewidth=0.8, linestyle='--')
                except Exception:
                    continue

        # --- Black hole shadow outline (b_crit = sqrt(27) * M) ---
        b_crit = np.sqrt(27.0) * self.mass
        shadow_angles = np.linspace(0, 2 * np.pi, 200)
        shadow_x = b_crit * np.cos(shadow_angles)
        shadow_y = b_crit * np.sin(shadow_angles)
        ax.plot(shadow_x, shadow_y, color='gray', alpha=0.3, linewidth=0.6, linestyle=':')

        # Store for plotter export
        self.export_data = {"polylines": all_polylines}

        if self.params.get('show_title', True):
            ax.set_title('Isoradial Curves', color='white')

        if self.params.get('show_labels', False):
            ax.legend(loc='upper right')

        return fig, ax
