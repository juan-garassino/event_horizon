#!/usr/bin/env python3
"""
Black Hole Visualization — evenHorizon CLI

Usage:
    python main.py                                   # Interactive Rich menu
    python main.py --mode luminet -N 20000           # Direct contour render
    python main.py --mode scatter -N 20000           # Scatter dots
    python main.py --mode isoradials                 # Isoradial curves
    python main.py --mode all --no-display           # All three, headless
"""

import argparse
import sys
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path

# Import eventHorizon framework components
from eventHorizon import (
    draw_blackhole, plot_points, plot_scatter, plot_isoradials,
    plot_isoredshifts, plot_photon_sphere,
    save_figure_organized,
    start_session, end_session,
)

# ---------------------------------------------------------------------------
# Argument parser (always available for non-interactive use)
# ---------------------------------------------------------------------------

def create_argument_parser():
    parser = argparse.ArgumentParser(
        description='evenHorizon — Black Hole Renderer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s                                          # Interactive menu
  %(prog)s --mode luminet -N 20000 --no-display     # Contour render, no GUI
  %(prog)s --mode scatter -N 20000                  # Scatter dots
  %(prog)s --mode isoradials                        # Isoradial curves
  %(prog)s --mode all                               # All three modes
""",
    )
    parser.add_argument('--mode', '-m',
                        choices=['luminet', 'scatter', 'isoradials', 'all'],
                        default=None,
                        help='Visualization mode (omit for interactive menu)')
    parser.add_argument('--mass', '-M', type=float, default=1.0,
                        help='Black hole mass (default: 1.0)')
    parser.add_argument('--inclination', '-i', type=float, default=80.0,
                        help='Observer inclination in degrees (default: 80.0)')
    parser.add_argument('--particle-count', '-N', type=int, default=10000,
                        help='Number of particles (default: 10000)')
    parser.add_argument('--power-scale', '-p', type=float, default=0.9,
                        help='Power scale for flux (default: 0.9)')
    parser.add_argument('--levels', '-l', type=int, default=100,
                        help='Contour levels (default: 100)')
    parser.add_argument('--quality', '-q',
                        choices=['draft', 'standard', 'high', 'publication'],
                        default='standard',
                        help='Quality level (default: standard)')
    parser.add_argument('--no-display', action='store_true',
                        help='Save only, do not show plots')
    parser.add_argument('--save-path', '-o', type=str, default=None,
                        help='Custom output path')
    parser.add_argument('--export', '-e', nargs='+',
                        choices=['svg', 'gcode'],
                        default=None,
                        help='Export plotter files (scatter/isoradials only)')
    return parser


# ---------------------------------------------------------------------------
# Quality multipliers
# ---------------------------------------------------------------------------

QUALITY_MULT = {
    'draft':       {'particles': 0.1,  'levels': 0.2},
    'standard':    {'particles': 1.0,  'levels': 1.0},
    'high':        {'particles': 2.0,  'levels': 2.0},
    'publication': {'particles': 5.0,  'levels': 3.0},
}


# ---------------------------------------------------------------------------
# Rich interactive menu
# ---------------------------------------------------------------------------

def interactive_menu():
    """Show Rich interactive menu and return (mode, params dict)."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm
    except ImportError:
        print("Rich is not installed. Install with: pip install rich")
        print("Falling back to --mode luminet defaults.")
        return 'luminet', {}

    console = Console()

    # Mode selection
    console.print("  [bold][1][/bold] Scatter      Individual particle dots (hot colormap)")
    console.print("  [bold][2][/bold] Contour      Smooth Luminet tricontourf (Greys_r)")
    console.print("  [bold][3][/bold] Isoradials   Constant-radius curves")
    console.print("  [bold][4][/bold] All modes    Generate all three")
    console.print()

    choice = Prompt.ask("  Select mode", choices=["1", "2", "3", "4"], default="2")
    mode_map = {"1": "scatter", "2": "luminet", "3": "isoradials", "4": "all"}
    mode = mode_map[choice]

    # Default parameters
    params = {
        'mass': 1.0,
        'inclination': 80.0,
        'particle_count': 10000,
        'power_scale': 0.9,
        'levels': 100,
        'quality': 'standard',
    }

    # Show parameter table
    console.print()
    table = Table(title="Current Parameters", border_style="dim")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Inclination", f"{params['inclination']}deg")
    table.add_row("Particle count", f"{params['particle_count']:,}")
    table.add_row("Mass", str(params['mass']))
    table.add_row("Quality", params['quality'])
    console.print(table)
    console.print()

    if Confirm.ask("  Modify parameters?", default=False):
        params['inclination'] = FloatPrompt.ask("  Inclination (degrees)", default=80.0)
        if mode in ('scatter', 'luminet', 'all'):
            params['particle_count'] = IntPrompt.ask("  Particle count", default=10000)
        params['mass'] = FloatPrompt.ask("  Mass", default=1.0)
        quality_choice = Prompt.ask("  Quality", choices=["draft", "standard", "high", "publication"], default="standard")
        params['quality'] = quality_choice

    # Export option for scatter/isoradials
    if mode in ('scatter', 'isoradials', 'all'):
        if Confirm.ask("  Export SVG/G-code for pen plotter?", default=False):
            export_choice = Prompt.ask("  Format", choices=["svg", "gcode", "both"], default="svg")
            if export_choice == "both":
                params['export'] = ['svg', 'gcode']
            else:
                params['export'] = [export_choice]

    return mode, params


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

def _apply_quality(params: dict) -> dict:
    """Apply quality multipliers to particle_count and levels."""
    q = params.get('quality', 'standard')
    mult = QUALITY_MULT.get(q, QUALITY_MULT['standard'])
    params['particle_count'] = max(500, int(params.get('particle_count', 10000) * mult['particles']))
    params['levels'] = max(20, int(params.get('levels', 100) * mult['levels']))
    return params


def _make_progress_callback():
    """Create a Rich progress callback if Rich is available, else return None."""
    try:
        from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
        progress = Progress(
            TextColumn("[cyan]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )
        task_id = None

        def callback(current, total):
            nonlocal task_id
            if task_id is None:
                progress.start()
                task_id = progress.add_task("Generating particles", total=total)
            progress.update(task_id, completed=current)
            if current >= total:
                progress.stop()

        return callback
    except ImportError:
        return None


def render_mode(mode: str, params: dict, save_path=None, export_formats=None) -> list:
    """Render the given mode and return list of (fig, label, elapsed) tuples."""
    from eventHorizon.utils.results_organization import get_active_session_path

    results = []
    mass = params.get('mass', 1.0)
    incl = params.get('inclination', 80.0)
    pc = params.get('particle_count', 10000)
    ps = params.get('power_scale', 0.9)
    levels = params.get('levels', 100)

    progress_cb = _make_progress_callback()
    extra = {'progress_callback': progress_cb} if progress_cb else {}

    # Export kwargs — only pass for modes that support it
    def _export_kwargs(supports_export: bool):
        if not supports_export or not export_formats:
            return {}
        export_dir = get_active_session_path() or "results"
        return {'export': export_formats, 'export_dir': str(Path(export_dir) / "plotter")}

    if mode in ('luminet', 'all'):
        t0 = time.time()
        fig, ax = draw_blackhole(
            mass=mass, inclination=incl, mode='luminet',
            particle_count=pc, power_scale=ps, levels=levels,
            show_ghost_image=True, **extra,
        )
        elapsed = time.time() - t0
        label = f"contour_i{incl}_N{pc}"
        if save_path and mode == 'luminet':
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
        else:
            save_figure_organized(fig, f"{label}.png", "luminet")
        results.append((fig, label, elapsed))

    if mode in ('scatter', 'all'):
        t0 = time.time()
        fig, ax = draw_blackhole(
            mass=mass, inclination=incl, mode='scatter',
            particle_count=pc, power_scale=ps,
            show_ghost_image=True, **extra, **_export_kwargs(True),
        )
        elapsed = time.time() - t0
        label = f"scatter_i{incl}_N{pc}"
        if save_path and mode == 'scatter':
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
        else:
            save_figure_organized(fig, f"{label}.png", "scatter")
        results.append((fig, label, elapsed))

    if mode in ('isoradials', 'all'):
        t0 = time.time()
        fig, ax = draw_blackhole(
            mass=mass, inclination=incl, mode='isoradials',
            radii=list(range(6, 51, 5)),
            **_export_kwargs(True),
        )
        elapsed = time.time() - t0
        label = f"isoradials_i{incl}"
        if save_path and mode == 'isoradials':
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='black')
        else:
            save_figure_organized(fig, f"{label}.png", "isoradials")
        results.append((fig, label, elapsed))

    return results


# ---------------------------------------------------------------------------
# Summary panel
# ---------------------------------------------------------------------------

def show_summary(results, session_path):
    """Print a Rich summary panel."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
    except ImportError:
        print(f"\nDone. Output in {session_path}")
        return

    console = Console()
    console.print()

    table = Table(border_style="dim", show_header=True)
    table.add_column("Mode", style="cyan")
    table.add_column("Time", style="yellow")

    total_time = 0.0
    for _fig, label, elapsed in results:
        table.add_row(label, f"{elapsed:.1f}s")
        total_time += elapsed

    body = table.__rich_console__(console, console.options)

    lines = [f"[bold]Session:[/bold] {session_path}"]
    lines.append(f"[bold]Total time:[/bold] {total_time:.1f}s")
    lines.append(f"[bold]Images:[/bold] {len(results)}")

    console.print(Panel(
        "\n".join(lines),
        title="[bold green]Render Complete[/bold green]",
        border_style="green",
    ))
    console.print(table)


# ---------------------------------------------------------------------------
# Startup title
# ---------------------------------------------------------------------------

def show_title():
    """Show the evenHorizon startup title using pyfiglet + Rich gradient."""
    try:
        import pyfiglet
        from rich.console import Console
        from rich.text import Text

        console = Console()
        console.print()

        art = pyfiglet.figlet_format("eventHorizon", font="small_slant")
        gradient = [
            "bright_cyan", "cyan", "dodger_blue", "blue",
            "medium_purple", "purple",
        ]

        for i, line in enumerate(art.rstrip("\n").split("\n")):
            color = gradient[i % len(gradient)]
            console.print(Text(line, style=f"bold {color}"), highlight=False)

        console.print()
        console.print("  [dim]Recreating Luminet's 1979 black hole image[/dim]")
        console.print()

    except ImportError:
        print("\n  eventHorizon")
        print("  Recreating Luminet's 1979 black hole image\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    # Always show the title banner
    show_title()

    # Decide interactive vs CLI
    if args.mode is None:
        mode, params = interactive_menu()
    else:
        mode = args.mode
        params = {
            'mass': args.mass,
            'inclination': args.inclination,
            'particle_count': args.particle_count,
            'power_scale': args.power_scale,
            'levels': args.levels,
            'quality': args.quality,
        }

    # Apply quality
    params = _apply_quality(params)

    # Use non-interactive backend if --no-display
    no_display = getattr(args, 'no_display', False)
    if no_display:
        matplotlib.use('Agg')

    plt.style.use('dark_background')

    # Start session
    session_path = start_session(params=params)

    print(f"Mode: {mode} | Particles: {params.get('particle_count', 'N/A')} | "
          f"Inclination: {params.get('inclination')}deg | Quality: {params.get('quality')}")
    print(f"Session: {session_path}")
    print("-" * 60)

    try:
        export_fmts = getattr(args, 'export', None) or params.get('export')
        results = render_mode(mode, params,
                              save_path=args.save_path if hasattr(args, 'save_path') else None,
                              export_formats=export_fmts)
        end_session()

        show_summary(results, session_path)

        if not no_display:
            plt.show()
        else:
            # Close all figures to free memory
            for fig, _, _ in results:
                plt.close(fig)

    except KeyboardInterrupt:
        end_session()
        print("\nInterrupted.")
        sys.exit(1)
    except Exception as e:
        end_session()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
