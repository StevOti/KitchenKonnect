# Deployment — KitchenKonnect

This document describes deploying KitchenKonnect with Supabase Postgres and Docker.

Prerequisites
- Docker & Docker Compose
- Supabase project with Postgres (connection string)
- Project `ENV` variables configured (see below)

Environment variables
Create a `.env` file (or set env vars in your host/CI) with the following values.

Example `.env` (Supabase)

```
SECRET_KEY=replace-with-secure-value
DEBUG=False
ALLOWED_HOSTS=your.domain.com

# Supabase connection string (preferred)
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.argcoarikrzgblzpyyrs.supabase.co:5432/postgres

# or individual DB settings (not required if using DATABASE_URL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=[YOUR_PASSWORD]
DB_HOST=db.argcoarikrzgblzpyyrs.supabase.co
DB_PORT=5432

# Other secrets
OPENAI_API_KEY=your_openai_key

# Django static/media
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=...
```

Notes:
- Use `DATABASE_URL` for simplicity. It will be picked up by `dj-database-url` in `config/settings.py` and configured with SSL.
- Keep the `.env` file secret. Use provider secret managers in production.

Install requirements (if building locally)

```bash
python -m venv venv
source venv/bin/activate   # or `.\venv\Scripts\Activate.ps1` on Windows PowerShell
pip install -r requirements.txt
```

Running migrations & collectstatic (Docker)

Build the production image and run the migrator (this will install requirements in the image):

```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml run --rm migrator
```

Run the web service

```bash
docker compose -f docker-compose.prod.yml up -d web
```

Running migrations without Docker (from your host)

Ensure `.env` is present and then run:

```bash
# activate virtualenv first
python manage.py migrate
python manage.py collectstatic --noinput
```

Notes for CI/CD
- Run `docker compose -f docker-compose.prod.yml run --rm migrator` as a release step before switching traffic to the new image.
- Store secrets in your CI provider's secret manager and inject `DATABASE_URL` and `SECRET_KEY` at runtime.

Supabase-specific tips
- Use the provided connection string from the Supabase Project Settings → Database → Connection string.
- Supabase requires SSL; `dj-database-url` is configured to require SSL for `DATABASE_URL`.
- Monitor connections and use pooling if you scale workers.

Backup & monitoring
- Enable automated backups in Supabase and test a restore periodically.
- Monitor database metrics (connections, CPU, queries).

Troubleshooting
- If migrations fail with SSL errors, ensure `DATABASE_URL` includes `?sslmode=require` or that `sslmode=require` is set in parsed options.

--
KitchenKonnect deployment notes — up to migrations and basic run