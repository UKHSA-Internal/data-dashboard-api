#!/bin/bash

function _quality_help() {
    echo
    echo "uhd quality <command>"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  architecture              - check architectural constraints"
    echo
    echo "  format                    - run all formatters over codebase"
    echo "  format-check              - run all formatters over codebase, error if changes are required"


    return 0
}

function _quality() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "architecture") _architecture $args ;;
        "format") _format $args ;;
        "format-check") _format_check $args ;;

        *) _quality_help ;;
    esac
}

function _architecture() {
    uhd venv activate
    lint-imports
}

function _format() {
    uhd venv activate
    _ruff_formatter
    _black_formatter
}

function _ruff_formatter() {
  echo "Running ruff formatter"
  ruff check . --preview --fix
}

function _black_formatter() {
  echo "Running black formatter"
  black .
}

function _format_check() {
    uhd quality format
    changed_files=$(git diff --name-only | grep "\.py" || true)

    if [ -n "${changed_files}"  ]; then
      echo "Some files appear to be un-formatted. Please rectify by running 'uhd quality format' and committing the changes."
      echo "${changed_files}"
      exit 1
    else
        echo "No changes, the files are okay to be checked into the repo."
    fi

}
