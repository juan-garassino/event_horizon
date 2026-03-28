# Particle Renderer Documentation

## Overview

The ParticleRenderer provides advanced rendering capabilities for Luminet-style black hole visualization. It implements sophisticated dot-based rendering techniques extracted directly from the luminet reference implementation, including tricontourf plotting, power scaling, and ghost image composition.

## Core Architecture

The ParticleRenderer follows luminet's signature visualization approach:

```
Particle Data → Flux Scaling → Tricontourf Rendering → Ghost Image Composition → Final Styling
```

## Key Components

### RenderConfig

Configuration dataclass for controlling rendering parameters:

```python
@dataclass
class RenderConfig:
    dot_size_range: Tuple[float, float] = (0.1, 2.0)
    brightness_scaling: str = 'logarithmic'
    color_scheme: str = 'temperature'
    background_color: str = 'black'
    alpha_blending: bool = True
    anti_aliasing: bool = True
    quality_level: str = 'standard'
    power_scale: float = 0.9  # Power scaling for flux visualization
    levels: int = 100  # Contour levels for tricontourf
```

## Extracted Luminet Techniques

### render_frame()

Main rendering method implementing luminet's complete visualization pipeline:

```python
def render_frame(
    self, 
    particles_df: pd.DataFrame, 
    ghost_particles_df: Optional[pd.DataFrame] = None,
    black_hole_params: Dict[str, Any] = None,
    viewport_config: Dict[str, Any] = None
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Extracted from luminet's plot_points() method
    Implements complete dot visualization with tricontourf and scatter plotting
    """
```

#### Pipeline Steps:

1. **Setup Luminet Figure**
   ```python
   fig, ax = self._setup_luminet_figure(viewport_config)
   ```

2. **Calculate Flux Scaling**
   ```python
   max_flux, min_flux = self._calculate_flux_range(particles_df, ghost_particles_df)
   ```

3. **Render Direct Image**
   ```python
   ax = self._plot_direct_image(ax, particles_df, max_flux, min_flux, black_hole_params)
   ```

4. **Render Ghost Image**
   ```python
   ax = self._plot_ghost_image(ax, ghost_particles_df, max_flux, min_flux, black_hole_params)
   ```

5. **Apply Final Styling**
   ```python
   self._apply_luminet_styling(ax, viewport_config)
   ```

### Direct Image Rendering

Extracted from luminet's `plot_direct_image()` function:

```python
def _plot_direct_image(
    self, ax: plt.Axes, particles_df: pd.DataFrame, 
    max_flux: float, min_flux: float,
    black_hole_params: Dict[str, Any] = None
) -> plt.Axes:
    """
    Implements luminet's tricontourf technique for direct image rendering
    """
    # Sort by angle for proper triangulation
    particles_sorted = particles_df.sort_values(by="angle")
    
    # Filter particles within apparent outer edge
    if black_hole_params and 'apparent_outer_edge_func' in black_hole_params:
        outer_edge_func = black_hole_params['apparent_outer_edge_func']
        mask = [b <= outer_edge_func(a) for b, a in 
               zip(particles_sorted["impact_parameter"], particles_sorted["angle"])]
        particles_filtered = particles_sorted.iloc[mask]
    
    # Apply power scaling to flux values (luminet's signature technique)
    fluxes = [(abs(fl + min_flux) / (max_flux + min_flux)) ** self.config.power_scale 
             for fl in particles_filtered['flux_o']]
    
    # Create tricontourf plot (luminet's primary visualization method)
    ax.tricontourf(
        particles_filtered['X'], particles_filtered['Y'], fluxes, 
        cmap='Greys_r', levels=self.config.levels, 
        norm=plt.Normalize(0, 1), nchunk=2
    )
    
    # Fill inner disk edge with black (artifact removal)
    if black_hole_params and 'inner_edge_coords' in black_hole_params:
        inner_x, inner_y = black_hole_params['inner_edge_coords']
        ax.fill_between(inner_x, inner_y, color='black', zorder=1)
```

### Ghost Image Rendering

Extracted from luminet's `plot_ghost_image()` function:

