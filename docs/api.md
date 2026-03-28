# API Reference

All public functions are available from the top-level `eventHorizon` package.

```python
import eventHorizon
```

---

## Visualization functions

### `draw_blackhole()`

Main entry point. Routes to the appropriate handler based on `mode`.

```python
fig, ax = eventHorizon.draw_blackhole(
    mass=1.0,
    inclination=80.0,
    mode='luminet',          # 'luminet', 'scatter', 'isoradials', 'points',
                             # 'raytracing', 'redshift', 'photon_sphere',
                             # 'apparent_edges'
    particle_count=10000,
    power_scale=0.9,
    levels=100,
    figsize=(10, 10),
    ax_lim=(-40, 40),
    background_color='black',
    show_ghost_image=True,
    accretion_rate=1.0,
    radii=None,              # for isoradials mode
    angular_resolution=360,  # for isoradials mode
    # Plotter export
    export=None,             # ['svg'], ['gcode'], or ['svg', 'gcode']
    export_dir=None,         # output directory for plotter files
    export_bed_kwargs=None,  # dict of PlotterBed overrides
    # Progress
    progress_callback=None,  # callback(current, total) for UI
)
```

**Returns:** `(matplotlib.Figure, matplotlib.Axes)`

---

### `plot_points()`

Luminet's original contour render (alias for `draw_blackhole(mode='luminet')`).

```python
fig, ax = eventHorizon.plot_points(
    mass=1.0, inclination=80.0, particle_count=10000,
    power_scale=0.9, levels=100
)
```

---

### `plot_scatter()`

Scatter-dot render with hot colormap.

```python
fig, ax = eventHorizon.plot_scatter(
    mass=1.0, inclination=80.0, particle_count=10000,
    power_scale=0.9
)
```

---

### `plot_isoradials()`

Constant-radius curves showing gravitational lensing.

```python
fig, ax = eventHorizon.plot_isoradials(
    mass=1.0, inclination=80.0,
    radii=[6, 10, 15, 20, 30, 40, 50]  # default: range(6, 51, 5)
)
```

---

### `plot_isoredshifts()`

Constant-redshift contour curves.

```python
fig, ax = eventHorizon.plot_isoredshifts(
    mass=1.0, inclination=80.0,
    redshift_levels=[-0.2, -0.1, 0, 0.1, 0.2, 0.5]
)
```

---

### `plot_photon_sphere()`

Photon sphere boundary at r = 3M.

```python
fig, ax = eventHorizon.plot_photon_sphere(mass=1.0)
```

---

### `plot_apparent_inner_edge()`

Apparent inner edge of the accretion disk (gravitationally lensed ISCO).

```python
fig, ax = eventHorizon.plot_apparent_inner_edge(mass=1.0, inclination=80.0)
```

---

## Convenience functions

### `quick_blackhole()`

Fast render with default parameters.

```python
fig, ax = eventHorizon.quick_blackhole(inclination=80.0)
```

### `high_quality_blackhole()`

High particle count (50,000), reduced power scale (0.8), 200 levels.

```python
fig, ax = eventHorizon.high_quality_blackhole(inclination=80.0)
```

### `compare_inclinations()`

Generate multiple renders at different viewing angles.

```python
results = eventHorizon.compare_inclinations(
    inclinations=[30, 60, 80, 90]
)
for fig, ax in results:
    plt.show()
```

---

## Session management

### `start_session()`

Start a new timestamped session. All subsequent `save_figure_organized()`
calls save into this session's directory.

```python
session_path = eventHorizon.start_session(
    base_path='results',
    params={'inclination': 80, 'mode': 'scatter'}
)
# session_path = "results/20260328_141047"
```

### `end_session()`

Finalize the session: update session.json with completion time and file list.

```python
path = eventHorizon.end_session()
```

### `save_figure_organized()`

Save a figure into the active session (or fallback to `base_path`).

```python
path = eventHorizon.save_figure_organized(
    fig, 'my_render.png', category='scatter', dpi=200
)
```

### `list_sessions()`

List all sessions, newest first.

```python
sessions = eventHorizon.list_sessions()
for s in sessions:
    print(s['timestamp'], s['status'], s.get('duration_seconds'))
```

### `archive_loose_files()`

Move root-level PNGs and old flat directories to `results/_archive/`.

```python
moved = eventHorizon.archive_loose_files()
```

---

## Plotter export

### Direct API

```python
from eventHorizon.visualization.plotter_export import (
    PlotterBed,
    polylines_to_svg,
    polylines_to_gcode,
    scatter_to_svg,
    scatter_to_gcode,
    export_render_data,
)
```

See [Pen Plotter Export](plotter_export.md) for detailed documentation.

---

## Quality presets

```python
from eventHorizon import get_quality_config, apply_quality_preset

config = get_quality_config('high')
print(config.particle_count)     # 20000
print(config.expected_time_seconds)

params = apply_quality_preset('publication', inclination=85.0)
fig, ax = eventHorizon.draw_blackhole(**params)
```

---

## Mode router (advanced)

The mode router dispatches to handler classes. You can access it directly
for custom workflows.

```python
from eventHorizon.visualization.mode_router import ModeRouter

router = ModeRouter()
print(sorted(router.VALID_MODES))
# ['apparent_edges', 'isoradials', 'luminet', 'photon_sphere',
#  'points', 'raytracing', 'redshift', 'scatter']

handler = router.route_visualization('scatter', {
    'mass': 1.0, 'inclination': 80.0, 'particle_count': 5000,
    'power_scale': 0.9, 'show_ghost_image': True
})
handler.validate_parameters()
fig, ax = handler.render()

# Access raw export data after render
print(handler.get_export_type())  # 'scatter'
print(len(handler.export_data['points']))
```
