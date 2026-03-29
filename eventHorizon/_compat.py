"""Backward compatibility aliases. All deprecated -- use canonical imports."""

from .physics.geodesics import UnifiedGeodesics as Geodesics
from .physics.geodesics import UnifiedGeodesics as KerrGeodesics
from .config.model_config import ModelConfig

# Clean framework aliases
ParticleModel = None  # Will be set after VisualizationModel is available
ParticlePlotter = None
ParticleConfig = ModelConfig

# Legacy reference aliases
LuminetModel = None
LuminetPlotter = None
LuminetConfiguration = ModelConfig
BhsimAdapter = None
LuminetAdapter = None


def _setup_lazy_aliases():
    """Setup aliases that depend on heavier imports."""
    global ParticleModel, ParticlePlotter, LuminetModel, LuminetPlotter
    global BhsimAdapter, LuminetAdapter
    try:
        from .core import VisualizationModel
        ParticleModel = VisualizationModel
        LuminetModel = VisualizationModel
    except ImportError:
        pass
    try:
        from .rendering.plotter import UnifiedPlotter
        ParticlePlotter = UnifiedPlotter
        LuminetPlotter = UnifiedPlotter
    except ImportError:
        try:
            from .visualization.unified_plotter import UnifiedPlotter
            ParticlePlotter = UnifiedPlotter
            LuminetPlotter = UnifiedPlotter
        except ImportError:
            pass
    try:
        from .adapters.reference_adapter import UnifiedReferenceAdapter
        BhsimAdapter = UnifiedReferenceAdapter
        LuminetAdapter = UnifiedReferenceAdapter
    except ImportError:
        pass
