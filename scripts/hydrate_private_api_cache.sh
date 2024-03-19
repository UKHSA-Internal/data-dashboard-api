#!/bin/bash

function run_script() {
    echo "Running script to fill cache for private API"

    # This script is intended to be ran within a job
    # Which means the entrypoint of the container is overridden with a call to this script
    # As such, the static files need to be collected within the job process
    # Before the `hydrate_private_api_cache` can be called
    uhd server setup-static-files
    uhd cache flush-redis
    echo "Completed filling cache for private API"
}

run_script