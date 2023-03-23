
function set_up_django() {
    echo "Migrating tables"
    python manage.py migrate --noinput

    echo "Starting server"
    python manage.py runserver 0.0.0.0:80
}

set_up_django
