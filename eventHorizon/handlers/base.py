"""
Base handler classes and mode router.

VisualizationHandler ABC and ModeRouter dispatch class.
"""
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Tuple, List
from abc import ABC, abstractmethod


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
        # Exportable data populated by render() -- used by plotter_export
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


class RayTracingHandler(VisualizationHandler):
    """Handler for ray-traced visualization (thin wrapper around LuminetPointsHandler)."""

    def validate_parameters(self) -> bool:
        return True

    def render(self) -> Tuple[plt.Figure, plt.Axes]:
        """Render ray-traced visualization by delegating to LuminetPointsHandler."""
        from .contour import LuminetPointsHandler
        points_handler = LuminetPointsHandler(self.params)
        return points_handler.render()


class ModeRouter:
    """Router that dispatches to appropriate visualization handlers."""

    VALID_MODES = {
        'points', 'luminet', 'scatter', 'raytracing', 'isoradials',
        'redshift', 'photon_sphere', 'apparent_edges'
    }

    def __init__(self):
        """Initialize the mode router."""
        from .contour import LuminetPointsHandler
        from .scatter import ScatterHandler
        from .isoradial import IsoradialHandler
        from .redshift import RedshiftHandler
        from .overlays import PhotonSphereHandler, ApparentEdgeHandler

        self.handlers = {
            'points': LuminetPointsHandler,
            'luminet': LuminetPointsHandler,  # Alias for points
            'scatter': ScatterHandler,
            'raytracing': RayTracingHandler,
            'isoradials': IsoradialHandler,
            'redshift': RedshiftHandler,
            'photon_sphere': PhotonSphereHandler,
            'apparent_edges': ApparentEdgeHandler,
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
            'apparent_edges': ['angular_resolution'],
        }
        return mode_params.get(mode, [])
