#!/bin/bash

function _tests_help() {
    echo
    echo "uhd tests <command>"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  unit                      - run all unit tests"
    echo "  integration               - run all integration tests"
    echo "  system                    - run all system tests"
    echo "  migrations                - run all migration tests"
    echo
    echo "  coverage                  - run test coverage"
    echo "  all                       - run all tests regardless of type"

    return 0
}

function _tests() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "unit") _tests_unit $args ;;
        "integration") _tests_integration $args ;;
        "system") _tests_system $args ;;
        "migrations") _tests_migrations $args ;;
        "coverage") _tests_coverage $args ;;
        "all") _tests_all $args ;;

        *) _tests_help ;;
    esac
}

function _tests_unit() {
    uhd venv activate
    pytest tests/unit "$@"
}

function _tests_integration() {
    uhd venv activate
    python -m pytest tests/integration "$@"
}

function _tests_system() {
    uhd venv activate
    pytest tests/system "$@"
}

function _tests_migrations() {
    uhd venv activate
    pytest tests/migrations "$@"
}

function _tests_coverage() {
    uhd venv activate
    pytest --cov
}

function _tests_all() {
    uhd tests unit
    uhd tests integration
    uhd tests system
    uhd tests migrations
}
