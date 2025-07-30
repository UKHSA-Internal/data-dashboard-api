#!/bin/bash

function run_script() {
    echo "Running script to fill reserved namespace in private API cache"

    source uhd.sh
    # This script is intended to be ran within a job
    # Which means the entrypoint of the container is overridden with a call to this script
    # As such, the static files need to be collected within the job process
    # Before the main action can be executed
    uhd server setup-static-files
    uhd cache flush-redis-reserved-namespace
    echo "Completed filling reserved namespace in private API cache"
}

run_script