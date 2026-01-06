from django.contrib.auth import get_user_model
import httpx
User = get_user_model()
username='kk_test_user'
password='TestPass123!'
if not User.objects.filter(username=username).exists():
    User.objects.create_user(username=username, password=password, email='test@example.com')
    print('created user')
else:
    print('user exists')

base='http://127.0.0.1:8000'
resp = httpx.post(base+'/api/auth/token/', json={'username':username,'password':password})
print('token endpoint status', resp.status_code, resp.text)
if resp.status_code == 200:
    token = resp.json().get('token') or resp.json().get('access') or resp.json().get('key')
    print('token:', token)
    headers = {'Authorization': f'Token {token}'}
    r2 = httpx.get(base+'/api/auth/me/', headers=headers)
    print('/api/auth/me/ status', r2.status_code, r2.text)
else:
    print('token request failed')
