#!/usr/bin/env sh

set -e

echo "Starting local server..."

aerich init -t wpapi.settings.TORTOISE_ORM
aerich init-db
aerich migrate
aerich upgrade

uvicorn wpapi.main:app --reload
