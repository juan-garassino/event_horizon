"""
Result organization utilities for eventHorizon package.

This module provides helper functions for organizing visualization outputs
into well-structured directory hierarchies with session-based timestamped folders.
"""
import os
import json
import shutil
import datetime
from typing import Optional, Dict, Any, List
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
_active_session_path: Optional[str] = None
_session_start_time: Optional[datetime.datetime] = None
_session_params: Optional[Dict[str, Any]] = None
_session_files: List[str] = []


def start_session(
    base_path: str = "results",
    params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Start a new visualization session with a timestamped folder.

    Creates ``results/<YYYYMMDD_HHMMSS>/`` and writes ``session.json``
    with the run parameters.

    Parameters
    ----------
    base_path : str
        Root results directory.
    params : dict, optional
        Parameters to record in session.json.

    Returns
    -------
    str
        Path to the session directory.
    """
    global _active_session_path, _session_start_time, _session_params, _session_files

    _session_start_time = datetime.datetime.now()
    timestamp = _session_start_time.strftime("%Y%m%d_%H%M%S")
    _active_session_path = os.path.join(base_path, timestamp)
    _session_params = params or {}
    _session_files = []

    os.makedirs(_active_session_path, exist_ok=True)

    # Write initial session.json
    session_meta = {
        "started_at": _session_start_time.isoformat(),
        "params": _session_params,
        "status": "running",
    }
    _write_json(os.path.join(_active_session_path, "session.json"), session_meta)

    return _active_session_path


def end_session() -> Optional[str]:
    """
    Finalize the active session — update session.json with completion time
    and list of generated files, then reset state.

    Returns
    -------
    str or None
        Path to the session directory, or None if no session was active.
    """
    global _active_session_path, _session_start_time, _session_params, _session_files

    if _active_session_path is None:
        return None

    completed_at = datetime.datetime.now()
    session_json_path = os.path.join(_active_session_path, "session.json")

    session_meta = {
        "started_at": _session_start_time.isoformat() if _session_start_time else None,
        "completed_at": completed_at.isoformat(),
        "duration_seconds": (completed_at - _session_start_time).total_seconds() if _session_start_time else None,
        "params": _session_params,
        "files": _session_files,
        "status": "completed",
    }
    _write_json(session_json_path, session_meta)

    path = _active_session_path
    _active_session_path = None
    _session_start_time = None
    _session_params = None
    _session_files = []
    return path


def get_active_session_path() -> Optional[str]:
    """Return the active session directory, or None."""
    return _active_session_path


# ---------------------------------------------------------------------------
# Saving figures
# ---------------------------------------------------------------------------

def save_figure_organized(
    fig: plt.Figure,
    filename: str,
    category: str = "examples",
    subcategory: Optional[str] = None,
    base_path: str = "results",
    dpi: int = 200,
    **kwargs,
) -> str:
    """
    Save a matplotlib figure.

    If a session is active the file is saved under
    ``<session_path>/<category>/<filename>``.  Otherwise falls back to
    ``<base_path>/<category>/<filename>``.

    Parameters
    ----------
    fig : plt.Figure
        Figure to save.
    filename : str
        Filename (without directory).
    category : str
        Subdirectory inside the session folder (e.g. "luminet", "traditional").
    subcategory : str, optional
        Additional nesting level.
    base_path : str
        Fallback root when no session is active.
    dpi : int
        Image resolution.

    Returns
    -------
    str
        Full path to the saved file.
    """
    if _active_session_path is not None:
        root = _active_session_path
    else:
        root = base_path

    if subcategory:
        directory = os.path.join(root, category, subcategory)
    else:
        directory = os.path.join(root, category)

    os.makedirs(directory, exist_ok=True)
    full_path = os.path.join(directory, filename)
    fig.savefig(full_path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor(), **kwargs)

    _session_files.append(full_path)
    return full_path


# ---------------------------------------------------------------------------
# Backward-compatible helpers
# ---------------------------------------------------------------------------

def create_results_structure(base_path: str = "results") -> Dict[str, str]:
    """
    Create a results directory structure.  Now delegates to start_session().

    Returns
    -------
    Dict[str, str]
        Dictionary mapping category names to directory paths.
    """
    session_path = start_session(base_path=base_path)
    return {"base": base_path, "session": session_path}


def create_session_summary(results_dirs: Dict[str, str], session_info: Dict[str, Any]) -> str:
    """Create a summary file for a visualization session."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_content = f"# eventHorizon Session Summary\n\n**Date:** {timestamp}\n"
    for key, val in session_info.items():
        summary_content += f"- **{key}:** {val}\n"

    base = results_dirs.get("session", results_dirs.get("base", "results"))
    summary_path = os.path.join(base, "session_summary.md")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w") as f:
        f.write(summary_content)
    return summary_path


def get_organized_path(
    filename: str,
    category: str = "examples",
    subcategory: Optional[str] = None,
    base_path: str = "results",
) -> str:
    """Get an organized path for saving files."""
    root = _active_session_path if _active_session_path else base_path
    if subcategory:
        directory = os.path.join(root, category, subcategory)
    else:
        directory = os.path.join(root, category)
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, filename)


