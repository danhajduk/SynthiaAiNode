#!/usr/bin/env bash
set -euo pipefail

BACKEND_SERVICE="synthia-ai-node-backend.service"
FRONTEND_SERVICE="synthia-ai-node-frontend.service"

if systemctl --user list-unit-files | rg -q "^${BACKEND_SERVICE}|^${FRONTEND_SERVICE}"; then
  echo "Restarting user systemd services..."
  systemctl --user restart "$BACKEND_SERVICE" "$FRONTEND_SERVICE"
  systemctl --user status "$BACKEND_SERVICE" --no-pager -n 5 || true
  systemctl --user status "$FRONTEND_SERVICE" --no-pager -n 5 || true
else
  echo "User systemd units not installed. Falling back to local stack-control script."
  "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/stack-control.sh" restart
fi
