#!/bin/bash

function run_script() {
    echo "Running bootstrap script to populate application"
    local admin_password=$1

    uhd django migrate
    uhd bootstrap admin-user $admin_password
    uhd bootstrap test-data
    uhd bootstrap test-content

    echo "Completed running bootstrap script"
}

run_script $1