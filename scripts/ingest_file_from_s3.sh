#!/bin/bash

function ingest_file_from_s3() {
    local file_key=$1
    python manage.py ingest_file_from_s3 --file-key=$file_key
}


function run_script() {
    echo "Uploading file from s3"
    local file_key=$1

    ingest_file_from_s3 $file_key
    echo "Completed uploading file from s3"
}

run_script $1