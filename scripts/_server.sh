#!/bin/bash

function _server_help() {
    echo
    echo "uhd server <command> [options]"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  run-local                 - start a local development grade server"
    echo "  run-production            - start a production grade server"
    echo
    echo "  setup-all                 - run all setup steps, migrations & static files"
    echo "  setup-migrations          - apply any outstanding database migrations"
    echo "  setup-static-files        - collect static files"

    return 0
}

function _server() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "run-local") _run_local_server  $args ;;
        "run-production") _run_production_server  $args ;;
        "setup-all") _setup_all  $args ;;
        "setup-migrations") _setup_migrations  $args ;;
        "setup-static-files") _setup_static_files  $args ;;

        *) _server_help ;;
    esac
}

function _run_local_server() {
    local port=$1

    if [[ -z ${port} ]]; then
        echo "Port is required" >&2
        return 1
    fi

    uhd venv activate
    python manage.py runserver localhost:${port}
}

function _run_production_server() {
    local port=$1

    if [[ -z ${port} ]]; then
        echo "Port is required" >&2
        return 1
    fi

    uhd venv activate
    gunicorn metrics.api.wsgi:application \
      --workers=3 \
      --threads=3 \
      --worker-class=gthread \
      --timeout=120 \
      --bind=0.0.0.0:${port}
}

function _setup_all() {
    _setup_migrations
    _setup_static_files
}

function _setup_migrations() {
    uhd venv activate

    echo "Collecting static files"
    python manage.py migrate --noinput
}

function _setup_static_files() {
    uhd venv activate

    echo "Collecting static files"
    python manage.py collectstatic --noinput
}