# Quick Start

Get a black hole image in under a minute.

---

## Install

```bash
cd eventHorizon
pip install -e .
```

Dependencies: `numpy`, `scipy`, `matplotlib`, `pandas`, `rich`.

---

## Option A: Command line

```bash
# Interactive menu -- just run it
python main.py

# Or skip the menu:
python main.py --mode scatter -N 5000 --no-display
```

Output appears in `results/<timestamp>/`.

---

## Option B: Python

```python
import eventHorizon
import matplotlib.pyplot as plt

# Contour render (Luminet's original style)
fig, ax = eventHorizon.draw_blackhole(
    mass=1.0,
    inclination=80.0,
    mode='luminet',
    particle_count=10000,
)
plt.show()
```

---

## Three render modes

### Contour (smooth grayscale)

```python
fig, ax = eventHorizon.draw_blackhole(mode='luminet', particle_count=15000)
```

Smooth Delaunay triangulation rendered with `Greys_r`. This is closest to
Luminet's 1979 image.

### Scatter (individual dots)

```python
fig, ax = eventHorizon.plot_scatter(particle_count=15000)
```

Each particle is a colored dot (`hot` colormap). Good for seeing the
sampling structure and for pen plotter export.

### Isoradials (constant-radius curves)

```python
fig, ax = eventHorizon.plot_isoradials(radii=[6, 10, 15, 20, 30, 40])
```

White curves showing how circles on the disk are distorted by lensing.
Also good for plotter export.

---

## Export for pen plotter

```bash
# SVG + G-code from the command line
python main.py --mode isoradials --export svg gcode --no-display

# Or from Python
fig, ax = eventHorizon.draw_blackhole(
    mode='scatter', particle_count=10000,
    export=['svg'], export_dir='output/'
)
```

See [Pen Plotter Export](../plotter_export.md) for details.

---

## Key parameters

| Parameter | Default | What it does |
|-----------|---------|-------------|
| `inclination` | 80 | Viewing angle from disk plane (degrees). 0 = face-on, 90 = edge-on |
| `particle_count` | 10000 | More particles = smoother image, slower render |
| `power_scale` | 0.9 | Flux contrast. Lower = more contrast |
| `mass` | 1.0 | Black hole mass. Scales all radii proportionally |

---

## Quality presets

```bash
python main.py --mode scatter -N 10000 -q draft       # ~1s, quick preview
python main.py --mode scatter -N 10000 -q standard     # ~10s, normal
python main.py --mode scatter -N 10000 -q high         # ~20s, detailed
python main.py --mode scatter -N 10000 -q publication  # ~50s, print-ready
```

Quality multiplies the particle count: draft is 0.1x, high is 2x,
publication is 5x.

---

## What to look for

A correct render shows:

1. **Bright arc above** the black hole (back of disk lensed over the top)
2. **Left side brighter** than right (Doppler beaming from approaching gas)
3. **Dark centre** with a lensed inner edge (not a simple circle)
4. **Ghost image below** the disk (light that went around the back)
5. **Disk extends to the sides** tapering off at large radii

If any of these are missing, the physics may need attention -- see
[Physics Overview](../physics.md).

---

## Next steps

- [CLI Reference](../cli.md) -- all command-line options
- [API Reference](../api.md) -- full Python API
- [Parameter Tuning](parameter_tuning.md) -- exploring different viewing angles
- [Physics Overview](../physics.md) -- understanding what's being computed
