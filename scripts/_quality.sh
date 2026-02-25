#!/bin/bash

function _quality_help() {
    echo
    echo "uhd quality <command>"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  all                       - run all checks with summary report"
    echo "  architecture              - check architectural constraints"
    echo "  ruff                      - run ruff checks across codebase"
    echo "  bandit                    - run bandit checks across codebase"
    echo
    echo "  format                    - run all formatters over codebase"
    echo "  format-check              - check formatting without modifying files"


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
    local ruff_status="FAIL"
    local bandit_status="FAIL"
    local architecture_status="FAIL"
    local format_check_status="FAIL"
    local ruff_exit_code=0
    local bandit_exit_code=0
    local architecture_exit_code=0
    local format_check_exit_code=0

    ( _quality_ruff )
    ruff_exit_code=$?
    if [ ${ruff_exit_code} -eq 0 ]; then
        ruff_status="SUCCESS"
    fi

    ( _quality_bandit )
    bandit_exit_code=$?
    if [ ${bandit_exit_code} -eq 0 ]; then
        bandit_status="SUCCESS"
    fi

    ( _quality_architecture )
    architecture_exit_code=$?
    if [ ${architecture_exit_code} -eq 0 ]; then
        architecture_status="SUCCESS"
    fi

    ( _quality_format_check )
    format_check_exit_code=$?
    if [ ${format_check_exit_code} -eq 0 ]; then
        format_check_status="SUCCESS"
    fi

    echo
    echo "+----------------------+----------+"
    echo "| CHECK                | STATUS   |"
    echo "+----------------------+----------+"
    printf "| %-20s | %-8s |\n" "ruff" "${ruff_status}"
    printf "| %-20s | %-8s |\n" "bandit" "${bandit_status}"
    printf "| %-20s | %-8s |\n" "architecture" "${architecture_status}"
    printf "| %-20s | %-8s |\n" "format-check" "${format_check_status}"
    echo "+----------------------+----------+"

    if [ ${ruff_exit_code} -ne 0 ] || [ ${bandit_exit_code} -ne 0 ] || [ ${architecture_exit_code} -ne 0 ] || [ ${format_check_exit_code} -ne 0 ]; then
        return 1
    fi

    return 0
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
    uhd venv activate

    echo "Running ruff formatting checks"
    ruff check .

    echo "Running black formatting checks"
    black --check .

    echo "No formatting changes required."

}
