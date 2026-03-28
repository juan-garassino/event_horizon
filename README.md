# evenHorizon

A recreation of Jean-Pierre Luminet's 1979 hand-computed image of a black hole
-- one of the first scientific visualizations of what a black hole actually looks
like.

The code traces how light bends around a Schwarzschild (non-rotating) black hole
and renders the appearance of a thin accretion disk as seen by a distant observer.

![Contour render](docs/images/contour_example.png)

---

## What you get

| Mode | Description | Output |
|------|-------------|--------|
| **Contour** (`luminet`) | Smooth tricontourf rendering in Greys_r | PNG |
| **Scatter** (`scatter`) | Individual particle dots with hot colormap | PNG, SVG, G-code |
| **Isoradials** (`isoradials`) | Constant-radius curves showing gravitational lensing | PNG, SVG, G-code |

All modes use the same physics: exact elliptic-integral impact parameters
(Luminet eq. 13), proper Doppler + gravitational redshift (eq. 19), and
Novikov-Thorne accretion flux with the logarithmic correction.

---

## Quick start

```bash
# Clone and install
git clone <repo-url> && cd eventHorizon
pip install -e .

# Interactive menu (Rich TUI)
python main.py

# Or specify everything on the command line
python main.py --mode scatter -N 20000 --no-display

# Export isoradials as SVG + G-code for a pen plotter
python main.py --mode isoradials --export svg gcode --no-display
```

### Python API

```python
import eventHorizon

# Contour render (Luminet's original style)
fig, ax = eventHorizon.draw_blackhole(
    mass=1.0, inclination=80.0, mode='luminet',
    particle_count=15000, power_scale=0.9
)

# Scatter render
fig, ax = eventHorizon.plot_scatter(particle_count=20000)

# Isoradial curves
fig, ax = eventHorizon.plot_isoradials(radii=[6, 10, 15, 20, 30, 40])

# Isoradials with SVG export
fig, ax = eventHorizon.draw_blackhole(
    mode='isoradials', export=['svg', 'gcode'], export_dir='output/'
)
```

---

## CLI reference

```
python main.py [OPTIONS]
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--mode` | `-m` | *(interactive)* | `luminet`, `scatter`, `isoradials`, `all` |
| `--particle-count` | `-N` | 10000 | Number of particles |
| `--inclination` | `-i` | 80.0 | Observer angle from disk plane (degrees) |
| `--mass` | `-M` | 1.0 | Black hole mass (geometric units) |
| `--power-scale` | `-p` | 0.9 | Flux power scaling |
| `--levels` | `-l` | 100 | Contour levels |
| `--quality` | `-q` | standard | `draft` / `standard` / `high` / `publication` |
| `--export` | `-e` | *(none)* | `svg`, `gcode`, or both |
| `--no-display` | | | Save only, don't show plots |
| `--save-path` | `-o` | *(auto)* | Custom output path |

When `--mode` is omitted, an interactive Rich menu appears with mode selection,
parameter editing, and an option to export for pen plotter.

---

## Output organization

Every run creates a timestamped session folder:

```
results/
  20260328_141047/
    session.json            # Parameters, timing, file list
    luminet/
      contour_i80.0_N15000.png
    scatter/
      scatter_i80.0_N15000.png
    isoradials/
      isoradials_i80.0.png
    plotter/
      isoradials.svg
      isoradials.gcode
      scatter.svg
      scatter.gcode
```

`session.json` records everything about the run:

```json
{
  "started_at": "2026-03-28T14:10:47",
  "completed_at": "2026-03-28T14:12:23",
  "duration_seconds": 96.3,
  "params": {
    "mass": 1.0,
    "inclination": 80.0,
    "particle_count": 15000,
    "quality": "standard"
  },
  "files": ["..."],
  "status": "completed"
}
```

---

## Pen plotter export

Scatter and isoradial modes can export SVG and G-code files for pen plotters.

### SVG
- A4 landscape (297 x 210 mm), 15 mm margins
- Uniform scale preserving aspect ratio
- White strokes on black background (editable)

