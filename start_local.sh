#!/usr/bin/env sh

set -e

echo "waiting 3 seconds for the DB to initialize"
sleep 3

echo "Starting local server..."

aerich init -t wpapi.settings.TORTOISE_ORM_LOCAL
aerich init-db
aerich migrate
aerich upgrade

uvicorn wpapi.main:app --reload
