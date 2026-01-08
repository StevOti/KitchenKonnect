"""
Simple integration test script for the auth cookie flow.
Requires Python `requests` package: `pip install requests`

Usage: python scripts/auth_integration_test.py

It will attempt to login (or register if not present), verify Set-Cookie is returned,
then call refresh and logout. Adjust credentials as needed.
"""
import requests
from datetime import datetime

BASE = 'http://127.0.0.1:8000'
PASSWORD = 'TestPass123!'
FRONTEND_ORIGIN = 'http://127.0.0.1:5173'


def make_cookie_header(session: requests.Session):
    return '; '.join([f"{k}={v}" for k, v in session.cookies.items()])

def get_csrf_token(session: requests.Session):
    # Call the explicit CSRF endpoint to get token and cookie
    r = session.get(BASE + '/api/auth/csrf/')
    try:
        data = r.json()
        return data.get('csrf') or session.cookies.get('csrftoken') or session.cookies.get('csrf')
    except Exception:
        return session.cookies.get('csrftoken') or session.cookies.get('csrf')


def unique_credentials():
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    username = f'kk_integ_{ts}'
    email = f'{username}@example.com'
    return username, email


s = requests.Session()

USERNAME, EMAIL = unique_credentials()

print('Fetching CSRF token...')
csrf = get_csrf_token(s)
cookie_csrf = s.cookies.get('csrftoken') or s.cookies.get('csrf')
print('CSRF token (session):', bool(csrf))
# Prefer the cookie value (double-submit) since Django validates header==cookie
headers = {'X-CSRFToken': cookie_csrf or csrf} if (cookie_csrf or csrf) else {}
if s.cookies:
    headers['Cookie'] = make_cookie_header(s)
print('\nSession cookies before register/login:')
for name, val in s.cookies.items():
    print(' ', name, '=', val)

print('\nHeaders to be sent on POSTs:')
for k, v in headers.items():
    print(' ', k, ':', v)

print('Registering a fresh test user...')
r2 = s.post(f'{BASE}/api/auth/register/', json={'username': USERNAME, 'email': EMAIL, 'password': PASSWORD}, headers=headers)
print('Register status:', r2.status_code)
print('Register body:', r2.text[:400])

# Refresh CSRF token/cookie after registration (server may have reset it)
csrf_after = get_csrf_token(s)
cookie_csrf_after = s.cookies.get('csrftoken') or s.cookies.get('csrf')
headers = {'X-CSRFToken': cookie_csrf_after or csrf_after} if (cookie_csrf_after or csrf_after) else {}
if s.cookies:
    headers['Cookie'] = make_cookie_header(s)
print('\nAfter register - session cookies:')
for name, val in s.cookies.items():
    print(' ', name, '=', val)
print('\nHeaders to be sent on POSTs (after refresh):')
for k, v in headers.items():
    print(' ', k, ':', v)

print('\nUsing access token returned by registration to call protected endpoint...')
access = None
try:
    access = r2.json().get('access')
except Exception:
    pass
if access:
    auth_headers = {'Authorization': f'Bearer {access}'}
    r_prot = s.get(f'{BASE}/api/auth/me/', headers=auth_headers)
    print('Protected /me/ status:', r_prot.status_code, 'body:', r_prot.text[:200])

print('\nCalling refresh endpoint (uses cookie)')
# Include Origin/Referer matching the frontend dev origin to satisfy origin checks
# CSRF_TRUSTED_ORIGINS includes http://localhost:5173 in DEBUG, so use that origin.
headers_with_origin = headers.copy()
if s.cookies:
    headers_with_origin['Cookie'] = make_cookie_header(s)
headers_with_origin.update({'Origin': FRONTEND_ORIGIN, 'Referer': FRONTEND_ORIGIN})
r3 = s.post(f'{BASE}/api/auth/cookie/refresh/', headers=headers_with_origin)
print('Refresh status:', r3.status_code)
print('Refresh body:')
print(r3.text)
print('Refresh response headers:', dict(r3.headers))
try:
    print('Refresh request headers sent:', dict(r3.request.headers))
except Exception:
    pass
print('Session cookies at refresh:', {k: v for k, v in s.cookies.items()})
# --- Non-cookie refresh test: post the refresh token in the request body ---
print('\nTesting non-cookie refresh endpoint (/api/auth/token/refresh/)')
refresh_token = s.cookies.get('refresh')
if refresh_token:
    r_nc = s.post(f'{BASE}/api/auth/token/refresh/', json={'refresh': refresh_token})
    print('Non-cookie refresh status:', r_nc.status_code)
    try:
        print('Non-cookie refresh body:', r_nc.json())
    except Exception:
        print('Non-cookie refresh body (text):', r_nc.text[:500])
else:
    print('No refresh token available for non-cookie refresh test')

# Also exercise the dedicated non-cookie endpoint (requires Authorization header)
if access and refresh_token:
    print('\nTesting non-cookie refresh-noncookie endpoint (requires Authorization header)')
    headers_nc = {'Authorization': f'Bearer {access}'}
    r_nc2 = s.post(f'{BASE}/api/auth/token/refresh-noncookie/', json={'refresh': refresh_token}, headers=headers_nc)
    print('Non-cookie-noncookie status:', r_nc2.status_code)
    try:
        print('Non-cookie-noncookie body:', r_nc2.json())
    except Exception:
        print('Non-cookie-noncookie body (text):', r_nc2.text[:500])

print('\nCalling logout endpoint')
# Include Authorization if available so logout can blacklist; otherwise rely on cookie
logout_headers = headers_with_origin.copy()
if access:
    logout_headers.update({'Authorization': f'Bearer {access}'})
r4 = s.post(f'{BASE}/api/auth/cookie/logout/', headers=logout_headers)
print('Logout status:', r4.status_code)

print('\nDone')
