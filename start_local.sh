#!/usr/bin/env sh

set -e

echo "Starting local server..."

aerich init -t settings.TORTOISE_ORM
aerich upgrade

uvicorn main:app --host 0.0.0.0 --port 5100 --reload
