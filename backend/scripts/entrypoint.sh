#!/bin/sh
set -eu

echo "Running database migrations..."
alembic upgrade head

exec "$@"
