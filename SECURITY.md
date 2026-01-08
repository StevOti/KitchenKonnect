Production authentication & security checklist

This file lists minimal changes and recommendations to make authentication safe for production.

1) Environment & secrets
- Set `SECRET_KEY` in environment; never check it into source.
- Set `DEBUG=False` in production.
- Set `ALLOWED_HOSTS` to your domain(s).
- Configure `DATABASE_URL` and use a managed DB (Postgres, etc.).

2) TLS / transport
- Serve the site only over HTTPS (obtain certificate via Let's Encrypt or managed provider).
- Enable `SECURE_SSL_REDIRECT=True` and set `SECURE_PROXY_SSL_HEADER` if behind a proxy.
- Set HSTS: `SECURE_HSTS_SECONDS` (>= 31536000) and enable `SECURE_HSTS_INCLUDE_SUBDOMAINS` and `SECURE_HSTS_PRELOAD`.

3) Cookies and CSRF
- Use secure, HttpOnly cookies for session/auth tokens when possible (`SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`).
- For cookie-based auth across different origins, add `CSRF_TRUSTED_ORIGINS` and set `CORS_ALLOWED_ORIGINS` appropriately.
- Prefer SameSite=Lax for auth cookies to reduce CSRF risk while allowing top-level navigations.

4) Token storage (frontend)
- Avoid storing long-lived tokens in `localStorage` or readable JS storage in production (XSS risk).
- Prefer storing refresh tokens in HttpOnly, Secure cookies and keeping access token short-lived in memory.
- Alternatively, implement cookie-based session authentication (Django sessions) with CSRF protection.

5) Authentication endpoints
- Use `djangorestframework-simplejwt` or robust token system; enable refresh token rotation and blacklisting if supported.
- Rate-limit authentication endpoints and consider account lockouts after repeated failures (e.g. `django-axes`).

6) CORS & origins
- Do not enable `CORS_ALLOW_ALL_ORIGINS=True` in production.
- Set `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS` to your frontend origin(s) (e.g. https://app.example.com).

7) Passwords & accounts
- Enforce strong password validators (already enabled).
- Consider email verification and password reset flows before allowing privileged actions.

8) Monitoring & rotation
- Log auth failures and monitor for suspicious activity.
- Rotate secrets periodically and use a secrets manager for production credentials.

9) Deployment minimums
- Run `manage.py migrate` on deployment and ensure the DB user has least privilege.
- Run the app behind a production WSGI server (Gunicorn/uvicorn) and a reverse proxy (nginx) configured for TLS.

10) Optional hardening
- Add Content Security Policy (CSP) to mitigate XSS.
- Use security scanners and automated tests for auth flows.

If you'd like, I can:
- Implement cookie-based token exchange endpoints (backend) and update the frontend login/register to use HttpOnly cookies instead of `localStorage`.
- Add `django-axes` or DRF throttling rules to limit auth attempts.

