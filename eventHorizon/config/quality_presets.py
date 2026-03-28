"""
Quality Enhancement and Presets for EventHorizon

This module provides configurable quality levels and presets for different
use cases, from quick drafts to publication-quality visualizations.
"""

import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class QualityLevel(Enum):
    """Enumeration of available quality levels."""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PUBLICATION = "publication"


class UseCase(Enum):
    """Enumeration of different use cases."""
    INTERACTIVE = "interactive"
    BATCH_PROCESSING = "batch_processing"
    PUBLICATION = "publication"
    EDUCATION = "education"
    RESEARCH = "research"


@dataclass
class QualityConfig:
    """Configuration for a specific quality level."""
    particle_count: int
    power_scale: float
    levels: int
    figsize: tuple
    dpi: int
    expected_time_seconds: float
    memory_usage_mb: float
    description: str


@dataclass
class PerformanceMetrics:
    """Performance metrics for a visualization operation."""
    execution_time: float
    particle_count: int
    quality_level: str
    memory_used_mb: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


class QualityPresetManager:
    """Manager for quality presets and performance monitoring."""
    
    def __init__(self):
        """Initialize quality preset manager."""
        self.quality_configs = self._setup_quality_configs()
        self.use_case_presets = self._setup_use_case_presets()
        self.performance_history = []
    
    def _setup_quality_configs(self) -> Dict[QualityLevel, QualityConfig]:
        """Setup predefined quality configurations."""
        return {
            QualityLevel.DRAFT: QualityConfig(
                particle_count=2000,
                power_scale=0.9,
                levels=50,
                figsize=(8, 8),
                dpi=100,
                expected_time_seconds=2.0,
                memory_usage_mb=50,
                description="Fast preview quality for quick iterations"
            ),
            QualityLevel.STANDARD: QualityConfig(
                particle_count=10000,
                power_scale=0.9,
                levels=100,
                figsize=(10, 10),
                dpi=150,
                expected_time_seconds=8.0,
                memory_usage_mb=150,
                description="Good balance of quality and performance"
            ),
            QualityLevel.HIGH: QualityConfig(
                particle_count=50000,
                power_scale=0.8,
                levels=200,
                figsize=(12, 12),
                dpi=200,
                expected_time_seconds=30.0,
                memory_usage_mb=400,
                description="High-quality visualization for detailed analysis"
            ),
            QualityLevel.PUBLICATION: QualityConfig(
                particle_count=100000,
                power_scale=0.7,
                levels=300,
                figsize=(16, 16),
                dpi=300,
                expected_time_seconds=120.0,
                memory_usage_mb=800,
                description="Publication-quality with maximum detail"
            )
        }
    
    def _setup_use_case_presets(self) -> Dict[UseCase, Dict[str, Any]]:
        """Setup presets for different use cases."""
        return {
            UseCase.INTERACTIVE: {
                'quality_level': QualityLevel.DRAFT,
                'show_progress': True,
                'auto_save': False,
                'background_color': 'black',
                'show_warnings': True,
                'description': "Optimized for interactive exploration and parameter tuning"
            },
            UseCase.BATCH_PROCESSING: {
                'quality_level': QualityLevel.STANDARD,
                'show_progress': False,
                'auto_save': True,
                'background_color': 'black',
                'show_warnings': False,
                'parallel_processing': True,
                'description': "Optimized for processing multiple visualizations efficiently"
            },
            UseCase.PUBLICATION: {
                'quality_level': QualityLevel.PUBLICATION,
                'show_progress': True,
                'auto_save': True,
                'background_color': 'black',
                'show_warnings': True,
                'validate_output': True,
                'description': "Maximum quality for scientific publications"
            },
            UseCase.EDUCATION: {
                'quality_level': QualityLevel.STANDARD,
                'show_progress': True,
                'auto_save': True,
                'background_color': 'black',
                'show_warnings': True,
                'add_annotations': True,
                'description': "Clear visualizations with educational annotations"
            },
            UseCase.RESEARCH: {
                'quality_level': QualityLevel.HIGH,
                'show_progress': True,
                'auto_save': True,
                'background_color': 'black',
                'show_warnings': True,
                'validate_output': True,
                'save_metadata': True,
                'description': "High-quality visualizations with detailed metadata"
            }
        }
    
    def get_quality_config(self, quality_level: QualityLevel) -> QualityConfig:
        """Get configuration for a specific quality level."""
        return self.quality_configs[quality_level]
    
    def get_use_case_preset(self, use_case: UseCase) -> Dict[str, Any]:
        """Get preset configuration for a specific use case."""
        return self.use_case_presets[use_case]
    
    def get_recommended_quality(self, 
                              target_time_seconds: Optional[float] = None,
                              available_memory_mb: Optional[float] = None) -> QualityLevel:
        """Recommend quality level based on constraints."""
        if target_time_seconds is not None:
            # Find highest quality that meets time constraint
            for quality in [QualityLevel.PUBLICATION, QualityLevel.HIGH, 
                          QualityLevel.STANDARD, QualityLevel.DRAFT]:
                config = self.quality_configs[quality]
                if config.expected_time_seconds <= target_time_seconds:
                    return quality
        
        if available_memory_mb is not None:
            # Find highest quality that meets memory constraint
            for quality in [QualityLevel.PUBLICATION, QualityLevel.HIGH, 
                          QualityLevel.STANDARD, QualityLevel.DRAFT]:
                config = self.quality_configs[quality]
                if config.memory_usage_mb <= available_memory_mb:
                    return quality
        
        # Default to standard quality
        return QualityLevel.STANDARD
    
    def create_progressive_config(self, 
                                base_quality: QualityLevel,
                                enhancement_factor: float = 1.5) -> QualityConfig:
        """Create enhanced configuration based on existing quality level."""
        base_config = self.quality_configs[base_quality]
        
        return QualityConfig(
            particle_count=int(base_config.particle_count * enhancement_factor),
            power_scale=max(0.3, base_config.power_scale - 0.1),
            levels=int(base_config.levels * enhancement_factor),
            figsize=base_config.figsize,
            dpi=min(300, int(base_config.dpi * 1.2)),
            expected_time_seconds=base_config.expected_time_seconds * (enhancement_factor ** 1.5),
            memory_usage_mb=base_config.memory_usage_mb * enhancement_factor,
            description=f"Enhanced {base_config.description}"
        )
    
    def monitor_performance(self, 
                          func: Callable,
                          quality_level: QualityLevel,
                          particle_count: int,
                          *args, **kwargs) -> tuple:
        """Monitor performance of a visualization function."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            success = True
            error_message = None
        except Exception as e:
            result = None
            success = False
            error_message = str(e)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        # Record performance metrics
        metrics = PerformanceMetrics(
            execution_time=end_time - start_time,
            particle_count=particle_count,
            quality_level=quality_level.value,
            memory_used_mb=end_memory - start_memory if start_memory and end_memory else None,
            success=success,
            error_message=error_message
        )
        
        self.performance_history.append(metrics)
        
        return result, metrics
    
    def _get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return None
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance history."""
        if not self.performance_history:
            return {'message': 'No performance data available'}
        
        successful_runs = [m for m in self.performance_history if m.success]
        
        if not successful_runs:
            return {'message': 'No successful runs recorded'}
        
        # Calculate statistics
        times = [m.execution_time for m in successful_runs]
        particle_counts = [m.particle_count for m in successful_runs]
        
        summary = {
            'total_runs': len(self.performance_history),
            'successful_runs': len(successful_runs),
            'average_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'average_particle_count': sum(particle_counts) / len(particle_counts),
            'quality_levels_used': list(set(m.quality_level for m in successful_runs))
        }
        
        # Add memory statistics if available
        memory_data = [m.memory_used_mb for m in successful_runs if m.memory_used_mb is not None]
        if memory_data:
            summary.update({
                'average_memory_mb': sum(memory_data) / len(memory_data),
                'max_memory_mb': max(memory_data)
            })
        
        return summary
    
    def suggest_quality_optimization(self, target_time: float = 10.0) -> Dict[str, Any]:
        """Suggest quality optimizations based on performance history."""
        if not self.performance_history:
            return {'suggestion': 'No performance data available for optimization'}
        
        successful_runs = [m for m in self.performance_history if m.success]
        
        if not successful_runs:
            return {'suggestion': 'No successful runs to analyze'}
        
        # Find runs that meet target time
        fast_runs = [m for m in successful_runs if m.execution_time <= target_time]
        
        if fast_runs:
            # Find the highest particle count that still meets target time
            best_run = max(fast_runs, key=lambda m: m.particle_count)
            return {
                'suggestion': f'Use {best_run.particle_count} particles for {target_time}s target',
                'quality_level': best_run.quality_level,
                'expected_time': best_run.execution_time,
                'particle_count': best_run.particle_count
            }
        else:
            # All runs are too slow, suggest reducing quality
            fastest_run = min(successful_runs, key=lambda m: m.execution_time)
            return {
                'suggestion': f'Reduce particle count below {fastest_run.particle_count}',
                'current_fastest': fastest_run.execution_time,
                'target_time': target_time,
                'recommended_reduction': 0.5
            }


