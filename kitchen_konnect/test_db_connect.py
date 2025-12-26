import os
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
    from django.db import connections
    c = connections['default']
    print('Attempting connection...')
    try:
        c.ensure_connection()
        print('Connected, usable:', c.is_usable())
    except Exception:
        print('Connection attempt failed:')
        traceback.print_exc()
except Exception:
    print('Django setup failed:')
    traceback.print_exc()
