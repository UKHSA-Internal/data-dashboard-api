#!/usr/bin/env sh

set -e

echo "Starting server..."

# aerich init -t settings.TORTOISE_ORM

# echo "AERICH initialization finished, runnig aerich upgrade now"
# aerich upgrade

# echo "AERICH upgrade is done, starting the app..."
uvicorn wpapi.main:app --host 0.0.0.0 --port 80
