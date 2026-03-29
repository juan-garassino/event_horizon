"""
ScatterHandler -- scatter-dot visualization of the accretion disk.

Extends LuminetPointsHandler with scatter-plot rendering and export data.
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Tuple

from .contour import LuminetPointsHandler
from ..utils.validation import validate_and_suggest


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
            power_scale=self.params.get('power_scale', 0.9),
        )
        power_scale = self.params.get('power_scale', 0.9)
        particle_count = self.params.get('particle_count', 10000)

        print(f"Generating {particle_count} scatter particles with exact Luminet physics...")

        direct_df, ghost_df, min_flux, max_flux = self._generate_particle_data(
            progress_callback=self.params.get('progress_callback'),
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
