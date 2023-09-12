#!/bin/bash

function hydrate_private_api_cache() {
    python manage.py hydrate_private_api_cache
}

function run_script() {
    echo "Running script to fill cache for private API"
    hydrate_private_api_cache
    echo "Completed filling cache for private API"
}

run_script