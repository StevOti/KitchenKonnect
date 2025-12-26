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

Security / env note
-------------------
- Do NOT commit your `.env` file. It may contain database passwords and other secrets.
- This repo now ignores `.env` via `.gitignore`. If you committed `.env` previously, remove it from the repo history and rotate secrets.

If anything above looks wrong or you'd like a different commit history, tell me and I can squash or reword commits before pushing.
