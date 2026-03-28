# CLI Reference

evenHorizon provides a command-line interface with two usage patterns:
an **interactive Rich menu** (when run with no arguments) and a
**non-interactive argparse mode** (when `--mode` is specified).

---

## Interactive mode

```bash
python main.py
```

The interactive menu walks you through:

1. **Mode selection** -- scatter, contour, isoradials, or all three
2. **Parameter review** -- shows a table of current parameters (inclination,
   particle count, mass, quality) and lets you modify them
3. **Plotter export** -- for scatter and isoradials, asks if you want SVG/G-code
4. **Progress bar** -- Rich progress bar during particle generation
5. **Summary panel** -- at the end, shows session path, timing, and file count

---

## Non-interactive mode

Pass `--mode` to skip the menu:

```bash
# Contour render (Luminet's original Greys_r tricontourf)
python main.py --mode luminet -N 20000 --no-display

# Scatter render (hot colormap, individual dots)
python main.py --mode scatter -N 20000 --no-display

# Isoradial curves
python main.py --mode isoradials --no-display

# All three modes at once
python main.py --mode all -N 15000 --no-display

# Export isoradials as SVG + G-code
python main.py --mode isoradials --export svg gcode --no-display

# Draft quality for quick preview
python main.py --mode scatter -N 10000 -q draft --no-display

# Publication quality
python main.py --mode luminet -N 10000 -q publication --no-display
```

---

## Flags

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--mode` | `-m` | choice | *(interactive)* | `luminet`, `scatter`, `isoradials`, `all` |
| `--particle-count` | `-N` | int | 10000 | Number of particles to sample from the disk |
| `--inclination` | `-i` | float | 80.0 | Observer angle from disk plane (degrees) |
| `--mass` | `-M` | float | 1.0 | Black hole mass in geometric units |
| `--power-scale` | `-p` | float | 0.9 | Flux power scaling (higher = more contrast) |
| `--levels` | `-l` | int | 100 | Contour levels for `luminet` mode |
| `--quality` | `-q` | choice | standard | `draft`, `standard`, `high`, `publication` |
| `--export` | `-e` | choice(s) | *(none)* | `svg` and/or `gcode` (scatter + isoradials only) |
| `--no-display` | | flag | false | Save only, do not open plot windows |
| `--save-path` | `-o` | str | *(auto)* | Custom output path for the image |

### Quality multipliers

Quality affects particle count and contour levels:

| Level | Particle multiplier | Level multiplier | Use case |
|-------|-------------------|-----------------|----------|
| `draft` | 0.1x | 0.2x | Quick preview, testing |
| `standard` | 1.0x | 1.0x | Normal renders |
| `high` | 2.0x | 2.0x | Detailed images |
| `publication` | 5.0x | 3.0x | Print-quality output |

For example, `-N 10000 -q high` renders 20,000 particles.

---

## Session output

Every run creates a timestamped session folder under `results/`:

```
results/20260328_141047/
  session.json
  luminet/contour_i80.0_N15000.png
  scatter/scatter_i80.0_N15000.png
  isoradials/isoradials_i80.0.png
  plotter/
    isoradials.svg
    isoradials.gcode
    scatter.svg
    scatter.gcode
```

### session.json

Records parameters, timing, and the list of generated files:

```json
{
  "started_at": "2026-03-28T14:10:47.123456",
  "completed_at": "2026-03-28T14:12:23.654321",
  "duration_seconds": 96.53,
  "params": {
    "mass": 1.0,
    "inclination": 80.0,
    "particle_count": 15000,
    "power_scale": 0.9,
    "levels": 100,
    "quality": "standard"
  },
  "files": [
    "results/20260328_141047/scatter/scatter_i80.0_N15000.png",
    "results/20260328_141047/plotter/scatter.svg",
    "results/20260328_141047/plotter/scatter.gcode"
  ],
  "status": "completed"
}
```

### Listing sessions

```python
from eventHorizon import list_sessions
for s in list_sessions():
    print(s['timestamp'], s.get('status'), s.get('duration_seconds'))
```

### Archiving old output

```python
from eventHorizon import archive_loose_files
moved = archive_loose_files()
print(f"Moved {moved} items to results/_archive/")
```

---

## Examples

### Generate a quick scatter preview

```bash
python main.py -m scatter -N 5000 -q draft --no-display
```

### High-quality contour for a poster

```bash
python main.py -m luminet -N 10000 -q publication -i 85 --no-display
```

### All modes with plotter export

```bash
python main.py -m all -N 15000 --export svg gcode --no-display
```

### Edge-on view

```bash
python main.py -m scatter -N 20000 -i 89 --no-display
```

### Face-on view (looking straight down at the disk)

```bash
python main.py -m scatter -N 20000 -i 10 --no-display
```
