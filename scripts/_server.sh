#!/bin/bash

function _server_help() {
    echo
    echo "uhd server <command> [options]"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  run-local <port>          - start a local development grade server, port defaults to to 8000"
    echo "  run-production <port>     - start a production grade server, port defaults 80"
    echo
    echo "  setup-all                 - run all setup steps, migrations & static files"
    echo "  setup-static-files        - collect static files"

    return 0
}

function _server() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "run-local") _server_run_local  $args ;;
        "run-production") _server_run_production  $args ;;
        "setup-all") _server_setup_all  $args ;;
        "setup-static-files") _server_setup_static_files  $args ;;

        *) _server_help ;;
    esac
}

function _server_run_local() {
    local port=$1

    uhd venv activate
    python manage.py runserver localhost:${port:-8000}
}

function _server_run_production() {
    local port=$1

    uhd venv activate
    gunicorn metrics.api.wsgi:application \
      --workers=3 \
      --threads=3 \
      --worker-class=gthread \
      --timeout=120 \
      --bind=0.0.0.0:${port:-80}
}

function _server_setup_all() {
    uhd django migrate
    _setup_static_files
}

function _server_setup_static_files() {
    uhd venv activate

    echo "Collecting static files"
    python manage.py collectstatic --noinput
}