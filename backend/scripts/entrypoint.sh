#!/bin/sh
set -eu

if [ "${SKIP_MIGRATIONS:-0}" != "1" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

exec "$@"
