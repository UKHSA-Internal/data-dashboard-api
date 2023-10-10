#!/bin/bash

function migrate_tables() {
    python manage.py migrate --noinput
}

function create_admin_user() {
    echo "Creating admin user"
    local admin_password=$1
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('testadmin', '', '$admin_password')"
}

function upload_truncated_test_data() {
    echo "Uploading truncated test data"
    python manage.py upload_truncated_test_data
}

function generate_cms_content() {
    echo "Creating CMS content"
    python manage.py build_cms_site
}

function _validate_args() {
    local admin_password=$1

    if [[ $# -ne 1 ]]; then
      echo "1 argument is required for the CMS admin password" >&2
      echo 1
      return
    fi

}

function run_script() {
    echo "Running bootstrap script to populate application"
    local admin_password=$1

    local validated=$(_validate_args $admin_password)
    if [[ $validated -eq 1 ]]; then
      return 1
    fi

    migrate_tables
    create_admin_user $admin_password
    upload_truncated_test_data
    generate_cms_content
    echo "Completed running bootstrap script"
}

run_script $1