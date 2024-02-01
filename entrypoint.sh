#!/bin/bash

function set_up_django() {
    echo "Migrating tables"
    python manage.py migrate --noinput

    echo "Collecting static files"
    python manage.py collectstatic --noinput

    echo "Starting server"
    gunicorn metrics.api.wsgi:application \
      --workers=3 \
      --threads=3 \
      --worker-class=gthread \
      --timeout=120 \
      --bind=0.0.0.0:80
}

set_up_django
