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
        "unit") _unit $args ;;
        "integration") _integration $args ;;
        "system") _system $args ;;
        "migrations") _migrations $args ;;
        "coverage") _coverage $args ;;
        "all") _all $args ;;

        *) _tests_help ;;
    esac
}

function _unit() {
    uhd venv activate
    pytest tests/unit
}

function _integration() {
    uhd venv activate
    python -m pytest tests/integration
}

function _system() {
    uhd venv activate
    pytest tests/system
}

function _migrations() {
    uhd venv activate
    pytest tests/migrations
}

function _coverage() {
    uhd venv activate
    pytest --cov
}

function _all() {
    _unit
    _integration
    _system
    _migrations
}
