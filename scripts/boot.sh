#!/bin/bash
#set -x

function run_script() {
    echo "Running bootstrap script to populate application"
    echo "Argument received: $1"

    source uhd.sh
    uhd django migrate
    uhd bootstrap all "$1" 2>&1

    echo "Completed running bootstrap script"
}

run_script $1