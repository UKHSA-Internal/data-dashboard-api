#!/bin/bash

function set_up_django() {
    echo "Migrating tables"
    python manage.py migrate --noinput

    echo "Collecting static files"
    python manage.py collectstatic --noinput

    if [[ "$DETACHED_MODE" == "true" ]]; then
      # Running in detached mode means the server is not started
      return
    fi

    echo "Starting server"
    python manage.py runserver 0.0.0.0:80
}

set_up_django
