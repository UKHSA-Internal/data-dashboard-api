#!/usr/bin/env sh

set -e

echo "Starting server..."

aerich init -t settings.TORTOISE_ORM
# aerich init-db
# aerich migrate
aerich upgrade

uvicorn main:app
