# KitchenKonnect

![CI](https://github.com/StevOti/KitchenKonnect/actions/workflows/ci.yml/badge.svg)

KitchenKonnect is a Django-based platform to generate AI-aware meal recommendations, store recipes, and provide a social feed and nutritionist portal.

Status
- Core backend scaffolded with Django 5.
- Supabase-ready DB configuration and deployment docs added.
- DRF-based user registration and session/JWT auth endpoints scaffolded.
- Basic API tests and GitHub Actions CI to run them on push/PR.

Getting started (local development)

1. Clone the repo

```bash
git clone https://github.com/StevOti/KitchenKonnect.git
cd KitchenKonnect/kitchen_konnect
```

2. Create virtual environment and install deps

```bash
python -m venv venv
# PowerShell
.\venv\Scripts\Activate.ps1
# or cmd
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Configure environment
- Copy `.env.example` to `.env` and fill values, or create `.env` with production values.
- For local quick start we default to SQLite in `.env`.

4. Migrate and run

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Auth endpoints
- `POST /api/auth/register/` — register new user
- `POST /api/auth/token/` — obtain JWT token (if SimpleJWT installed)
- `POST /api/auth/token/refresh/` — refresh token (if available)
- `GET /api/auth/me/` — get current user (auth required)

Testing

```bash
python manage.py test users
```

Frontend dev quick start (Vite + React)

```bash
cd frontend
npm install
npm run dev
```

Open the dev server (default http://localhost:5173) and use the test UI to register, login (session), and fetch `/api/users/me/`.

Deployment (Supabase + Docker)
- See `deployment/README.md` for step-by-step instructions including `.env` examples, Docker compose for production, and Supabase tips.

Useful files
- `config/settings.py` — Django settings with `dj-database-url` support
- `docker-compose.prod.yml` — production docker compose with `migrator` and `web` services
- `Dockerfile.prod` — production image
- `deployment/README.md` — deployment notes and commands
- `users/` — user app (models, serializers, views, tests)

Next steps
- Continue Week 1 plan: complete app models (recipes, health), then Week 2 AI integration.
- Add front-end PWA, media storage integration, and scale DB to managed Postgres for production traffic.

If you'd like, I can:
- Add a GitHub Pages / status badge variant, or update badge owner if repo moves.
- Add a CI step for linting or coverage.

Recent changes
------------
- Frontend: added `Login`, `Register`, and `Home` pages under `frontend/src/`.
- Routing updated so the login page is the app entry (`/`), register at `/register`, and home at `/home`.
- Token handling: client now supports DRF Token and JWT (`access`) responses and validates tokens before redirecting.
- Backend: Supabase `DATABASE_URL` support and docs; compatibility shim applied for template context on Python 3.14.

New (2026-01-06)
-----------------
- Role & groups: users are classified by `role` (`regular`, `nutritionist`, `regulator`, `admin`). Django `Group` membership is synchronized with `role` on user save (`users`, `regulators`, `admins`).
- Regulators: `admin_level` minimum is now 50 so regulator users can access regulator/admin-level endpoints.
- Group sync command: added management command `python manage.py sync_groups` (supports `--dry-run` and `--username`) to one-off sync existing DB rows into groups.
- Frontend toasts: lightweight toast system added (`frontend/src/Toasts.jsx`) and wired to admin actions and verification flows.

How to sync existing users into groups
-------------------------------------
Run a dry-run first to preview changes:
```
cd kitchen_konnect
python manage.py sync_groups --dry-run
```
Apply changes:
```
python manage.py sync_groups
```

Notes
-----
- The `sync_groups` command creates/uses three groups: `users`, `regulators`, and `admins`.
- Approving a verification request for a regulator will set the user's `admin_level` to at least 50.
- No schema migration is necessary for these behavioral changes; they run at the application level.

Security / env note
-------------------
- Do NOT commit your `.env` file. It may contain database passwords and other secrets.
- This repo now ignores `.env` via `.gitignore`. If you committed `.env` previously, remove it from the repo history and rotate secrets.

If anything above looks wrong or you'd like a different commit history, tell me and I can squash or reword commits before pushing.

Auth / Production Checklist
---------------------------
- **Dependencies:** ensure `djangorestframework-simplejwt` is installed in production (already listed in `kitchen_konnect/requirements.txt`).
- **Environment variables:** set secure values in environment or secret store (examples): `SECRET_KEY`, `DATABASE_URL`, `DJANGO_ALLOWED_HOSTS`, `REDIS_URL` (if using token blacklisting), `SIMPLE_JWT_SIGNING_KEY` (optional if rotating keys), and any cloud storage keys.
- **Token endpoints & usage:** the API supports both JWT (preferred) and DRF Token fallback. In production, prefer JWT (obtain at `POST /api/auth/token/`, refresh at `POST /api/auth/token/refresh/`).
- **HTTPS & Cookies:** enable `SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`, and `CSRF_COOKIE_SECURE = True` so tokens/cookies are only sent over HTTPS.
- **CORS & Allowed Hosts:** set `CORS_ALLOWED_ORIGINS` to your frontend origin(s) and configure `ALLOWED_HOSTS` appropriately.
- **Token rotation & blacklisting:** consider enabling token rotation and blacklist (via `django-redis` + `simplejwt` settings) if you need immediate revoke behavior.
- **Key rotation:** if you use asymmetric signing (RSA), plan and automate key rotation; for HMAC signing keep `SIMPLE_JWT_SIGNING_KEY` secret and rotate periodically.
- **Rate limiting & brute-force protection:** add rate-limiting on auth endpoints (via `django-ratelimit` or API gateway) to mitigate credential stuffing.
- **Logging & monitoring:** log auth failures, suspicious IPs, and set up alerts for repeated failures.
- **Database backups & secrets rotation:** ensure DB backups are scheduled and secrets (DB passwords, API keys) are rotated per policy.

Quick deploy checklist
----------------------
- Confirm required packages are installed: `pip install -r kitchen_konnect/requirements.txt`.
- Set environment variables in your host (or use a secrets manager) before starting the app.
- Run migrations and any one-off commands: `python manage.py migrate && python manage.py sync_groups`.
- Verify token endpoints in a staging environment and test login/refresh flows before promoting to production.

If you want, I can add a `DEPLOYMENT.md` with exact sample environment variable values and a small checklist for rotating JWT keys and enabling token blacklisting.

Frontend font note
------------------
- The frontend is configured to prefer `Nimbus Mono` as the site font via `frontend/src/styles.css`.
- If you want the exact Nimbus Mono font bundled, add `@font-face` rules and include the font files in your build, or host them on a CDN and reference them from `index.html`.
- I can add a self-hosted font setup (font files + `@font-face`) if you provide the font files or a CDN URL.
