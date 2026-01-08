Deployment checklist and recommended environment variables
=========================================================

This file describes the key environment variables and recommended production settings
for deploying KitchenKonnect in a secure configuration.

Important general guidance
- Always run under HTTPS (TLS) behind a reverse proxy or load balancer.
- Keep `DEBUG=False` in production and ensure a strong `SECRET_KEY` is set.
- Use a managed Postgres or equivalent DB for production; ensure backups.

Required / strongly-recommended environment variables

- SECRET_KEY: a long unpredictable secret used by Django.
  Example: SECRET_KEY="_very_long_random_string_here_"

- DEBUG: must be `False` in production.
  Example: DEBUG=False

- ALLOWED_HOSTS: comma-separated hostnames for the app.
  Example: ALLOWED_HOSTS=api.example.com,example.com

- DATABASE_URL (optional): if using a remote DB; otherwise set DB_* vars.
  Example: DATABASE_URL=postgres://user:pass@db-host:5432/dbname

- REDIS_URL: required if using Redis for token blacklisting / caching.
  Example: REDIS_URL=redis://:password@redis-host:6379/0

HTTPS & cookie flags
- SECURE_SSL_REDIRECT=True
- SESSION_COOKIE_SECURE=True
- CSRF_COOKIE_SECURE=True
- SESSION_COOKIE_HTTPONLY=True
- CSRF_COOKIE_HTTPONLY=False
- SESSION_COOKIE_SAMESITE=Lax
- CSRF_COOKIE_SAMESITE=Lax

CORS & CSRF trusted origins
- CORS_ALLOWED_ORIGINS: comma-separated list of allowed frontend origins.
  Example: CORS_ALLOWED_ORIGINS=https://app.example.com
- CSRF_TRUSTED_ORIGINS: comma-separated list of origins allowed for CSRF checks.
  Example: CSRF_TRUSTED_ORIGINS=https://app.example.com

SIMPLE_JWT (djangorestframework-simplejwt) examples
- Use short `ACCESS_TOKEN_LIFETIME` (minutes) and longer `REFRESH_TOKEN_LIFETIME` (days).
- Enable rotation and blacklist in production.

Example env values (strings):
- JWT_ACCESS_MINUTES=5
- JWT_REFRESH_DAYS=7
- JWT_ROTATE_REFRESH=True
- JWT_BLACKLIST_AFTER_ROTATION=True

Notes: when `JWT_ROTATE_REFRESH=True` and `JWT_BLACKLIST_AFTER_ROTATION=True`,
you should enable a cache or Redis backend and run the `rest_framework_simplejwt.token_blacklist`
migrations (if installed) so old refresh tokens are tracked/blacklisted.

Throttling and rate limits
- Protect auth endpoints with throttles and/or API gateway rules.
- Example env vars used by settings:
  - RATE_LOGIN=5/min
  - RATE_REGISTER=3/min
  - RATE_REFRESH=30/min

Non-browser clients (CI, mobile, server-to-server)
- Use the `token/refresh/` (or `token/refresh-noncookie/`) endpoints that accept the
  refresh token in the request body or Authorization header. These endpoints are
  intended for non-browser clients only; avoid using body-based refresh from browser JS.

Production checklist before deploy
- Set `DEBUG=False` and `SECRET_KEY` securely.
- Configure `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` to exact hosts.
- Ensure `SECURE_SSL_REDIRECT=True` (or set at reverse proxy) and TLS certificates are valid.
- Install and configure Redis if you rely on token blacklisting or caching.
- Run migrations including any `simplejwt` blacklist migrations:
  ```bash
  python manage.py migrate
  ```
- Configure monitoring and alerts for auth failures and suspicious activity.

Optional hardening
- Consider DPoP or mTLS to bind tokens to clients if high security is required.
- Enforce Content Security Policy (CSP) and other XSS mitigations on the frontend.

If you'd like, I can convert these examples into a `docker-compose.prod.yml` snippet
or a sample `.env.example` tailored for your production domain.
