"""
Progress Monitoring for EventHorizon

This module provides progress monitoring capabilities for long-running
geodesic calculations and visualization operations.
"""

import time
import sys
from typing import Optional, Callable, Any, Dict
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class ProgressState:
    """State information for progress monitoring."""
    current_step: int
    total_steps: int
    start_time: float
    current_operation: str
    estimated_remaining: Optional[float] = None


class ProgressMonitor:
    """Progress monitor for long-running operations."""
    
    def __init__(self, show_progress: bool = True, update_interval: float = 0.5):
        """
        Initialize progress monitor.
        
        Parameters
        ----------
        show_progress : bool, default=True
            Whether to display progress information
        update_interval : float, default=0.5
            Minimum time between progress updates in seconds
        """
        self.show_progress = show_progress
        self.update_interval = update_interval
        self.last_update_time = 0
        self.state = None
    
    @contextmanager
    def monitor_operation(self, operation_name: str, total_steps: int):
        """
        Context manager for monitoring an operation.
        
        Parameters
        ----------
        operation_name : str
            Name of the operation being monitored
        total_steps : int
            Total number of steps in the operation
            
        Yields
        ------
        ProgressState
            Current progress state
        """
        self.state = ProgressState(
            current_step=0,
            total_steps=total_steps,
            start_time=time.time(),
            current_operation=operation_name
        )
        
        if self.show_progress:
            self._print_start_message()
        
        try:
            yield self.state
        finally:
            if self.show_progress:
                self._print_completion_message()
            self.state = None
    
    def update_progress(self, step: int, substep_info: str = ""):
        """
        Update progress to a specific step.
        
        Parameters
        ----------
        step : int
            Current step number
        substep_info : str, optional
            Additional information about current substep
        """
        if self.state is None:
            return
        
        self.state.current_step = step
        current_time = time.time()
        
        # Calculate estimated remaining time
        if step > 0:
            elapsed = current_time - self.state.start_time
            rate = step / elapsed
            remaining_steps = self.state.total_steps - step
            self.state.estimated_remaining = remaining_steps / rate if rate > 0 else None
        
        # Update display if enough time has passed
        if (current_time - self.last_update_time) >= self.update_interval:
            if self.show_progress:
                self._print_progress_update(substep_info)
            self.last_update_time = current_time
    
    def _print_start_message(self):
        """Print operation start message."""
        print(f"\n🚀 Starting {self.state.current_operation}...")
        print(f"   Total steps: {self.state.total_steps}")
        sys.stdout.flush()
    
    def _print_progress_update(self, substep_info: str = ""):
        """Print progress update."""
        if self.state is None:
            return
        
        percentage = (self.state.current_step / self.state.total_steps) * 100
        
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * self.state.current_step // self.state.total_steps)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Format time information
        elapsed = time.time() - self.state.start_time
        elapsed_str = self._format_time(elapsed)
        
        remaining_str = ""
        if self.state.estimated_remaining is not None:
            remaining_str = f" | ETA: {self._format_time(self.state.estimated_remaining)}"
        
        # Format substep info
        substep_str = f" | {substep_info}" if substep_info else ""
        
        # Print update (overwrite previous line)
        progress_line = (f"\r   Progress: [{bar}] {percentage:5.1f}% "
                        f"({self.state.current_step}/{self.state.total_steps}) "
                        f"| Elapsed: {elapsed_str}{remaining_str}{substep_str}")
        
        print(progress_line, end='', flush=True)
    
    def _print_completion_message(self):
        """Print operation completion message."""
        if self.state is None:
            return
        
        elapsed = time.time() - self.state.start_time
        elapsed_str = self._format_time(elapsed)
        
        print(f"\n✅ {self.state.current_operation} completed in {elapsed_str}")
        sys.stdout.flush()
    
    def _format_time(self, seconds: float) -> str:
        """Format time duration as human-readable string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.0f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


class ParticleGenerationMonitor(ProgressMonitor):
    """Specialized progress monitor for particle generation."""
    
    def monitor_particle_generation(self, particle_count: int):
        """Monitor particle generation progress."""
        return self.monitor_operation("Particle Generation", particle_count)
    
    def update_particle_progress(self, particles_generated: int, current_operation: str = ""):
        """Update particle generation progress."""
        self.update_progress(particles_generated, current_operation)


class GeodesicCalculationMonitor(ProgressMonitor):
    """Specialized progress monitor for geodesic calculations."""
    
    def monitor_geodesic_calculation(self, total_rays: int):
        """Monitor geodesic ray tracing progress."""
        return self.monitor_operation("Geodesic Ray Tracing", total_rays)
    
    def update_geodesic_progress(self, rays_completed: int, current_ray_info: str = ""):
        """Update geodesic calculation progress."""
        self.update_progress(rays_completed, current_ray_info)


class RenderingMonitor(ProgressMonitor):
    """Specialized progress monitor for rendering operations."""
    
    def monitor_rendering(self, total_elements: int):
        """Monitor rendering progress."""
        return self.monitor_operation("Visualization Rendering", total_elements)
    
    def update_rendering_progress(self, elements_rendered: int, current_element: str = ""):
        """Update rendering progress."""
        self.update_progress(elements_rendered, current_element)


# Global progress monitors for easy access
particle_monitor = ParticleGenerationMonitor()
geodesic_monitor = GeodesicCalculationMonitor()
rendering_monitor = RenderingMonitor()


def create_progress_monitor(show_progress: bool = True) -> ProgressMonitor:
    """Create a new progress monitor instance."""
    return ProgressMonitor(show_progress=show_progress)


@contextmanager
def monitor_visualization_pipeline(particle_count: int, show_progress: bool = True):
    """
    Monitor complete visualization pipeline.
    
    Parameters
    ----------
    particle_count : int
        Number of particles being processed
    show_progress : bool, default=True
        Whether to show progress information
        
    Yields
    ------
    Dict[str, ProgressMonitor]
        Dictionary of specialized progress monitors
    """
    monitors = {
        'particle': ParticleGenerationMonitor(show_progress),
        'geodesic': GeodesicCalculationMonitor(show_progress),
        'rendering': RenderingMonitor(show_progress)
    }
    
    if show_progress:
        print(f"\n🌌 Starting Black Hole Visualization Pipeline")
        print(f"   Particle count: {particle_count:,}")
        print(f"   Estimated total time: {_estimate_pipeline_time(particle_count)}")
    
    try:
        yield monitors
    finally:
        if show_progress:
            print(f"\n🎉 Visualization pipeline completed!")


def _estimate_pipeline_time(particle_count: int) -> str:
    """Estimate total pipeline execution time."""
    # Rough estimates based on typical performance
    particle_time = particle_count * 0.0001  # 0.1ms per particle
    geodesic_time = particle_count * 0.001   # 1ms per ray
    rendering_time = particle_count * 0.0005  # 0.5ms per particle
    
    total_seconds = particle_time + geodesic_time + rendering_time
    
    if total_seconds < 60:
        return f"~{total_seconds:.1f}s"
    elif total_seconds < 3600:
        minutes = total_seconds / 60
        return f"~{minutes:.1f}m"
    else:
        hours = total_seconds / 3600
        return f"~{hours:.1f}h"


# Decorator for automatic progress monitoring
def monitor_function_progress(operation_name: str, show_progress: bool = True):
    """
    Decorator to automatically monitor function progress.
    
    Parameters
    ----------
    operation_name : str
        Name of the operation for display
    show_progress : bool, default=True
        Whether to show progress information
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            monitor = ProgressMonitor(show_progress)
            
            # Try to extract particle count or similar from arguments
            total_steps = 100  # Default
            for arg in args:
                if isinstance(arg, int) and arg > 100:
                    total_steps = arg
                    break
            
            with monitor.monitor_operation(operation_name, total_steps):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator