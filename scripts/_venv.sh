#!/bin/bash

VENV_LOCATION=.venv

function _venv_help() {
    echo
    echo "uhd venv <command>"
    echo
    echo "commands:"
    echo "  help                      - this help screen"
    echo
    echo "  activate                  - activate the virtual environment"
    echo "  create                    - create a new virtual environment"
    echo "  deactivate                - deactivate the current virtual environment"


    return 0
}

function _venv() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "activate") _activate $args ;;
        "create") _create $args ;;
        "deactivate") _deactivate $args ;;

        *) _venv_help ;;
    esac
}

function _activate() {
    source .venv/bin/activate || echo "Did you forget to create a venv? Please run 'uhd venv create' first"
}

function _deactivate() {
  deactivate
}

function _create() {
    local python_version=`cat .python-version`
    python${python_version} -m venv --upgrade-deps .venv
    _activate
    pip install -r requirements.txt
}



