# Enabling JWT refresh tokens (SimpleJWT)

This project supports both DRF TokenAuth and JWT (SimpleJWT). To enable access + refresh token flows, install `djangorestframework-simplejwt` and optionally the blacklist app for revocation.

Steps to enable and use:

1. Install the package:

```bash
cd kitchen_konnect
pip install -r requirements.txt
# or specifically
pip install djangorestframework-simplejwt
```

2. Ensure `requirements.txt` contains `djangorestframework-simplejwt` (already added).

3. Settings:

- `config/settings.py` contains a conditional `SIMPLE_JWT` configuration which sets `ACCESS_TOKEN_LIFETIME` and `REFRESH_TOKEN_LIFETIME` using env vars `JWT_ACCESS_MINUTES` and `JWT_REFRESH_DAYS`.
- If you want refresh token blacklisting (to revoke refresh tokens), install the blacklist extras and add the app:

```bash
pip install 'djangorestframework-simplejwt[blacklist]'
```

Then add `'rest_framework_simplejwt.token_blacklist'` to `INSTALLED_APPS` in `config/settings.py` and set `ROTATE_REFRESH_TOKENS = True` and `BLACKLIST_AFTER_ROTATION = True` in `SIMPLE_JWT`.

4. URL endpoints:

- Token obtain (JWT): `POST /api/auth/token/` — returns `access` and `refresh` tokens when `simplejwt` is available.
- Token refresh (JWT): `POST /api/auth/token/refresh/` — pass `{ "refresh": "<refresh_token>" }` to get a new access token.

Note: If `simplejwt` is not installed, the project falls back to DRF's `obtain_auth_token` endpoint for simple token auth.

5. Example client usage (fetch):

```js
// Obtain tokens
const res = await fetch('/api/auth/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
})
const data = await res.json()
// data: { access: '...', refresh: '...' }

// Use access token in Authorization header
fetch('/api/auth/me/', { headers: { Authorization: `Bearer ${data.access}` } })

// Refresh access
const r = await fetch('/api/auth/token/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: data.refresh })
})
const newTokens = await r.json()
```

6. Revoke refresh tokens (blacklist)

If using the blacklist app, you can revoke refresh tokens by calling `token.blacklist()` on a `RefreshToken` instance server-side, or deleting the token from the blacklist table.

7. Migrations

If you enable the blacklist app, run:

```bash
python manage.py migrate
```

That's it — the backend now supports refresh tokens when `djangorestframework-simplejwt` is installed and configured.
