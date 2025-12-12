#!/usr/bin/env python3
"""
Render wrapper for the PLEX dashboard.

Render runs: gunicorn app:app

This file:
1) clones the real dashboard repo (if missing)
2) installs its requirements
3) imports dashboard's create_app() WITHOUT colliding with this wrapper module name
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = BASE_DIR / "create-an-interactive-data-dashboard-with-python"
DASHBOARD_REPO_URL = "https://github.com/dorian-sotpyrc/create-an-interactive-data-dashboard-with-python.git"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"[render-wrapper] Running: {' '.join(cmd)} (cwd={cwd or BASE_DIR})")
    subprocess.run(cmd, cwd=str(cwd or BASE_DIR), check=True)


def ensure_dashboard_repo() -> None:
    if not DASHBOARD_DIR.exists():
        print(f"[render-wrapper] Cloning dashboard repo into {DASHBOARD_DIR} ...")
        run(["git", "clone", DASHBOARD_REPO_URL, str(DASHBOARD_DIR)])
    else:
        print(f"[render-wrapper] Dashboard repo already present at {DASHBOARD_DIR}")

    req_path = DASHBOARD_DIR / "requirements.txt"
    if req_path.exists():
        print(f"[render-wrapper] Installing dashboard requirements from {req_path} ...")
        run([sys.executable, "-m", "pip", "install", "-r", str(req_path)], cwd=DASHBOARD_DIR)


def import_dashboard_create_app():
    """
    Import dashboard's app package as a uniquely named module to avoid colliding
    with this wrapper file called app.py.
    """
    pkg_init = DASHBOARD_DIR / "app" / "__init__.py"
    if not pkg_init.exists():
        raise RuntimeError(f"Expected dashboard create_app at {pkg_init}, but it does not exist.")

    spec = importlib.util.spec_from_file_location("dashboard_app", str(pkg_init))
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to create import spec for dashboard_app")

    dashboard_app = importlib.util.module_from_spec(spec)
    sys.modules["dashboard_app"] = dashboard_app
    spec.loader.exec_module(dashboard_app)

    if not hasattr(dashboard_app, "create_app"):
        raise RuntimeError("dashboard_app does not expose create_app()")

    return dashboard_app.create_app


# Ensure Render PORT is present (Render injects it, but keep a default for local)
os.environ.setdefault("PORT", "10000")

ensure_dashboard_repo()
create_app = import_dashboard_create_app()

# Gunicorn looks for this
app = create_app()

if __name__ == "__main__":
    # Local dev fallback
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
