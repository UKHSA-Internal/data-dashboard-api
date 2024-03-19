#!/bin/bash

function _bootstrap_help() {
    echo
    echo "uhd bootstrap <command> [options]"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  admin-user                - add an admin superuser"
    echo
    echo "  test-content              - populate the cms with base pages"
    echo "  test-data                 - upload the truncated test dataset"

    return 0
}

function _bootstrap() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "admin-user") _admin_user $args ;;
        "test-content") _test_content $args ;;
        "test-data") _test_data $args ;;

        *) _bootstrap_help ;;
    esac
}

function _admin_user() {
    local admin_password=$1
    if [[ -z ${admin_password} ]]; then
        echo "Password for admin user is required" >&2
        return 1
    fi

    echo "Creating admin user"
    uhd venv activate
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('testadmin', '', '$admin_password')"
}

function _test_content() {
    echo "Creating CMS content"
    uhd venv activate
    python manage.py build_cms_site
}

function _test_data() {
    echo "Uploading truncated test data"
    uhd venv activate
    python manage.py upload_truncated_test_data
}
