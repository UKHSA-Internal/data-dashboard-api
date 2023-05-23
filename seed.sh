#!/bin/bash

function migrate_tables() {
    echo "Migrating tables"
    python manage.py migrate --noinput
}

function create_admin_user() {
    echo "Creating admin user"

}

function create_api_key() {
    echo "Creating API key"
    api_key=$(python manage.py create_api_key)
    echo $api_key
}

function create_cms_content() {
    echo "Creating CMS content for base design"
    python manage.py build_cms_site
}

function upload_data() {
    echo "Uploading data"
    python manage.py upload_data
}


migrate_tables
create_admin_user
create_api_key
create_cms_content
upload_data