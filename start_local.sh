#!/usr/bin/env sh

set -e

# echo "waiting 3 seconds for the DB to initialize"
# sleep 3

echo "Starting local server..."

# Some env vars need to be set in this file
. /opt/.env

# aws_access_key_id=ASIAYLNTCV4VYUXMON6K
# aws_secret_access_key=0wv30Jo8nyYI3vBvRw9jKfvImtOTrBz19heC5pn5

aerich init -t settings.TORTOISE_ORM
aerich upgrade

uvicorn main:app --host 0.0.0.0 --port 5100 --reload
