# render-deployment-demo

A tiny Render deployment wrapper that runs the PLEX marketing dashboard app from:

- https://github.com/dorian-sotpyrc/create-an-interactive-data-dashboard-with-python

Instead of duplicating code, this repo:

1. Clones the dashboard repo during the Render build.
2. Installs its dependencies.
3. Serves it with `gunicorn` on the Render free tier.

It is essentially a *linking clone* used to automate deployment.

---

## How it works

On Render, the service defined in `render.yaml` does the following:

1. Install this repo’s minimal dependency:

   ```bash
   pip install -r requirements.txt
````

2. Clone the dashboard project into a subfolder:

   ```bash
   git clone https://github.com/dorian-sotpyrc/create-an-interactive-data-dashboard-with-python.git dashboard_app
   ```

3. Install the dashboard’s own dependencies:

   ```bash
   pip install -r dashboard_app/requirements.txt
   ```

4. Start the app with `gunicorn`, pointing at the dashboard’s app factory:

   ```bash
   gunicorn 'dashboard_app.app:create_app()'
   ```

The result: your Render service runs the full interactive data dashboard, even though this repo only contains a couple of config files.

---

## Local development (optional)

If you want to reproduce the Render setup locally:

```bash
# Clone this wrapper repo
git clone https://github.com/dorian-sotpyrc/render-deployment-demo.git
cd render-deployment-demo

# Install minimal dependency for this wrapper
pip install -r requirements.txt

# Clone the dashboard app into a subfolder
git clone https://github.com/dorian-sotpyrc/create-an-interactive-data-dashboard-with-python.git dashboard_app

# Install the dashboard's dependencies
pip install -r dashboard_app/requirements.txt

# Run with gunicorn the same way Render does
gunicorn 'dashboard_app.app:create_app()'
```

Then open:

* Home/dashboard: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

(Adjust the host/port flags if you want a different binding.)

You can also work directly in the dashboard repo itself for day-to-day development:

```bash
cd dashboard_app
python app.py
```

---

## Deploying on Render

1. Push this repo to GitHub (already done for `dorian-sotpyrc/render-deployment-demo`).
2. In Render:

   * Click **New +** → **Blueprint**.
   * Point Render at `https://github.com/dorian-sotpyrc/render-deployment-demo.git`.
3. Render will detect `render.yaml` and create a web service using that configuration.
4. Wait for the deploy to go **Live**, then open the generated URL – you’ll be looking at the interactive data dashboard app.

Any time you push updates to the dashboard repo, you can:

* Trigger a redeploy of this service in Render (it will pull the latest dashboard code next build), or
* Pin to a specific branch/commit by editing the `git clone` line in `render.yaml`.

