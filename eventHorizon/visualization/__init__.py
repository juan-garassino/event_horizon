"""Advanced visualization components for black hole rendering."""

from .unified_plotter import UnifiedPlotter, create_unified_plotter
from .particle_renderer import ParticleRenderer, RenderConfig
from .isoradial_plotter import IsoradialPlotter, IsoredshiftPlotter, CombinedIsoPlotter
from .export_manager import ExportManager
from .mode_router import ModeRouter, VisualizationHandler

# Clean framework-native aliases
ParticlePlotter = UnifiedPlotter

# Legacy reference-specific aliases (deprecated)
LuminetPlotter = ParticlePlotter

__all__ = [
    'UnifiedPlotter', 'create_unified_plotter',
    'ParticleRenderer', 'RenderConfig',
    'IsoradialPlotter', 'IsoredshiftPlotter', 'CombinedIsoPlotter',
    'ExportManager', 'ModeRouter', 'VisualizationHandler',
    'ParticlePlotter', 'LuminetPlotter',
]
