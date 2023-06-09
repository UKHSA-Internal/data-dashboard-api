#!/bin/bash

function migrate_tables() {
    python manage.py migrate --noinput
}


function set_api_key() {
    echo "Setting API key"
    local password_prefix=$1
    local password_suffix=$2
    python manage.py create_api_key --password_prefix=$password_prefix --password_suffix=$password_suffix
}


function create_admin_user() {
    echo "Creating admin user"
    local admin_password=$1
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('testadmin', '', '$admin_password')"
}


function create_core_time_series() {
    echo "Creating core time series"
    python manage.py upload_test_data
}


function generate_api_time_series() {
    echo "Generating API time series"
    python manage.py generate_api_time_series
}

function generate_cms_content() {
    echo "Generating CMS content"
    python manage.py build_cms_site
}


function _validate_args() {
    local password_prefix=$1
    local password_suffix=$2
    local admin_password=$3

    if [[ $# -ne 3 ]]; then
      echo "3 arguments are required. 1) password prefix 2) password suffix and 3) admin password" >&2
      echo 1
      return
    fi

}

function run_script() {
    echo "Running bootstrap script to populate application"
    local password_prefix=$1
    local password_suffix=$2
    local admin_password=$3

    local validated=$(_validate_args $password_prefix $password_prefix $admin_password)
    if [[ $validated -eq 1 ]]; then
      return 1
    fi

    migrate_tables
    set_api_key $password_prefix $password_suffix
    create_admin_user $admin_password
    create_core_time_series
    generate_api_time_series
    generate_cms_content
}

run_script $1 $2 $3