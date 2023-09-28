#!/bin/bash

function hydrate_frontend_cache() {
    python manage.py hydrate_frontend_cache
}

function run_script() {
    echo "Running script to fill cache for the frontend"
    hydrate_frontend_cache
    echo "Completed filling cache for the frontend"
}

run_script