#!/bin/sh
set -e

cd /app

if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

exec "$@"
