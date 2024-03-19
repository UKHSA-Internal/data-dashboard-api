#!/bin/bash

root=$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)

for script_file in "$root"/scripts/_*.sh; do
    source $script_file
done

function _uhd_commands_help() {

    echo 
    echo "                    █░█ █▄▀ █░█ █▀ ▄▀█ "
    echo "                    █▄█ █░█ █▀█ ▄█ █▀█ "
    echo 
    echo "    █▀▄ ▄▀█ ▀█▀ ▄▀█   █▀▄ ▄▀█ █▀ █░█ █▄▄ █▀█ ▄▀█ █▀█ █▀▄ "
    echo "    █▄▀ █▀█ ░█░ █▀█   █▄▀ █▀█ ▄█ █▀█ █▄█ █▄█ █▀█ █▀▄ █▄▀ "
    echo 
    echo "                        █▀▀ █░░ █"
    echo "                        █▄▄ █▄▄ █"
    echo
    echo "               UKHSA Data Dashboard Backend CLI Tool"
    echo
    echo "uhd <command> [options]"
    echo
    echo "commands:"
    echo "  help         - this help screen"
    echo
    echo "  django       - django application commands"
    echo "  bootstrap    - bootstrap environment commands"
    echo "  cache         - cache flush tooling commands"
    echo "  security     - security tooling commands"
    echo "  server       - running server commands"
    echo "  tests        - test suite execution commands"
    echo "  quality      - code quality tooling commands"
    echo "  venv         - virtual environment commands"

    return 0
}

function uhd() {
    if [ $CI ]; then
        echo $0 $@
    fi

    local current=$(pwd)
    local command=$1
    local args=(${@:2}) 

    cd $root

    case $command in
        "bootstrap") _bootstrap $args ;;
        "django") _django $args ;;
        "cache") _cache $args ;;
        "security") _security $args ;;
        "server") _server $args ;;
        "tests") _tests $args ;;
        "quality") _quality $args ;;
        "venv") _venv $args ;;

        *) _uhd_commands_help ;;
    esac

    local exit_code=$?

    cd $current

    return $exit_code
}

echo
echo "uhd cli loaded"
echo
echo "Type uhd for the help screen"
echo

return 0