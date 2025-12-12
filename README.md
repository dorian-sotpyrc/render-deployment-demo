
# render-deployment-demo

A tiny Render deployment wrapper that runs the PLEX interactive dashboard from:

- https://github.com/dorian-sotpyrc/create-an-interactive-data-dashboard-with-python

Instead of duplicating code, this repo deploys a **small wrapper Flask entrypoint** that:

1. Clones the dashboard repo at runtime (if not present)
2. Installs the dashboard’s dependencies
3. Imports the dashboard’s `create_app()` safely (no module name collisions)
4. Serves it on Render using Gunicorn

It’s essentially a *linking clone* used to automate deployment.

---

## How it works

Render runs this repo’s start command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
````

That imports `app.py` in this repo (the wrapper). The wrapper then:

1. Clones the dashboard repo into a subfolder:

```bash
create-an-interactive-data-dashboard-with-python/
```

2. Installs the dashboard’s dependencies from its `requirements.txt`.

3. Loads the dashboard’s Flask factory from:

```text
create-an-interactive-data-dashboard-with-python/app/__init__.py
```

4. Exposes a WSGI app called `app` (so Gunicorn can serve it).

---

## Local development (optional)

You can reproduce the Render-style startup locally:

```bash
git clone https://github.com/dorian-sotpyrc/render-deployment-demo.git
cd render-deployment-demo

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# Run the wrapper (it will clone + install the dashboard on first run)
PORT=8000 gunicorn app:app --bind 0.0.0.0:8000
```

Open:

* [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Deploying on Render

1. In Render, click **New +** → **Web Service** (or **Blueprint** if you prefer).
2. Connect this repo:

   * `dorian-sotpyrc/render-deployment-demo`
3. Use these settings:

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

4. Deploy and open the generated `*.onrender.com` URL.

---

## Notes / gotchas

* If you update the dashboard repo, redeploy this Render service to pull the latest code.
* This wrapper avoids circular-import issues by importing the dashboard package under a different module name internally.