### G-code
- Millimetre units, absolute positioning
- Servo pen control (`M3 S1000` / `M5`) or Z-axis (configurable)
- Draw feed 3000 mm/min, travel feed 5000 mm/min
- Scatter dots use nearest-neighbor ordering to minimize pen travel
- 50 ms dwell per dot (configurable)

#### Customize plotter bed

```python
from eventHorizon.visualization.plotter_export import PlotterBed

bed = PlotterBed(
    bed_width_mm=420,     # A3 landscape
    bed_height_mm=297,
    margin_mm=20,
    world_range=(-40, 40)
)

fig, ax = eventHorizon.draw_blackhole(
    mode='isoradials',
    export=['svg', 'gcode'],
    export_dir='output/',
    export_bed_kwargs={'bed_width_mm': 420, 'bed_height_mm': 297}
)
```

---

## Physics

### Schwarzschild spacetime

All units are geometric: G = c = 1, M = 1.

| Quantity | Value |
|----------|-------|
| Event horizon | r = 2M |
| Photon sphere | r = 3M |
| ISCO (inner disk edge) | r = 6M |
| Critical impact parameter | b = 5.196M |
| Observer inclination | 80 deg (default) |
| Observer distance | >> r (flat-space limit) |

### Pipeline

1. **Impact parameter** -- For each (r, angle) on the disk, solve Luminet's
   equation 13 using elliptic integrals to find the impact parameter b that
   connects that emission point to the observer. This is the gravitational
   lensing step.

2. **Redshift** -- Compute the combined Doppler + gravitational redshift factor
   (1+z) using Luminet's equation 19:
   ```
   (1+z) = [1 + sqrt(M/r^3) * b * sin(i) * sin(a)] * [1 - 3M/r]^(-1/2)
   ```
   The approaching side of the disk (left) is blueshifted (brighter), the
   receding side is redshifted (dimmer).

3. **Flux** -- Compute the Novikov-Thorne intrinsic flux with the full
   logarithmic correction term, then apply the relativistic beaming law:
   ```
   F_obs = F_intrinsic / (1+z)^4
   ```

4. **Rendering** -- Assemble particles into a contour plot (Greys_r), scatter
   plot (hot colormap), or export as vector paths.

### Ghost image

Light that passes behind the black hole and loops around creates a secondary
(ghost) image below the main disk. Ghost particles are filtered by apparent
inner/outer edge radii and plotted with reduced opacity.

---

## Project structure

```
eventHorizon/
  core/             # Particle system, physics engine, ray tracing
  math/             # Geodesics, flux, spacetime geometry, numerical solvers
  config/           # Model config, quality presets
  visualization/
    mode_router.py  # Handler dispatch (luminet, scatter, isoradials, ...)
    plotter_export.py  # SVG + G-code generation
    particle_renderer.py
    unified_plotter.py
    export_manager.py
  utils/
    results_organization.py  # Session-based output management
  luminet.py        # Public API (draw_blackhole, plot_scatter, plot_isoradials, ...)
  __init__.py       # Package exports

main.py             # CLI with Rich interactive menu
references/         # Original luminet + bhsim reference implementations
docs/               # Technical docs, tutorials, validation
scripts/dev/        # Development and test scripts
```

---

## Dependencies

- Python 3.8+
- NumPy, SciPy (ODE integration, elliptic integrals)
- Matplotlib (rendering)
- Pandas (particle data management)
- Rich (interactive CLI, progress bars)
- Pillow (optional, for image export)

```bash
pip install numpy scipy matplotlib pandas rich
```

---

## Key numbers to remember

- Event horizon: **r = 2**
- Photon sphere: **r = 3**
- Inner disk edge (ISCO): **r = 6**
- Critical impact parameter: **b = 5.196**
- Observer angle: **80 deg** from disk plane
- Left side brighter than right (Doppler beaming)
- Ghost image visible below the disk

---

## References

- Luminet, J.-P. (1979). "Image of a spherical black hole with thin accretion disk."
  *Astronomy and Astrophysics*, 75, 228-235.
- Page, D. N. & Thorne, K. S. (1974). "Disk-accretion onto a black hole."
  *The Astrophysical Journal*, 191, 499-506.
