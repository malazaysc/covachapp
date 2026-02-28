#!/usr/bin/env sh
set -e

python - <<'PY'
import os
import socket
import time
from urllib.parse import urlparse

database_url = os.environ.get("DATABASE_URL", "postgres://covach:covach@db:5432/covach")
parsed = urlparse(database_url)
host = parsed.hostname or "db"
port = parsed.port or 5432

for attempt in range(1, 61):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((host, port))
    except OSError:
        if attempt == 60:
            raise SystemExit(f"Database not reachable at {host}:{port} after 60 attempts")
        time.sleep(1)
    else:
        sock.close()
        break
PY

python manage.py migrate
if [ "${AUTO_SEED_DEMO:-1}" = "1" ]; then
  python manage.py seed_demo_data --if-empty
fi
python manage.py collectstatic --noinput
if [ "$#" -gt 0 ]; then
  exec "$@"
fi
exec python manage.py runserver 0.0.0.0:8000
