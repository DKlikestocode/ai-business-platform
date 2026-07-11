#!/usr/bin/env bash
# Deploy ai-business-platform to production (Hetzner).
# Usage:
#   ./scripts/deploy-prod.sh           # frontend + backend rebuild
#   ./scripts/deploy-prod.sh frontend  # frontend only
#   ./scripts/deploy-prod.sh backend   # backend only

set -euo pipefail

TARGET="${1:-}"
SERVICES=()

case "$TARGET" in
  "" | all)
    SERVICES=(frontend backend)
    ;;
  frontend | backend)
    SERVICES=("$TARGET")
    ;;
  *)
    echo "Usage: $0 [frontend|backend|all]" >&2
    exit 1
    ;;
esac

SERVICE_ARGS="${SERVICES[*]}"

ssh root@167.233.104.25 bash -s <<EOF
set -euo pipefail
cd /opt/ai-business-platform
git pull origin main
docker compose --env-file .env -f infrastructure/docker/docker-compose.prod.yml up --build -d ${SERVICE_ARGS}
EOF

echo "Deploy finished: ${SERVICE_ARGS}"
