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
    local no_venv_found_message="
    There is no venv available.
    If this is for local development,
    then please run 'uhd venv create' first.
    If not, the system interpreter will be used.
    "
    source .venv/bin/activate || echo ${no_venv_found_message}
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



