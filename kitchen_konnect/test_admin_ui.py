import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

urls = [
    'http://127.0.0.1:8000/admin/',
    'http://127.0.0.1:8000/admin/users/customuser/'
]

for u in urls:
    print('\nRequesting', u)
    req = Request(u, headers={'User-Agent': 'curl/7.64'})
    try:
        with urlopen(req, timeout=10) as r:
            status = r.getcode()
            data = r.read(5000)
            print('Status:', status)
            print('Body snippet:\n')
            print(data.decode('utf-8', errors='replace')[:2000])
    except HTTPError as e:
        print('HTTPError:', e.code)
        try:
            print(e.read().decode('utf-8', errors='replace')[:2000])
        except Exception:
            pass
    except URLError as e:
        print('URLError:', e)
    except Exception as e:
        print('Error:', type(e).__name__, e)

print('\nDone')
