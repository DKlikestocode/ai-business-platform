#!/bin/sh
set -e

if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

if [ "$1" = "npm" ] && [ "$2" = "run" ] && [ "$3" = "dev" ]; then
  rm -rf .next
fi

exec "$@"
