#!/usr/bin/env bash
# Generate infrastructure/docker/www/index.html with the tokenized widget embed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker compose --env-file ../../.env -f docker-compose.prod.yml exec -T backend \
  python -m app.scripts.write_pilot_website > www/index.html

echo "Wrote ${ROOT}/www/index.html"
