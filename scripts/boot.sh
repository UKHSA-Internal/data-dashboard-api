#!/bin/bash

function run_script() {
    echo "Running bootstrap script to populate application"
    local admin_password=$1

    source uhd.sh
    uhd bootstrap all $admin_password

    echo "Completed running bootstrap script"
}

run_script $1