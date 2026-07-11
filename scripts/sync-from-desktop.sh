#!/usr/bin/env bash
# Copy local edits from the Desktop Cursor workspace into this repo.
# Run from ~/dev/ai-business-platform after agent changes on Desktop.
#
# Usage: ./scripts/sync-from-desktop.sh

set -euo pipefail

DESKTOP="${DESKTOP:-$HOME/Desktop/ai-agent-platform}"
DEST="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! -d "$DESKTOP" ]]; then
  echo "Desktop workspace not found: $DESKTOP" >&2
  exit 1
fi

rsync -a \
  --exclude '.git' \
  --exclude 'node_modules' \
  --exclude '.next' \
  --exclude '.env' \
  "$DESKTOP/" "$DEST/"

echo "Synced from $DESKTOP → $DEST"
echo "Next: git status && git add … && git commit"
