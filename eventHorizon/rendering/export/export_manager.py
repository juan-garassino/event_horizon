"""
Export manager for various output formats.

This module handles exporting visualizations and data
in multiple formats for different use cases.
Enhanced with luminet-style export capabilities.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
import json


class ExportManager:
    """Manager for exporting visualizations and data with luminet-style capabilities."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize export manager."""
        self.config = config or {
            'default_quality': 'high',
            'default_format': 'png',
            'luminet_dpi': 300,
            'luminet_facecolor': 'black'
        }

    def export_image(self, figure_data: Union[plt.Figure, Tuple[plt.Figure, plt.Axes]],
                    output_path: Path, format: str = 'png',
                    quality: str = 'high', **kwargs):
        """
        Export visualization as image with luminet-style settings.

        Supports the quality levels and DPI settings used in luminet reference.
        """
        # Extract figure from data
        if isinstance(figure_data, tuple):
            fig, ax = figure_data
        else:
            fig = figure_data

        # Set DPI based on quality (luminet-style)
        dpi_settings = {
            'draft': 150,
            'standard': 300,
            'high': 600,
            'publication': 1200
        }

        dpi = dpi_settings.get(quality, self.config.get('luminet_dpi', 300))

        # Apply luminet export settings
        export_kwargs = {
            'dpi': dpi,
            'facecolor': kwargs.get('facecolor', self.config.get('luminet_facecolor', 'black')),
            'bbox_inches': 'tight',
            'pad_inches': kwargs.get('pad_inches', 0.1)
        }

        # Add format-specific settings
        if format.lower() == 'svg':
            export_kwargs['format'] = 'svg'
        elif format.lower() == 'pdf':
            export_kwargs['format'] = 'pdf'

        # Save the figure
        fig.savefig(str(output_path), **export_kwargs)

        return str(output_path)

    def export_data(self, data: pd.DataFrame, output_path: Path,
                   format: str = 'csv', **kwargs):
        """
        Export particle data in luminet-compatible formats.

        Supports the CSV format used by luminet for particle coordinates and flux data.
        """
        if format.lower() == 'csv':
            # Use luminet-style CSV format with index
            data.to_csv(str(output_path), index=True)
        elif format.lower() == 'json':
            # Export as JSON for modern applications
            data.to_json(str(output_path), orient='records', indent=2)
        elif format.lower() == 'hdf5':
            # High-performance format for large datasets
            data.to_hdf(str(output_path), key='particles', mode='w')
        else:
            raise ValueError(f"Unsupported data format: {format}")

        return str(output_path)

    def export_animation(self, frames: List[Tuple[plt.Figure, plt.Axes]],
                        output_path: Path, format: str = 'gif',
                        fps: int = 10, **kwargs):
        """
        Export animation sequence using luminet-style frame rendering.

        Supports GIF and MP4 formats similar to luminet's animation capabilities.
        """
        if format.lower() == 'gif':
            return self._export_gif_animation(frames, output_path, fps, **kwargs)
        elif format.lower() == 'mp4':
            return self._export_mp4_animation(frames, output_path, fps, **kwargs)
        else:
            raise ValueError(f"Unsupported animation format: {format}")

    def _export_gif_animation(self, frames: List[Tuple[plt.Figure, plt.Axes]],
                             output_path: Path, fps: int, **kwargs):
        """Export GIF animation (requires pillow)."""
        try:
            from PIL import Image
            import io
        except ImportError:
            raise ImportError("PIL (Pillow) required for GIF export")

        images = []

        for fig, ax in frames:
            # Save figure to bytes
            buf = io.BytesIO()
            fig.savefig(buf, format='png',
                       facecolor=self.config.get('luminet_facecolor', 'black'),
                       dpi=150)  # Lower DPI for animations
            buf.seek(0)

            # Convert to PIL Image
            img = Image.open(buf)
            images.append(img)

            # Close the buffer
            buf.close()

        # Save as GIF
        if images:
            duration = int(1000 / fps)  # Convert fps to milliseconds
            images[0].save(
                str(output_path),
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0
            )

        return str(output_path)

    def _export_mp4_animation(self, frames: List[Tuple[plt.Figure, plt.Axes]],
                             output_path: Path, fps: int, **kwargs):
        """Export MP4 animation (requires ffmpeg)."""
        try:
            import matplotlib.animation as animation
        except ImportError:
            raise ImportError("matplotlib.animation required for MP4 export")

        if not frames:
            return str(output_path)

        # Create animation from frames
        fig, ax = frames[0]

        def animate(frame_idx):
            ax.clear()
            # Re-plot the frame content
            # This is a simplified version - in practice, you'd need to store
            # the plot data and re-render each frame
            return ax.collections

        anim = animation.FuncAnimation(fig, animate, frames=len(frames),
                                     interval=int(1000/fps), blit=False)

        # Save as MP4
        writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='eventHorizon'),
                                      bitrate=1800)
        anim.save(str(output_path), writer=writer)

        return str(output_path)

    def export_interactive(self, data: pd.DataFrame, output_path: Path, **kwargs):
        """Export interactive visualization (HTML with plotly)."""
        try:
            import plotly.graph_objects as go
            import plotly.express as px
        except ImportError:
            raise ImportError("plotly required for interactive export")

        # Create interactive scatter plot
        if 'X' in data.columns and 'Y' in data.columns:
            fig = px.scatter(data, x='X', y='Y',
                           color=data.get('flux_o', None),
                           title='Interactive Black Hole Visualization')

            # Apply dark theme (luminet-style)
            fig.update_layout(
                plot_bgcolor='black',
                paper_bgcolor='black',
                font_color='white'
            )

            # Save as HTML
            fig.write_html(str(output_path))

        return str(output_path)

    def batch_export(self, export_jobs: List[Dict[str, Any]], **kwargs):
        """
        Perform batch export operations.

        Each job should be a dict with keys: 'type', 'data', 'output_path', 'format', etc.
        """
        results = []

        for job in export_jobs:
            job_type = job.get('type', 'image')
            data = job.get('data')
            output_path = Path(job.get('output_path'))
            format_type = job.get('format', self.config['default_format'])

            try:
                if job_type == 'image':
                    result = self.export_image(data, output_path, format_type, **job)
                elif job_type == 'data':
                    result = self.export_data(data, output_path, format_type, **job)
                elif job_type == 'animation':
                    result = self.export_animation(data, output_path, format_type, **job)
                elif job_type == 'interactive':
                    result = self.export_interactive(data, output_path, **job)
                else:
                    raise ValueError(f"Unknown export type: {job_type}")

                results.append({'status': 'success', 'output': result, 'job': job})

            except Exception as e:
                results.append({'status': 'error', 'error': str(e), 'job': job})

        return results

    def export_luminet_composition(self, direct_particles: pd.DataFrame,
                                  ghost_particles: pd.DataFrame,
                                  black_hole_params: Dict[str, Any],
                                  output_path: Path,
                                  composition_config: Dict[str, Any] = None,
                                  **kwargs):
        """
        Export luminet-style composed image with proper direct/ghost image handling.

        Uses the LuminetCompositor for proper image composition.
        """
        from ..compositor import LuminetCompositor, CompositionConfig

        # Setup compositor
        if composition_config:
            config = CompositionConfig(**composition_config)
        else:
            config = CompositionConfig()

        compositor = LuminetCompositor(config)

        # Create composition
        fig, ax = compositor.compose_images(
            direct_particles=direct_particles,
            ghost_particles=ghost_particles,
            black_hole_params=black_hole_params,
            **kwargs
        )

        # Export the composed image
        return self.export_image(fig, output_path, **kwargs)

    def export_multi_inclination_sequence(self, direct_particles: pd.DataFrame,
                                        ghost_particles: pd.DataFrame,
                                        output_dir: Path,
                                        inclinations: List[float] = None,
                                        **kwargs):
        """
        Export sequence of images at different inclination angles.

        Creates a series of images showing the black hole from different viewing angles.
        """
        from ..compositor import LuminetCompositor, CompositionConfig

        if inclinations is None:
            inclinations = list(range(0, 181, 5))  # 0 to 180 degrees in 5-degree steps

        # Setup compositor
        config = CompositionConfig()
        compositor = LuminetCompositor(config)

        # Create compositions at different inclinations
        compositions = compositor.create_multi_inclination_composition(
            particles=direct_particles,
            ghost_particles=ghost_particles,
            inclinations=inclinations,
            **kwargs
        )

        # Export each composition
        exported_files = []
        for i, (fig, ax) in enumerate(compositions):
            filename = output_dir / f'inclination_{inclinations[i]:03d}.png'
            exported_path = self.export_image(fig, filename, **kwargs)
            exported_files.append(exported_path)

            # Close figure to save memory
            plt.close(fig)

        return exported_files

    def export_luminet_comparison(self, original_data: pd.DataFrame,
                                 generated_data: pd.DataFrame,
                                 output_dir: Path, **kwargs):
        """
        Export comparison between original luminet data and generated results.

        Creates side-by-side visualizations for validation purposes.
        """
        from ..plotter import UnifiedPlotter

        plotter = UnifiedPlotter()

        # Create comparison figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

        # Plot original data
        if not original_data.empty:
            ax1.scatter(original_data.get('X', []), original_data.get('Y', []),
                       c=original_data.get('flux_o', 'blue'), cmap='Greys_r', s=1)
            ax1.set_title('Original Luminet Data')
            ax1.set_facecolor('black')

        # Plot generated data
        if not generated_data.empty:
            ax2.scatter(generated_data.get('X', []), generated_data.get('Y', []),
                       c=generated_data.get('flux_o', 'blue'), cmap='Greys_r', s=1)
            ax2.set_title('Generated Data')
            ax2.set_facecolor('black')

        # Apply consistent styling
        for ax in [ax1, ax2]:
            ax.set_aspect('equal')
            ax.set_xlim(-40, 40)
            ax.set_ylim(-40, 40)

        fig.patch.set_facecolor('black')

        # Export comparison
        comparison_path = output_dir / 'luminet_comparison.png'
        self.export_image(fig, comparison_path, quality='high')

        # Export data files
        if not original_data.empty:
            self.export_data(original_data, output_dir / 'original_data.csv')
        if not generated_data.empty:
            self.export_data(generated_data, output_dir / 'generated_data.csv')

        return {
            'comparison_image': str(comparison_path),
            'original_data': str(output_dir / 'original_data.csv'),
            'generated_data': str(output_dir / 'generated_data.csv')
        }
