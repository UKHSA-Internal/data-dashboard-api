#!/bin/bash

function _quality_help() {
    echo
    echo "uhd quality <command>"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  all                       - run all checks"
    echo "  architecture              - check architectural constraints"
    echo "  ruff                      - run ruff checks across codebase"
    echo "  bandit                    - run bandit checks across codebase"
    echo
    echo "  format                    - run all formatters over codebase"
    echo "  format-check              - run all formatters over codebase, error if changes are required"


    return 0
}

function _quality() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "all") _quality_all $args ;;
        "architecture") _quality_architecture $args ;;
        "ruff") _quality_ruff $args ;;
        "bandit") _quality_bandit $args ;;
        "format") _quality_format $args ;;
        "format-check") _quality_format_check $args ;;

        *) _quality_help ;;
    esac
}

function _quality_all() {
    _quality_ruff
    _quality_bandit
}

function _quality_ruff() {
    uhd venv activate
    ruff check .
}

function _quality_bandit() {
    uhd venv activate
    bandit -c pyproject.toml -r .
}

function _quality_architecture() {
    uhd venv activate
    lint-imports
}

function _quality_format() {
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

function _quality_format_check() {
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
