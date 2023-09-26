#!/bin/bash

function set_up_django() {
    echo "Migrating tables"
    python manage.py migrate --noinput

    echo "Collecting static files"
    python manage.py collectstatic --noinput

    echo "Starting server"
    gunicorn -w 3 metrics.api.wsgi:application 0.0.0.0:80
}

set_up_django
