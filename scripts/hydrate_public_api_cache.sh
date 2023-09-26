#!/bin/bash

function hydrate_public_api_cache() {
    python manage.py hydrate_public_api_cache
}

function run_script() {
    echo "Running script to fill cache for public API"

    echo "Running command to fill cache for public API"
    hydrate_public_api_cache
    echo "Completed filling cache for public API"
}

run_script