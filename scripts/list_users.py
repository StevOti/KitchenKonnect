from pathlib import Path
import sqlite3
import sys

def find_db():
    candidates = [Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]]
    for p in candidates:
        candidate = p / 'db.sqlite3'
        if candidate.exists():
            return candidate
    return None


def main():
    db = find_db()
    if not db:
        print('ERROR: db.sqlite3 not found. Tried:', [str(p / 'db.sqlite3') for p in [Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]]])
        sys.exit(1)

    conn = sqlite3.connect(str(db))
    cur = conn.cursor()

    # Find tables related to users
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'users%';")
    tables = [r[0] for r in cur.fetchall()]
    print('Found tables:', tables)

    possible_tables = ['users_customuser', 'auth_user', 'users_user']
    for t in possible_tables:
        if t in tables:
            print('\nContents of table', t)
            try:
                cur.execute(f"PRAGMA table_info('{t}')")
                cols = [r[1] for r in cur.fetchall()]
                print('Columns:', cols)
                cur.execute(f"SELECT id, username, email, is_active, is_staff, is_superuser FROM {t};")
                rows = cur.fetchall()
                if rows:
                    for r in rows:
                        print(r)
                else:
                    print('No rows found in', t)
            except Exception as e:
                print('Error reading', t, e)

    conn.close()


if __name__ == '__main__':
    main()
