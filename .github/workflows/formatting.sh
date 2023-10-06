#!/usr/bin/env bash
# Exit immediately on non-zero status
set -xe

# Run ruff and black (in that order) to check that there are no changes
ruff . --preview fix
black .

# Only verify for .py files
changed_files=$(git diff --name-only | grep "\.py" || true)

if [ -n "${changed_files}"  ]; then
    echo "Some files appear to be un-ruffed or unblacked. Please rectify by running ruff & then black over them."
    echo "${changed_files}"
    exit 1
else
    echo "No changes, the files are okay to be checked into the repo."
fi

