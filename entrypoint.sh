#!/bin/bash

function set_up_django() {
    echo "Migrating tables"
    python manage.py migrate --noinput

    echo "Collecting static files"
    python manage.py collectstatic

    echo "Starting server"
    python manage.py runserver 0.0.0.0:80
}

set_up_django
