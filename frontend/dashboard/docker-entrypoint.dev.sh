#!/bin/sh
set -e

cd /app

if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

# Dev container only. The dashboard bind mount can leave stale .next chunks on disk.
if [ "$1" = "npm" ] && [ "$2" = "run" ] && [ "$3" = "dev" ]; then
  rm -rf /app/.next
fi

exec "$@"
