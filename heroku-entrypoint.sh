#!/usr/bin/env bash
set -e

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (if database is available)
python manage.py migrate --noinput || echo "Migrations failed, continuing..."

# Start the application
exec gunicorn nbtesite.wsgi:application --bind 0.0.0.0:$PORT