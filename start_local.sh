#!/usr/bin/env sh

set -e

echo "waiting 3 seconds for the DB to initialize"
sleep 3

echo "Starting local server..."

aerich init -t settings.TORTOISE_ORM_LOCAL
aerich init-db
aerich migrate
aerich upgrade

uvicorn main:app --host 0.0.0.0 --port 5100 --reload
