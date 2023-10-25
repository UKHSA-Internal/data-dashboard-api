#!/bin/bash

function set_up_django() {
    echo "Migrating tables"
    python manage.py migrate --noinput

    echo "Collecting static files"
    python manage.py collectstatic --noinput

    echo "Starting server"
    gunicorn --workers=3 --bind=0.0.0.0:80 metrics.api.wsgi:application --timeout=120
}

set_up_django