# ---------------------------------------------------------------------------
# Listing & cleanup
# ---------------------------------------------------------------------------

def list_sessions(base_path: str = "results") -> List[Dict[str, Any]]:
    """
    List all sessions, newest first.

    Returns
    -------
    list of dict
        Each dict has 'path', 'timestamp', and 'params' (if session.json exists).
    """
    if not os.path.isdir(base_path):
        return []

    sessions = []
    for entry in sorted(os.listdir(base_path), reverse=True):
        entry_path = os.path.join(base_path, entry)
        session_json = os.path.join(entry_path, "session.json")
        if os.path.isdir(entry_path) and os.path.isfile(session_json):
            try:
                with open(session_json) as f:
                    meta = json.load(f)
                sessions.append({"path": entry_path, "timestamp": entry, **meta})
            except (json.JSONDecodeError, OSError):
                sessions.append({"path": entry_path, "timestamp": entry})
    return sessions


def list_generated_files(base_path: str = "results") -> Dict[str, list]:
    """List all generated image files in the results directory."""
    files_by_category: Dict[str, list] = {}
    if not os.path.exists(base_path):
        return files_by_category
    for root, _dirs, files in os.walk(base_path):
        rel_path = os.path.relpath(root, base_path)
        image_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg', '.pdf', '.svg'))]
        if image_files:
            files_by_category[rel_path] = image_files
    return files_by_category


def cleanup_old_results(base_path: str = "results", days_old: int = 7) -> int:
    """Remove files older than *days_old* days."""
    import time
    if not os.path.exists(base_path):
        return 0
    cutoff_time = time.time() - (days_old * 24 * 60 * 60)
    removed_count = 0
    for root, _dirs, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    removed_count += 1
                except OSError:
                    pass
    return removed_count


def archive_loose_files(base_path: str = "results") -> int:
    """
    Move root-level PNGs and old flat folders into ``results/_archive/``.

    Returns number of items moved.
    """
    if not os.path.isdir(base_path):
        return 0

    archive_dir = os.path.join(base_path, "_archive")
    moved = 0

    for entry in os.listdir(base_path):
        entry_path = os.path.join(base_path, entry)

        # Skip session dirs (timestamped), _archive itself
        if entry.startswith("_") or entry == "_archive":
            continue
        # Timestamp dirs like 20260328_120000 — skip
        if len(entry) == 15 and entry[8] == "_":
            continue

        # Move loose PNGs
        if os.path.isfile(entry_path) and entry.lower().endswith(('.png', '.jpg', '.jpeg')):
            os.makedirs(archive_dir, exist_ok=True)
            shutil.move(entry_path, os.path.join(archive_dir, entry))
            moved += 1
        # Move old flat directories (session_*, examples, tests, etc.)
        elif os.path.isdir(entry_path) and not os.path.isfile(os.path.join(entry_path, "session.json")):
            os.makedirs(archive_dir, exist_ok=True)
            dest = os.path.join(archive_dir, entry)
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.move(entry_path, dest)
            moved += 1

    return moved


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _write_json(path: str, data: Any) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
