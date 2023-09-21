#!/bin/bash

function upload_files_from_s3() {
    python manage.py upload_files_from_s3
}


function run_script() {
    echo "Running script to upload data from s3 bucket"
    upload_files_from_s3
    echo "Completed running script to upload data"
}

run_script