```python
def _plot_ghost_image(
    self, ax: plt.Axes, ghost_particles_df: pd.DataFrame,
    max_flux: float, min_flux: float,
    black_hole_params: Dict[str, Any] = None
) -> plt.Axes:
    """
    Implements luminet's ghost image rendering with Y-coordinate flipping
    """
    # Filter particles for inner and outer regions
    if black_hole_params:
        inner_edge_func = black_hole_params.get('apparent_inner_edge_func')
        outer_edge_func = black_hole_params.get('apparent_outer_edge_func')
        
        # Separate inner and outer ghost regions
        inner_mask = [b < inner_edge_func(a + np.pi) for b, a in 
                     zip(ghost_particles_df["impact_parameter"], ghost_particles_df["angle"])]
        particles_inner = ghost_particles_df.iloc[inner_mask]
        
        outer_mask = [b > outer_edge_func(a + np.pi) for b, a in 
                     zip(ghost_particles_df["impact_parameter"], ghost_particles_df["angle"])]
        particles_outer = ghost_particles_df.iloc[outer_mask]
    
    # Plot both regions with Y-coordinate flipped (luminet's ghost image technique)
    for i, particles in enumerate([particles_inner, particles_outer]):
        if particles.empty:
            continue
        
        # Sort by flux for proper rendering order
        particles_sorted = particles.sort_values(by=['flux_o'], ascending=False)
        
        # Apply power scaling
        fluxes = [(abs(fl + min_flux) / (max_flux + min_flux)) ** self.config.power_scale 
                 for fl in particles_sorted['flux_o']]
        
        # Render with Y-coordinate flipped (key luminet technique)
        ax.tricontourf(
            particles_sorted['X'], [-y for y in particles_sorted['Y']], 
            fluxes, cmap='Greys_r', norm=plt.Normalize(0, 1), 
            levels=self.config.levels, nchunk=2, zorder=1-i
        )
```

## Power Scaling Technique

Luminet's signature power scaling for enhanced visualization:

```python
def apply_power_scaling(self, flux_values: List[float], power_scale: float = 0.9) -> List[float]:
    """
    Luminet's power scaling technique:
    scaled_flux = (flux / max_flux) ^ power_scale
    
    This enhances contrast and makes faint features more visible
    while preserving the overall flux distribution structure.
    """
    if not flux_values:
        return []
    
    max_flux = max(flux_values)
    min_flux = min(flux_values)
    flux_range = max_flux - min_flux
    
    if flux_range == 0:
        return [1.0] * len(flux_values)
    
    # Normalize and apply power scaling
    scaled_fluxes = [
        ((abs(fl - min_flux) / flux_range) ** power_scale)
        for fl in flux_values
    ]
    
    return scaled_fluxes
```

## Tricontourf Rendering

Core rendering technique extracted from luminet:

```python
def render_tricontourf(
    self, 
    x_coords: List[float], 
    y_coords: List[float], 
    flux_values: List[float],
    ax: plt.Axes,
    **kwargs
) -> plt.Axes:
    """
    Luminet's tricontourf rendering technique
    
    Creates smooth contour plots from scattered particle data
    Superior to scatter plots for continuous flux visualization
    """
    try:
        # Apply power scaling
        scaled_fluxes = self.apply_power_scaling(flux_values, self.config.power_scale)
        
        # Create tricontourf plot
        contour = ax.tricontourf(
            x_coords, y_coords, scaled_fluxes,
            cmap='Greys_r',
            levels=self.config.levels,
            norm=plt.Normalize(0, 1),
            nchunk=2,  # Optimize for performance
            **kwargs
        )
        
        return ax
        
    except Exception as e:
        # Fallback to scatter plot if triangulation fails
        ax.scatter(
            x_coords, y_coords, 
            c=scaled_fluxes, 
            cmap='Greys_r', 
            s=1, 
            alpha=0.7
        )
        return ax
```

## Quality Levels

Progressive quality enhancement system:

```python
class QualitySettings:
    DRAFT = {
        'levels': 20,
        'power_scale': 0.8,
        'anti_aliasing': False,
        'nchunk': 4
    }
    
    STANDARD = {
        'levels': 100,
        'power_scale': 0.9,
        'anti_aliasing': True,
        'nchunk': 2
    }
    
    HIGH = {
        'levels': 200,
        'power_scale': 0.95,
        'anti_aliasing': True,
        'nchunk': 1
    }
    
    PUBLICATION = {
        'levels': 500,
        'power_scale': 0.98,
        'anti_aliasing': True,
        'nchunk': 1,
        'dpi': 1200
    }
```

