"""
Overlay handlers -- photon sphere and apparent edge visualizations.
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Tuple

from .base import VisualizationHandler
from ..physics.geodesics import UnifiedGeodesics
from ..utils.validation import validate_and_suggest


class PhotonSphereHandler(VisualizationHandler):
    """Handler for photon sphere visualization."""

    def validate_parameters(self) -> bool:
        return True

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render photon sphere visualization."""
        validate_and_suggest("plot_photon_sphere", mass=self.mass)

        fig, ax = self.setup_figure()

        # Plot photon sphere (r = 3M)
        photon_sphere_radius = 3.0 * self.mass
        circle = plt.Circle(
            (0, 0), photon_sphere_radius,
            fill=False, color='red', linestyle='--',
            linewidth=2, alpha=0.8, label='Photon Sphere',
        )
        ax.add_patch(circle)

        # Plot event horizon (r = 2M)
        event_horizon_radius = 2.0 * self.mass
        horizon_circle = plt.Circle(
            (0, 0), event_horizon_radius,
            fill=True, color='black',
            edgecolor='white', linewidth=1,
            alpha=1.0, label='Event Horizon',
        )
        ax.add_patch(horizon_circle)

        if self.params.get('show_title', True):
            ax.set_title('Photon Sphere and Event Horizon', color='white')

        if self.params.get('show_legend', True):
            ax.legend(loc='upper right')

        return fig, ax


class ApparentEdgeHandler(VisualizationHandler):
    """Handler for apparent edge visualization."""

    def validate_parameters(self) -> bool:
        return True

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render apparent inner edge visualization."""
        validate_and_suggest("plot_apparent_inner_edge", mass=self.mass, inclination=self.inclination)

        fig, ax = self.setup_figure()

        geodesics = UnifiedGeodesics(mass=self.mass)
        inclination_rad = self.inclination * np.pi / 180

        angular_resolution = self.params.get('angular_resolution', 360)
        angles = np.linspace(0, 2 * np.pi, angular_resolution)
        inner_radius = 6.0 * self.mass  # ISCO

        # Calculate impact parameters for inner edge
        impact_params = []
        for angle in angles:
            try:
                b = geodesics.calculate_impact_parameter(
                    angle, inner_radius, inclination_rad, image_order=0,
                )
                impact_params.append(b if b is not None else 0)
            except Exception:
                impact_params.append(0)

        # Convert to Cartesian coordinates (rotate 90 degrees clockwise)
        x = [b * np.cos(a - np.pi / 2) for b, a in zip(impact_params, angles)]
        y = [b * np.sin(a - np.pi / 2) for b, a in zip(impact_params, angles)]

        ax.plot(x, y, color='orange', linewidth=2, alpha=0.8, label='Apparent Inner Edge')

        # Reference circles
        photon_circle = plt.Circle(
            (0, 0), 3.0 * self.mass, fill=False, color='red',
            linestyle='--', alpha=0.6, label='Photon Sphere',
        )
        horizon_circle = plt.Circle(
            (0, 0), 2.0 * self.mass, fill=True, color='black',
            edgecolor='white', alpha=1.0, label='Event Horizon',
        )
        ax.add_patch(photon_circle)
        ax.add_patch(horizon_circle)

        if self.params.get('show_title', True):
            ax.set_title(f'Apparent Inner Edge (i={self.inclination})', color='white')

        if self.params.get('show_legend', True):
            ax.legend(loc='upper right')

        return fig, ax
