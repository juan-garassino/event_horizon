"""Utility functions and helpers for Event Horizon framework."""

from .performance import PerformanceProfiler
from .validation import ParameterValidator
from .results_organization import (
    create_results_structure,
    save_figure_organized,
    create_session_summary,
    get_organized_path,
    list_generated_files,
    cleanup_old_results,
    start_session,
    end_session,
    get_active_session_path,
    list_sessions,
    archive_loose_files,
)

# Stubs for deleted modules
CoordinateTransforms = type('CoordinateTransforms', (), {})
ParticleArray = type('ParticleArray', (), {})
ImageData = type('ImageData', (), {})

__all__ = [
    'CoordinateTransforms',
    'ParticleArray',
    'ImageData',
    'PerformanceProfiler',
    'ParameterValidator',
    'create_results_structure',
    'save_figure_organized',
    'create_session_summary',
    'get_organized_path',
    'list_generated_files',
    'cleanup_old_results',
    'start_session',
    'end_session',
    'get_active_session_path',
    'list_sessions',
    'archive_loose_files',
]