# Global instance for easy access
quality_manager = QualityPresetManager()


def get_quality_config(quality_level: str) -> QualityConfig:
    """Get quality configuration by string name."""
    level_map = {
        'draft': QualityLevel.DRAFT,
        'standard': QualityLevel.STANDARD,
        'high': QualityLevel.HIGH,
        'publication': QualityLevel.PUBLICATION
    }
    
    if quality_level not in level_map:
        raise ValueError(f"Unknown quality level: {quality_level}. "
                        f"Available: {list(level_map.keys())}")
    
    return quality_manager.get_quality_config(level_map[quality_level])


def get_use_case_preset(use_case: str) -> Dict[str, Any]:
    """Get use case preset by string name."""
    case_map = {
        'interactive': UseCase.INTERACTIVE,
        'batch_processing': UseCase.BATCH_PROCESSING,
        'publication': UseCase.PUBLICATION,
        'education': UseCase.EDUCATION,
        'research': UseCase.RESEARCH
    }
    
    if use_case not in case_map:
        raise ValueError(f"Unknown use case: {use_case}. "
                        f"Available: {list(case_map.keys())}")
    
    return quality_manager.get_use_case_preset(case_map[use_case])


def apply_quality_preset(quality_level: str, **override_params) -> Dict[str, Any]:
    """Apply quality preset with optional parameter overrides."""
    config = get_quality_config(quality_level)
    
    # Convert to dictionary
    params = {
        'particle_count': config.particle_count,
        'power_scale': config.power_scale,
        'levels': config.levels,
        'figsize': config.figsize,
        'dpi': config.dpi
    }
    
    # Apply overrides
    params.update(override_params)
    
    return params


def apply_use_case_preset(use_case: str, **override_params) -> Dict[str, Any]:
    """Apply use case preset with optional parameter overrides."""
    preset = get_use_case_preset(use_case)
    
    # Get quality config from preset
    quality_config = quality_manager.get_quality_config(preset['quality_level'])
    
    # Combine quality config with use case settings
    params = {
        'particle_count': quality_config.particle_count,
        'power_scale': quality_config.power_scale,
        'levels': quality_config.levels,
        'figsize': quality_config.figsize,
        'dpi': quality_config.dpi,
        'background_color': preset.get('background_color', 'black'),
        'show_progress': preset.get('show_progress', True),
        'auto_save': preset.get('auto_save', False)
    }
    
    # Apply overrides
    params.update(override_params)
    
    return params