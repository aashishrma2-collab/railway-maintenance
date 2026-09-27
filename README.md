# Railway Maintenance Optimization — Prototype

An AI-assisted decision-support layer for railway maintenance scheduling:
risk/priority scoring, corridor task discovery, equipment mobilization &
backward-scheduling feasibility checks, and a human approval workflow.

**This does not replace signalling, interlocking, block-proving, or existing
approval procedures.** It recommends; authorized personnel approve.

All data (tasks, equipment, depots, users) is synthetic/demo data created
for this prototype — not real Indian Railways data.

## Architecture

- **Backend:** Python + FastAPI, JWT auth (bcrypt-hashed passwords), SQLAlchemy ORM
- **Database:** SQLite by default — a single file, zero extra services to install
  or run. Swap to PostgreSQL any time by changing one env var (`DATABASE_URL`) —
  nothing else in the code changes.
- **Frontend:** plain HTML/CSS/JS (no Node.js/npm build step), served by the
  same FastAPI process on the same origin as the API
- **No Docker, no containers.** Just a Python virtual environment. This runs
  identically on Ubuntu, Windows, and macOS wherever Python 3.10+ is installed.

## Prerequisite (once, on whichever machine runs the server)

Install **Python 3.10 or newer**:
- Ubuntu: `sudo apt update && sudo apt install -y python3 python3-venv python3-pip`
- Windows: download from [python.org](https://www.python.org/downloads/) — tick
  **"Add Python to PATH"** during install.

Nothing else needs installing. Whoever *opens the link in a browser* later
needs nothing at all — not even Python.

## Run it locally

**Ubuntu / macOS / WSL:**
```bash
cd railway-app
./run.sh
```

**Windows (Command Prompt or PowerShell):**
```bat
cd railway-app
run.bat
```

Either script: creates a virtual environment, installs dependencies, copies
`.env.example` to `.env` on first run, creates the database, seeds demo data,
and starts the server. Open `http://localhost:8000` in a browser.

Demo logins seeded automatically:
- `admin` / `admin123` (Admin role)
- `planner1` / `planner123` (Planner role — can run feasibility + approve)

You can also register your own account from the login screen with any role
(Engineering / S&T / Electrical / Operations / Planner / Officer / Admin).

Stop the server with `Ctrl+C`. Your data persists in `backend/data/railway.db`
between runs — run the script again later and everything is still there.

## Demo scenario (built into the seed data)

- Anchor task: Track Maintenance, KM 100 (Engineering, High priority)
- Corridor discovery finds S&T Inspection KM 112 and Electrical Inspection KM 118
  (both within the ±20 KM search radius)
- Running feasibility from the Corridor & Feasibility page:
  - Engineering and S&T tasks come back **FEASIBLE** (mobilization fits the
    300-minute block window)
  - Electrical comes back **NOT FEASIBLE** — the OHE Tower Car's 190-minute
    travel time alone pushes total required time past the window
  - This demonstrates the core point: geographic proximity is only a
    candidate-discovery signal, never a reason to bundle tasks on its own.

## Making it reachable by someone else, from their own device

Running `run.sh` / `run.bat` only serves your own machine until you do one of
the following — none of them require Docker:

### Option A — Deploy to a cloud platform, no server management (easiest)
Render, Railway, and PythonAnywhere can all run a plain Python app directly
from your GitHub repo (no Dockerfile needed — they detect `requirements.txt`
and run a start command you give them):
- **Build command:** `pip install -r backend/requirements.txt`
- **Start command:** `cd backend && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set the environment variables from `.env.example` in their dashboard
  (`JWT_SECRET` especially — generate a long random value).
- They give you a public HTTPS URL immediately after the first successful build.
- **Note on free tiers:** some free plans use ephemeral disks, so a SQLite file
  can be wiped on redeploy/restart. For anything beyond a demo, either use
  their paid persistent-disk tier, or point `DATABASE_URL` at a managed
  Postgres add-on (most of these platforms offer one) — the code already
  supports both, so it's a one-line env var change either way.

### Option B — Your own Ubuntu server (a VPS you rent, or a college server)
Run it as a proper background service with `systemd`, then put Nginx in front
for HTTPS:
1. Copy the project to the server, run `./run.sh` once to confirm it starts,
   then `Ctrl+C`.
2. Create `/etc/systemd/system/railway-app.service`:
   ```ini
   [Unit]
   Description=Railway Maintenance Optimization
   After=network.target

   [Service]
   WorkingDirectory=/path/to/railway-app/backend
   EnvironmentFile=/path/to/railway-app/.env
   ExecStart=/path/to/railway-app/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always
   User=www-data

   [Install]
   WantedBy=multi-user.target
   ```
3. `sudo systemctl enable --now railway-app` — it now runs on boot and restarts
   if it crashes.
4. Put Nginx in front for HTTPS (`sudo apt install nginx certbot python3-certbot-nginx`),
   proxying your domain to `127.0.0.1:8000`, then `sudo certbot --nginx` for a
   free TLS certificate. Share `https://yourdomain.com`.

### Option C — Windows Server
Use **NSSM** (Non-Sucking Service Manager, a free tool) to wrap
`backend\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000`
as a proper Windows Service that starts on boot, or simply run `run.bat` in a
scheduled task set to run at startup. Open port 8000 (or 443, if you put IIS
or Caddy in front for HTTPS) in Windows Firewall.

### Option D — Quick, temporary sharing while developing
Run it locally (`run.sh` / `run.bat`) and tunnel it with `ngrok http 8000` (or
Cloudflare Tunnel) to get a temporary public HTTPS URL — good for a hackathon
demo, not for judged production use.

Any of A–C gives you a link that works from any browser, on any device
(desktop, laptop, Android, iOS Safari) — nobody else needs Python or anything
else installed; only the machine actually running the server does.

## What's implemented vs. deferred

**Implemented:** login/register with real hashed passwords + JWT + roles,
task entry with explainable weighted risk scoring, corridor discovery,
equipment-aware backward-scheduling feasibility engine, recommendation +
role-gated approval workflow, dashboard summary.

**Deferred for a follow-up pass** (structured to slot in cleanly): What-if
re-optimization, Planned-vs-Actual execution feedback loop, multi-block
OR-Tools optimization (current engine is a transparent, documented
rule-based stand-in — see `backend/app/feasibility.py`), Reports page,
Admin/user-management UI, corridor map visualization, train/block movement
data integration.

## API reference

Interactive docs are auto-generated at `http://localhost:8000/docs` (Swagger UI)
once the server is running — every endpoint, its inputs, and try-it-out included.

## Security notes for going beyond a hackathon demo

- Set a strong random `JWT_SECRET` in `.env` before any real deployment
- Put the app behind HTTPS (Nginx/Caddy + Let's Encrypt, or your host's managed TLS)
- Restrict CORS (`backend/app/main.py`) to your actual frontend origin instead of `*`
- Move from SQLite to PostgreSQL for concurrent multi-user production load
- Add rate limiting and audit logging on the approval endpoints
