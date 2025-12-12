#!/usr/bin/env python3
"""
Render wrapper app for the PLEX dashboard.

This tiny Flask entrypoint does three things on startup:

1. Clones the real dashboard repo (if it isn't present yet).
2. Installs the dashboard's Python dependencies from its requirements.txt.
3. Imports the dashboard's Flask app factory and exposes `app` for Gunicorn.

Render runs `gunicorn app:app`, so this file is the only thing
the Render service needs to know about.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = BASE_DIR / "create-an-interactive-data-dashboard-with-python"
DASHBOARD_REPO_URL = "https://github.com/dorian-sotpyrc/create-an-interactive-data-dashboard-with-python.git"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a shell command with basic logging and error propagation."""
    print(f"[render-wrapper] Running: {' '.join(cmd)} (cwd={cwd or BASE_DIR})")
    subprocess.run(cmd, cwd=str(cwd or BASE_DIR), check=True)


def ensure_dashboard_repo() -> None:
    """Clone the dashboard repo and install its requirements if needed."""
    if not DASHBOARD_DIR.exists():
        print(f"[render-wrapper] Cloning dashboard repo into {DASHBOARD_DIR} ...")
        run(["git", "clone", DASHBOARD_REPO_URL, str(DASHBOARD_DIR)])
    else:
        print(f"[render-wrapper] Dashboard repo already present at {DASHBOARD_DIR}")

    req_path = DASHBOARD_DIR / "requirements.txt"
    if req_path.exists():
        print(f"[render-wrapper] Installing dashboard requirements from {req_path} ...")
        run([sys.executable, "-m", "pip", "install", "-r", str(req_path)], cwd=DASHBOARD_DIR)
    else:
        print("[render-wrapper] WARNING: No requirements.txt found in dashboard repo; "
              "assuming dependencies are already satisfied.")


# Ensure the dashboard code + deps are ready before importing.
ensure_dashboard_repo()

# Make the dashboard repo importable as a top-level module.
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

# The dashboard repo exposes its Flask app via app.create_app().
#   create-an-interactive-data-dashboard-with-python/
#     ├── app.py          # entrypoint
#     └── app/__init__.py # create_app()
from app import create_app  # type: ignore

# Gunicorn will look for this.
app = create_app()

# Optional local dev entrypoint
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
