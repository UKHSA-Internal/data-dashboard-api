#!/bin/bash

function _django_help() {
    echo
    echo "uhd django <command>"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  makemigrations            - create any outstanding database migrations"
    echo "  migrate                   - apply any outstanding database migrations"
    echo
    echo "  shell                     - create an interactive shell into the django app"

    return 0
}

function _django() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "makemigrations") _django_make_migrations $args ;;
        "migrate") _django_migrate $args ;;
        "shell") _django_shell $args ;;

        *) _django_help ;;
    esac
}

function _django_make_migrations() {
    uhd venv activate
    python manage.py makemigrations
}

function _django_migrate() {
    uhd venv activate
    python manage.py migrate
}

function _django_shell() {
    uhd venv activate
    python manage.py shell
}