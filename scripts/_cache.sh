#!/bin/bash

function _cache_help() {
    echo
    echo "uhd cache <command>"
    echo
    echo "commands:"
    echo "  help                            - this help screen"
    echo
    echo "  flush-redis                     - flush and re-fill the redis (private api) cache"
    echo "  flush-redis-reserved-namespace  - blue-green update the reserved namespace in the redis (private api) cache"

    return 0
}

function _cache() {
    local verb=$1
    local args=(${@:2})

    case $verb in
        "flush-redis") _cache_flush_redis $args ;;
        "flush-redis-reserved-namespace") _cache_flush_redis_reserved_namespace $args ;;

        *) _cache_help ;;
    esac
}

function _cache_flush_redis() {
    uhd venv activate
    python manage.py hydrate_private_api_cache
}

function _cache_flush_redis_reserved_namespace() {
    uhd venv activate
    python manage.py hydrate_private_api_cache_reserved_namespace
}
