"""Advanced visualization components for black hole rendering."""

from .unified_plotter import UnifiedPlotter, create_unified_plotter
from .particle_renderer import ParticleRenderer, RenderConfig
from .isoradial_plotter import IsoradialPlotter, IsoredshiftPlotter, CombinedIsoPlotter
from .interactive_viewer import InteractiveViewer
from .animation_engine import AnimationEngine
from .export_manager import ExportManager

# Clean framework-native aliases
ParticlePlotter = UnifiedPlotter

# Legacy reference-specific aliases (deprecated)
LuminetPlotter = ParticlePlotter

__all__ = [
    # Primary unified interfaces
    'UnifiedPlotter',
    'create_unified_plotter',
    'ParticleRenderer',
    'RenderConfig',
    'IsoradialPlotter',
    'IsoredshiftPlotter', 
    'CombinedIsoPlotter',
    'InteractiveViewer',
    'AnimationEngine',
    'ExportManager',
    
    # Clean framework-native aliases
    'ParticlePlotter',
    
    # Legacy compatibility (deprecated)
    'LuminetPlotter'
]