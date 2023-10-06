#!/usr/bin/env bash
# Exit immediately on non-zero status
set -xe

# Run black to check that there are no changes
black .

# Only verify for .py files
changed_files=$(git diff --name-only | grep "\.py" || true)

if [ -n "${changed_files}"  ]; then
    echo "Some files appear to be unblacked. Please rectify by running black over them."
    echo "${changed_files}"
    exit 1
else
    echo "No changes, the files are okay to be checked into the repo."
fi

