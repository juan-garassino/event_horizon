# Pen Plotter Export

evenHorizon can export scatter particles and isoradial curves as SVG paths
and G-code toolpaths, ready to draw on a pen plotter.

---

## Supported modes

| Mode | Export type | SVG element | G-code pattern |
|------|-----------|-------------|----------------|
| `scatter` | Dots | `<circle>` elements with optional opacity | Pen-down dwell at each point |
| `isoradials` | Lines | `<path>` elements (polylines) | Pen-down line segments |

The `luminet` (contour) mode is a filled raster surface and cannot be
meaningfully exported as vector paths.

---

## CLI usage

```bash
# Export isoradials as both SVG and G-code
python main.py --mode isoradials --export svg gcode --no-display

# Export scatter as SVG only
python main.py --mode scatter -N 10000 --export svg --no-display

# All modes -- export applies to scatter and isoradials only
python main.py --mode all --export svg gcode --no-display
```

Files are saved under the session's `plotter/` directory:
```
results/20260328_141047/plotter/
  isoradials.svg
  isoradials.gcode
  scatter.svg
  scatter.gcode
```

---

## Python API

```python
import eventHorizon

# Isoradials with export
fig, ax = eventHorizon.draw_blackhole(
    mode='isoradials',
    radii=[6, 10, 15, 20, 30, 40],
    export=['svg', 'gcode'],
    export_dir='output/',
)

# Scatter with export
fig, ax = eventHorizon.draw_blackhole(
    mode='scatter',
    particle_count=15000,
    export=['svg'],
    export_dir='output/',
)
```

---

## Coordinate mapping

The `PlotterBed` class maps world coordinates (centered on the black hole)
to plotter bed coordinates in millimetres.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `bed_width_mm` | 297 | Bed width (A4 landscape) |
| `bed_height_mm` | 210 | Bed height |
| `margin_mm` | 15 | Margins on all sides |
| `world_range` | (-40, 40) | World coordinate range |

The mapping uses uniform scaling (preserves aspect ratio) and flips the
Y axis (SVG and G-code use Y-down conventions). World origin (0, 0) maps
to the centre of the bed.

### Custom bed size

```python
fig, ax = eventHorizon.draw_blackhole(
    mode='isoradials',
    export=['svg', 'gcode'],
    export_dir='output/',
    export_bed_kwargs={
        'bed_width_mm': 420,     # A3 landscape
        'bed_height_mm': 297,
        'margin_mm': 20,
    }
)
```

### Direct API

```python
from eventHorizon.visualization.plotter_export import (
    PlotterBed, polylines_to_svg, polylines_to_gcode,
    scatter_to_svg, scatter_to_gcode
)

bed = PlotterBed(bed_width_mm=420, bed_height_mm=297)

# Isoradials
polylines = [[(x1,y1), (x2,y2), ...], ...]  # world coords
polylines_to_svg(polylines, 'output.svg', bed=bed)
polylines_to_gcode(polylines, 'output.gcode', bed=bed)

# Scatter
points = [(x1,y1), (x2,y2), ...]
intensities = [0.8, 0.3, ...]  # optional, controls SVG opacity
scatter_to_svg(points, 'output.svg', bed=bed, intensities=intensities)
scatter_to_gcode(points, 'output.gcode', bed=bed)
```

---

## SVG details

- Output is a standalone SVG with explicit `width`/`height` in mm and
  a matching `viewBox`
- Black background rectangle (set `background="none"` to omit)
- White strokes, `stroke-width=0.5` (configurable)
- Round line caps and joins
- Scatter dots rendered as `<circle>` elements; intensity maps to opacity
- Isoradials rendered as `<path>` elements with `M` / `L` commands

The SVG is ready for Inkscape, Illustrator, or direct import into
plotter software (e.g. vpype, Saxi).

---

## G-code details

### Header

```gcode
; evenHorizon plotter export
G21       ; millimetres
G90       ; absolute positioning
G28       ; home all axes
```

### Pen control

By default, servo-based pen control:

| Action | Command |
|--------|---------|
| Pen up | `M5` |
| Pen down | `M3 S1000` |

For Z-axis plotters, pass `z_pen_down` and `z_pen_up`:

```python
polylines_to_gcode(
    polylines, 'output.gcode',
    z_pen_down=-1.0,   # mm below surface
    z_pen_up=3.0,      # mm above surface
)
```

### Feed rates

| Movement | Default (mm/min) |
|----------|-----------------|
| Drawing | 3000 |
| Travel (pen up) | 5000 |

### Scatter dot pattern

Each scatter point produces:
1. `G0` travel to the point
2. Pen down
3. `G4 P50` dwell (50 ms)
4. Pen up

Points are sorted by **nearest-neighbor** to minimize total pen travel
distance. This greedy algorithm typically reduces travel by 60-80% compared
to random ordering.

### Footer

```gcode
G0 X0 Y0  ; return home
M5         ; pen up
M2         ; end program
```

---

## Tips for good plotter output

1. **Isoradials** produce the cleanest plotter output -- they are
   continuous curves with no pen lifts within each radius.

2. **Scatter with 5,000-15,000 points** gives good density on A4. More
   than 20,000 dots on A4 starts to look like a solid fill.

3. **Increase `dot_dwell_ms`** to 100-200 for felt-tip pens that need
   more ink time.

4. **Use draft quality** for test plots to save time, then switch to
   standard or high for final output.

5. **The SVG** can be post-processed with vpype for further optimization:
   ```bash
   vpype read output.svg linesort write optimized.svg
   ```

6. **Adjust margins** for your specific plotter -- some machines can't
   reach the full bed area.