## Luminet Styling

Authentic luminet visual styling:

```python
def _setup_luminet_figure(self, viewport_config: Dict[str, Any] = None) -> Tuple[plt.Figure, plt.Axes]:
    """
    Setup figure with authentic luminet styling
    """
    config = viewport_config or {}
    
    fig = plt.figure(figsize=config.get('figsize', (10, 10)))
    ax = fig.add_subplot(111)
    
    # Luminet's signature black background
    plt.axis('off')
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Set coordinate system
    ax_lim = config.get('ax_lim', (-40, 40))
    ax.set_xlim(ax_lim)
    ax.set_ylim(ax_lim)
    
    return fig, ax

def _apply_luminet_styling(self, ax: plt.Axes, viewport_config: Dict[str, Any] = None):
    """
    Apply final luminet-style formatting
    """
    # Equal aspect ratio (critical for accurate black hole shape)
    ax.set_aspect('equal')
    
    # Remove ticks and labels for clean look
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Optional title
    config = viewport_config or {}
    if config.get('show_title', False):
        title = config.get('title', 'Black Hole Visualization')
        ax.set_title(title, color='white')
```

## Animation Support

Frame-by-frame animation rendering:

```python
def render_animation(
    self, 
    particle_sequences: List[pd.DataFrame], 
    animation_config: Dict[str, Any] = None
) -> List[Tuple[plt.Figure, plt.Axes]]:
    """
    Render animation sequence using luminet techniques
    """
    frames = []
    
    for i, particles_df in enumerate(particle_sequences):
        # Update time-dependent parameters
        frame_config = animation_config.copy() if animation_config else {}
        frame_config['title'] = f"Frame {i+1}"
        
        # Render frame with consistent scaling
        fig, ax = self.render_frame(particles_df, viewport_config=frame_config)
        frames.append((fig, ax))
    
    return frames
```

## Export Capabilities

High-quality export with luminet settings:

```python
def export_render(
    self, 
    render_data: Tuple[plt.Figure, plt.Axes], 
    filename: str, 
    format: str = 'png', 
    quality: str = 'high'
) -> str:
    """
    Export with luminet-quality settings
    """
    fig, ax = render_data
    
    # Quality-based DPI settings
    dpi_settings = {
        'draft': 150,
        'standard': 300,
        'high': 600,
        'publication': 1200
    }
    
    dpi = dpi_settings.get(quality, 300)
    
    # Save with luminet-style settings
    fig.savefig(
        filename, 
        dpi=dpi, 
        facecolor='black',  # Luminet's signature black background
        bbox_inches='tight', 
        pad_inches=0.1
    )
    
    return filename
```

## Performance Optimizations

### Triangulation Optimization
- `nchunk` parameter for memory management
- Fallback to scatter plots for failed triangulations
- Efficient data filtering before rendering

### Memory Management
- Streaming processing for large particle counts
- Configurable quality levels for performance tuning
- Garbage collection between frames for animations

## Usage Examples

### Basic Luminet Rendering
```python
renderer = ParticleRenderer(RenderConfig(
    power_scale=0.9,
    levels=100,
    quality_level='standard'
))

fig, ax = renderer.render_frame(particles_df, ghost_particles_df)
```

### High-Quality Publication Rendering
```python
config = RenderConfig(
    power_scale=0.98,
    levels=500,
    quality_level='publication',
    anti_aliasing=True
)

renderer = ParticleRenderer(config)
fig, ax = renderer.render_frame(particles_df, ghost_particles_df)
renderer.export_render((fig, ax), 'black_hole_publication.png', quality='publication')
```

### Animation Rendering
```python
frames = renderer.render_animation(
    particle_sequences,
    animation_config={'show_title': True, 'figsize': (12, 12)}
)
```

## Integration Points

The ParticleRenderer integrates with:

- **ParticleSystem**: Receives processed particle data
- **PhysicsEngine**: Uses particles with calculated physical properties
- **Configuration System**: Respects quality and performance settings
- **Export System**: Provides multiple output formats and quality levels

This comprehensive rendering system faithfully reproduces luminet's iconic visualization techniques while providing modern performance optimizations and extensibility.