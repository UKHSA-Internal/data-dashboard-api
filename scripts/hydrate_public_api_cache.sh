#!/bin/bash

function hydrate_public_api_cache() {
    python manage.py hydrate_public_api_cache
}

function collect_static_files() {
    # This script is intended to be ran within a job
    # Which means the entrypoint of the container is overridden with a call to this script
    # As such, the static files need to be collected within the job process
    # Before the `hydrate_public_api_cache` can be called
    python manage.py collectstatic --noinput
}

function run_script() {
    echo "Running script to fill cache for public API"

    echo "Collecting static files"
    collect_static_files
    echo "Finished collecting static files"

    echo "Running command to fill cache for public API"
    hydrate_public_api_cache
    echo "Completed filling cache for public API"
}

run_script