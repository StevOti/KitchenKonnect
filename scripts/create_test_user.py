from pathlib import Path
import os
import sys
from datetime import datetime

# Ensure project root is on sys.path so Django settings can be imported
# Locate the Django project directory by walking up until we find manage.py
HERE = Path(__file__).resolve()
PROJECT_DIR = None
for p in [HERE] + list(HERE.parents):
    if (p / 'manage.py').exists():
        PROJECT_DIR = p
        break
if PROJECT_DIR is None:
    # fallback to parent/kitchen_konnect
    alt = Path(__file__).resolve().parents[1] / 'kitchen_konnect'
    if alt.exists():
        PROJECT_DIR = alt
    else:
        PROJECT_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.contrib.auth import get_user_model


def main():
    User = get_user_model()
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    username = f'kk_test_{ts}'
    email = f'{username}@example.com'
    password = 'TestPass123!'

    if User.objects.filter(email=email).exists():
        print('User with email already exists, using existing user: ', email)
        user = User.objects.filter(email=email).first()
    else:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True
        user.save()
        print('Created test user')

    print('Credentials:')
    print('  username:', user.username)
    print('  email:   ', user.email)
    print('  password:', password)


if __name__ == '__main__':
    main()
