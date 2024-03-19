#!/bin/bash

function _quality_help() {
    echo
    echo "uhd quality <command>"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  architecture              - check architectural constraints"
    echo "  format                    - run all formatters over codebase"

    return 0
}

function _quality() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "architecture") _architecture $args ;;
        "format") _format $args ;;

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
