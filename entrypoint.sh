#!/usr/bin/env bash
set -e

echo "Waiting for DB at ${DB_HOST}:${DB_PORT}..."
until python - <<'PYCODE'
import os, socket, sys
host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))
s = socket.socket()
try:
    s.settimeout(2)
    s.connect((host, port))
    sys.exit(0)
except Exception:
    sys.exit(1)
finally:
    s.close()
PYCODE
do
  echo "DB not ready yet..."
  sleep 2
done
echo "DB is up."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn nbtesite.wsgi:application --bind 0.0.0.0:8000
