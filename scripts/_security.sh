#!/bin/bash

function _security_help() {
    echo
    echo "uhd security <command>"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  dependencies              - run checks over project dependencies"
    echo "  vulnerabilities           - run vulnerabilities static analysis over codebase"

    return 0
}

function _security() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "dependencies") _dependencies $args ;;
        "vulnerabilities") _vulnerabilities $args ;;

        *) _security_help ;;
    esac
}

function _dependencies() {
    uhd venv activate
    pip-audit -r requirements.txt
}

function _vulnerabilities() {
    uhd venv activate
    bandit -c pyproject.toml -r .
}
