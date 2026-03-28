"""
Animation Engine for EventHorizon

This module provides comprehensive animation capabilities for black hole
visualizations, including parameter sweeps and comparison animations.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import os
import time
from typing import List, Dict, Any, Callable, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

# Import eventHorizon components
from ..luminet import draw_blackhole, plot_isoradials, plot_isoredshifts, plot_photon_sphere
from ..config.quality_presets import apply_quality_preset
from ..utils.progress_monitor import create_progress_monitor


@dataclass
class AnimationConfig:
    """Configuration for animation generation."""
    fps: int = 10
    duration_seconds: float = 5.0
    quality_level: str = "standard"
    figsize: Tuple[int, int] = (10, 10)
    dpi: int = 100
    output_format: str = "mp4"  # "mp4", "gif", "frames"
    show_progress: bool = True
    cleanup_frames: bool = True


class AnimationEngine:
    """Engine for creating black hole visualization animations."""
    
    def __init__(self, config: Optional[AnimationConfig] = None):
        """
        Initialize animation engine.
        
        Parameters
        ----------
        config : AnimationConfig, optional
            Animation configuration. If None, uses default settings.
        """
        self.config = config or AnimationConfig()
        self.frames = []
        self.current_animation = None
    
    def create_inclination_sweep(self,
                               inclination_range: Tuple[float, float] = (10, 170),
                               num_frames: int = 36,
                               **visualization_params) -> str:
        """
        Create animation sweeping through inclination angles.
        
        Parameters
        ----------
        inclination_range : Tuple[float, float], default=(10, 170)
            Range of inclination angles in degrees
        num_frames : int, default=36
            Number of frames in animation
        **visualization_params
            Additional parameters for visualization
            
        Returns
        -------
        str
            Path to generated animation file
            
        Examples
        --------
        >>> engine = AnimationEngine()
        >>> animation_path = engine.create_inclination_sweep(
        ...     inclination_range=(30, 150),
        ...     num_frames=24,
        ...     particle_count=5000
        ... )
        """
        print(f"\n🎬 Creating inclination sweep animation...")
        print(f"   Range: {inclination_range[0]}° to {inclination_range[1]}°")
        print(f"   Frames: {num_frames}")
        
        # Generate inclination values
        inclinations = np.linspace(inclination_range[0], inclination_range[1], num_frames)
        
        # Apply quality preset
        params = apply_quality_preset(self.config.quality_level, **visualization_params)
        
        # Create frames
        frames_dir = self._setup_frames_directory("inclination_sweep")
        
        monitor = create_progress_monitor(self.config.show_progress)
        
        with monitor.monitor_operation("Inclination Sweep Animation", num_frames):
            for i, inclination in enumerate(inclinations):
                monitor.update_progress(i, f"Inclination: {inclination:.1f}°")
                
                # Create visualization
                fig, ax = draw_blackhole(inclination=inclination, **params)
                
                # Add frame info
                ax.text(0.02, 0.98, f'Inclination: {inclination:.1f}°', 
                       transform=ax.transAxes, color='white', fontsize=14,
                       verticalalignment='top', bbox=dict(boxstyle='round', 
                       facecolor='black', alpha=0.7))
                
                # Save frame
                frame_path = frames_dir / f"frame_{i:04d}.png"
                plt.savefig(frame_path, facecolor='black', dpi=self.config.dpi)
                plt.close(fig)
        
        # Create animation
        output_path = self._create_animation_from_frames(frames_dir, "inclination_sweep")
        
        if self.config.cleanup_frames:
            self._cleanup_frames(frames_dir)
        
        return str(output_path)
    
    def create_mass_sweep(self,
                         mass_range: Tuple[float, float] = (0.5, 5.0),
                         num_frames: int = 30,
                         **visualization_params) -> str:
        """
        Create animation sweeping through black hole masses.
        
        Parameters
        ----------
        mass_range : Tuple[float, float], default=(0.5, 5.0)
            Range of black hole masses
        num_frames : int, default=30
            Number of frames in animation
        **visualization_params
            Additional parameters for visualization
            
        Returns
        -------
        str
            Path to generated animation file
        """
        print(f"\n🎬 Creating mass sweep animation...")
        print(f"   Range: {mass_range[0]} to {mass_range[1]} M☉")
        print(f"   Frames: {num_frames}")
        
        # Generate mass values
        masses = np.linspace(mass_range[0], mass_range[1], num_frames)
        
        # Apply quality preset
        params = apply_quality_preset(self.config.quality_level, **visualization_params)
        
        # Create frames
        frames_dir = self._setup_frames_directory("mass_sweep")
        
        monitor = create_progress_monitor(self.config.show_progress)
        
        with monitor.monitor_operation("Mass Sweep Animation", num_frames):
            for i, mass in enumerate(masses):
                monitor.update_progress(i, f"Mass: {mass:.2f}M☉")
                
                # Create visualization
                fig, ax = draw_blackhole(mass=mass, **params)
                
                # Add frame info
                ax.text(0.02, 0.98, f'Mass: {mass:.2f}M☉', 
                       transform=ax.transAxes, color='white', fontsize=14,
                       verticalalignment='top', bbox=dict(boxstyle='round', 
                       facecolor='black', alpha=0.7))
                
                # Save frame
                frame_path = frames_dir / f"frame_{i:04d}.png"
                plt.savefig(frame_path, facecolor='black', dpi=self.config.dpi)
                plt.close(fig)
        
        # Create animation
        output_path = self._create_animation_from_frames(frames_dir, "mass_sweep")
        
        if self.config.cleanup_frames:
            self._cleanup_frames(frames_dir)
        
        return str(output_path)
    
    def create_particle_count_sweep(self,
                                  particle_range: Tuple[int, int] = (1000, 50000),
                                  num_frames: int = 20,
                                  **visualization_params) -> str:
        """
        Create animation showing effect of particle count on quality.
        
        Parameters
        ----------
        particle_range : Tuple[int, int], default=(1000, 50000)
            Range of particle counts
        num_frames : int, default=20
            Number of frames in animation
        **visualization_params
            Additional parameters for visualization
            
        Returns
        -------
        str
            Path to generated animation file
        """
        print(f"\n🎬 Creating particle count sweep animation...")
        print(f"   Range: {particle_range[0]:,} to {particle_range[1]:,} particles")
        print(f"   Frames: {num_frames}")
        
        # Generate particle counts (logarithmic scale for better distribution)
        log_min = np.log10(particle_range[0])
        log_max = np.log10(particle_range[1])
        log_counts = np.linspace(log_min, log_max, num_frames)
        particle_counts = [int(10**log_count) for log_count in log_counts]
        
        # Apply quality preset (without particle_count override)
        params = apply_quality_preset(self.config.quality_level, **visualization_params)
        params.pop('particle_count', None)  # Remove default particle count
        
        # Create frames
        frames_dir = self._setup_frames_directory("particle_count_sweep")
        
        monitor = create_progress_monitor(self.config.show_progress)
        
        with monitor.monitor_operation("Particle Count Sweep Animation", num_frames):
            for i, particle_count in enumerate(particle_counts):
                monitor.update_progress(i, f"Particles: {particle_count:,}")
                
                # Create visualization
                fig, ax = draw_blackhole(particle_count=particle_count, **params)
                
                # Add frame info
                ax.text(0.02, 0.98, f'Particles: {particle_count:,}', 
                       transform=ax.transAxes, color='white', fontsize=14,
                       verticalalignment='top', bbox=dict(boxstyle='round', 
                       facecolor='black', alpha=0.7))
                
                # Save frame
                frame_path = frames_dir / f"frame_{i:04d}.png"
                plt.savefig(frame_path, facecolor='black', dpi=self.config.dpi)
                plt.close(fig)
        
        # Create animation
        output_path = self._create_animation_from_frames(frames_dir, "particle_count_sweep")
        
        if self.config.cleanup_frames:
            self._cleanup_frames(frames_dir)
        
        return str(output_path)
    
    def create_comparison_animation(self,
                                  visualization_types: List[str] = None,
                                  inclination_range: Tuple[float, float] = (30, 150),
                                  num_frames: int = 24,
                                  **visualization_params) -> str:
        """
        Create side-by-side comparison animation of different visualization methods.
        
        Parameters
        ----------
        visualization_types : List[str], optional
            Types to compare: ["luminet", "isoradials", "isoredshifts", "photon_sphere"]
            If None, uses ["luminet", "isoradials"]
        inclination_range : Tuple[float, float], default=(30, 150)
            Range of inclination angles
        num_frames : int, default=24
            Number of frames in animation
        **visualization_params
            Additional parameters for visualization
            
        Returns
        -------
        str
            Path to generated animation file
        """
        if visualization_types is None:
            visualization_types = ["luminet", "isoradials"]
        
        print(f"\n🎬 Creating comparison animation...")
        print(f"   Types: {visualization_types}")
        print(f"   Inclination range: {inclination_range[0]}° to {inclination_range[1]}°")
        print(f"   Frames: {num_frames}")
        
        # Generate inclination values
        inclinations = np.linspace(inclination_range[0], inclination_range[1], num_frames)
        
        # Apply quality preset
        params = apply_quality_preset(self.config.quality_level, **visualization_params)
        
        # Create frames
        frames_dir = self._setup_frames_directory("comparison_animation")
        
        monitor = create_progress_monitor(self.config.show_progress)
        
        with monitor.monitor_operation("Comparison Animation", num_frames):
            for i, inclination in enumerate(inclinations):
                monitor.update_progress(i, f"Inclination: {inclination:.1f}°")
                
                # Create comparison figure
                fig, axes = plt.subplots(1, len(visualization_types), 
                                       figsize=(self.config.figsize[0] * len(visualization_types), 
                                               self.config.figsize[1]))
                fig.patch.set_facecolor('black')
                
                if len(visualization_types) == 1:
                    axes = [axes]
                
                for j, viz_type in enumerate(visualization_types):
                    # Create individual visualization
                    if viz_type == "luminet":
                        temp_fig, temp_ax = draw_blackhole(inclination=inclination, **params)
                        title = "Luminet Particles"
                    elif viz_type == "isoradials":
                        temp_fig, temp_ax = plot_isoradials(inclination=inclination, 
                                                           mass=params.get('mass', 1.0))
                        title = "Isoradial Curves"
                    elif viz_type == "isoredshifts":
                        temp_fig, temp_ax = plot_isoredshifts(inclination=inclination,
                                                            mass=params.get('mass', 1.0),
                                                            particle_count=params.get('particle_count', 5000))
                        title = "Isoredshift Curves"
                    elif viz_type == "photon_sphere":
                        temp_fig, temp_ax = plot_photon_sphere(mass=params.get('mass', 1.0))
                        title = "Photon Sphere"
                    else:
                        continue
                    
                    # Copy to comparison subplot
                    axes[j].clear()
                    axes[j].set_facecolor('black')
                    
                    # Copy all visual elements
                    for collection in temp_ax.collections:
                        axes[j].add_collection(collection)
                    for line in temp_ax.lines:
                        axes[j].add_line(line)
                    for patch in temp_ax.patches:
                        axes[j].add_patch(patch)
                    
                    axes[j].set_xlim(temp_ax.get_xlim())
                    axes[j].set_ylim(temp_ax.get_ylim())
                    axes[j].set_aspect('equal')
                    axes[j].set_title(f'{title}\ni = {inclination:.1f}°', 
                                     color='white', fontsize=12)
                    axes[j].axis('off')
                    
                    plt.close(temp_fig)
                
                # Save frame
                frame_path = frames_dir / f"frame_{i:04d}.png"
                plt.tight_layout()
                plt.savefig(frame_path, facecolor='black', dpi=self.config.dpi)
                plt.close(fig)
        
        # Create animation
        output_path = self._create_animation_from_frames(frames_dir, "comparison_animation")
        
        if self.config.cleanup_frames:
            self._cleanup_frames(frames_dir)
        
        return str(output_path)
    
    def create_parameter_evolution_animation(self,
                                           parameter_name: str,
                                           parameter_values: List[float],
                                           **visualization_params) -> str:
        """
        Create animation showing evolution of a specific parameter.
        
        Parameters
        ----------
        parameter_name : str
            Name of parameter to animate
        parameter_values : List[float]
            Values of parameter for each frame
        **visualization_params
            Additional parameters for visualization
            
        Returns
        -------
        str
            Path to generated animation file
        """
        print(f"\n🎬 Creating {parameter_name} evolution animation...")
        print(f"   Values: {len(parameter_values)} frames")
        print(f"   Range: {min(parameter_values):.2f} to {max(parameter_values):.2f}")
        
        # Apply quality preset
        params = apply_quality_preset(self.config.quality_level, **visualization_params)
        
        # Create frames
        frames_dir = self._setup_frames_directory(f"{parameter_name}_evolution")
        
        monitor = create_progress_monitor(self.config.show_progress)
        
        with monitor.monitor_operation(f"{parameter_name.title()} Evolution Animation", len(parameter_values)):
            for i, param_value in enumerate(parameter_values):
                monitor.update_progress(i, f"{parameter_name}: {param_value:.2f}")
                
                # Set parameter value
                current_params = params.copy()
                current_params[parameter_name] = param_value
                
                # Create visualization
                fig, ax = draw_blackhole(**current_params)
                
                # Add frame info
                ax.text(0.02, 0.98, f'{parameter_name.title()}: {param_value:.2f}', 
                       transform=ax.transAxes, color='white', fontsize=14,
                       verticalalignment='top', bbox=dict(boxstyle='round', 
                       facecolor='black', alpha=0.7))
                
                # Save frame
                frame_path = frames_dir / f"frame_{i:04d}.png"
                plt.savefig(frame_path, facecolor='black', dpi=self.config.dpi)
                plt.close(fig)
        
        # Create animation
        output_path = self._create_animation_from_frames(frames_dir, f"{parameter_name}_evolution")
        
        if self.config.cleanup_frames:
            self._cleanup_frames(frames_dir)
        
        return str(output_path)
    
    def _setup_frames_directory(self, animation_name: str) -> Path:
        """Setup directory for animation frames."""
        frames_dir = Path("results/animations/frames") / animation_name
        frames_dir.mkdir(parents=True, exist_ok=True)
        return frames_dir
    
    def _create_animation_from_frames(self, frames_dir: Path, animation_name: str) -> Path:
        """Create animation file from individual frames."""
        output_dir = Path("results/animations")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.config.output_format == "gif":
            output_path = output_dir / f"{animation_name}.gif"
            self._create_gif_from_frames(frames_dir, output_path)
        elif self.config.output_format == "mp4":
            output_path = output_dir / f"{animation_name}.mp4"
            self._create_mp4_from_frames(frames_dir, output_path)
        else:
            # Just return frames directory
            return frames_dir
        
        return output_path
    
    def _create_gif_from_frames(self, frames_dir: Path, output_path: Path):
        """Create GIF animation from frames."""
        try:
            from PIL import Image
            
            # Load all frames
            frame_files = sorted(frames_dir.glob("frame_*.png"))
            frames = [Image.open(frame_file) for frame_file in frame_files]
            
            # Calculate frame duration
            frame_duration = int(1000 / self.config.fps)  # milliseconds
            
            # Save as GIF
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=frame_duration,
                loop=0
            )
            
            print(f"✅ GIF animation saved: {output_path}")
            
        except ImportError:
            print("❌ PIL/Pillow not available for GIF creation")
            print("   Install with: pip install Pillow")
    
    def _create_mp4_from_frames(self, frames_dir: Path, output_path: Path):
        """Create MP4 animation from frames."""
        try:
            import subprocess
            
            # Use ffmpeg to create MP4
            frame_pattern = str(frames_dir / "frame_%04d.png")
            
            cmd = [
                'ffmpeg', '-y',  # -y to overwrite output file
                '-framerate', str(self.config.fps),
                '-i', frame_pattern,
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ MP4 animation saved: {output_path}")
            else:
                print(f"❌ FFmpeg error: {result.stderr}")
                
        except FileNotFoundError:
            print("❌ FFmpeg not found for MP4 creation")
            print("   Install ffmpeg: https://ffmpeg.org/download.html")
    
    def _cleanup_frames(self, frames_dir: Path):
        """Clean up individual frame files."""
        import shutil
        if frames_dir.exists():
            shutil.rmtree(frames_dir)
            print(f"🧹 Cleaned up frames directory: {frames_dir}")


# Convenience functions for easy animation creation
def create_inclination_animation(inclination_range: Tuple[float, float] = (10, 170),
                               num_frames: int = 36,
                               quality_level: str = "standard",
                               **kwargs) -> str:
    """
    Create inclination sweep animation with default settings.
    
    Parameters
    ----------
    inclination_range : Tuple[float, float], default=(10, 170)
        Range of inclination angles in degrees
    num_frames : int, default=36
        Number of frames in animation
    quality_level : str, default="standard"
        Quality level for visualization
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated animation file
        
    Examples
    --------
    >>> animation_path = create_inclination_animation(
    ...     inclination_range=(30, 150),
    ...     num_frames=24,
    ...     quality_level="high"
    ... )
    """
    config = AnimationConfig(quality_level=quality_level)
    engine = AnimationEngine(config)
    return engine.create_inclination_sweep(inclination_range, num_frames, **kwargs)


def create_comparison_animation(visualization_types: List[str] = None,
                              inclination_range: Tuple[float, float] = (30, 150),
                              num_frames: int = 24,
                              quality_level: str = "standard",
                              **kwargs) -> str:
    """
    Create comparison animation with default settings.
    
    Parameters
    ----------
    visualization_types : List[str], optional
        Visualization types to compare
    inclination_range : Tuple[float, float], default=(30, 150)
        Range of inclination angles
    num_frames : int, default=24
        Number of frames in animation
    quality_level : str, default="standard"
        Quality level for visualization
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated animation file
        
    Examples
    --------
    >>> animation_path = create_comparison_animation(
    ...     visualization_types=["luminet", "isoradials"],
    ...     inclination_range=(45, 135),
    ...     num_frames=18
    ... )
    """
    config = AnimationConfig(quality_level=quality_level)
    engine = AnimationEngine(config)
    return engine.create_comparison_animation(visualization_types, inclination_range, num_frames, **kwargs)


def create_parameter_animation(parameter_name: str,
                             parameter_values: List[float],
                             quality_level: str = "standard",
                             **kwargs) -> str:
    """
    Create parameter evolution animation with default settings.
    
    Parameters
    ----------
    parameter_name : str
        Name of parameter to animate
    parameter_values : List[float]
        Values of parameter for each frame
    quality_level : str, default="standard"
        Quality level for visualization
    **kwargs
        Additional visualization parameters
        
    Returns
    -------
    str
        Path to generated animation file
        
    Examples
    --------
    >>> masses = [0.5, 1.0, 2.0, 5.0, 10.0]
    >>> animation_path = create_parameter_animation("mass", masses)
    """
    config = AnimationConfig(quality_level=quality_level)
    engine = AnimationEngine(config)
    return engine.create_parameter_evolution_animation(parameter_name, parameter_values, **kwargs)