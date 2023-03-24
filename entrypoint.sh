#!/bin/bash

function set_up_django() {
    echo "Migrating tables"
    python manage.py migrate --noinput

    echo "Creating test superuser"
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('test', 'test.dashboard@ukhsa.com', 'adminpass')"

    echo "Starting server"
    python manage.py runserver 0.0.0.0:80
}

set_up_django
