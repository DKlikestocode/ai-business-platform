#!/bin/sh
set -e

# Volume mount at /app/.next — clear contents only (not the mount point itself).
if [ -d /app/.next ]; then
  find /app/.next -mindepth 1 -delete 2>/dev/null || true
fi

exec npm run dev
