#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PM2_NAME="${PM2_NAME:-ibkr-vertex-ai-fund-gateway}"
IBKR_GATEWAY_ZIP_URL="${IBKR_GATEWAY_ZIP_URL:-https://download2.interactivebrokers.com/portal/clientportal.beta.gw.zip}"
LOGIN_URL="${IBKR_LOGIN_URL:-https://localhost:5000/}"
API_BASE_URL="${IBKR_API_BASE_URL:-https://localhost:5000/v1/api}"
LOGIN_TIMEOUT_SECONDS="${LOGIN_TIMEOUT_SECONDS:-900}"

cd "$ROOT_DIR"
export IBKR_GATEWAY_ZIP_URL

for command_name in docker pm2 uv; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
done

if pm2 describe "$PM2_NAME" >/dev/null 2>&1; then
  pm2 restart "$PM2_NAME" --update-env
else
  pm2 start "docker compose up --build" --name "$PM2_NAME" --cwd "$ROOT_DIR" --time
fi

echo "Waiting for gateway to accept HTTPS requests"
uv run scripts/wait_for_gateway.py --url "$LOGIN_URL"

if command -v open >/dev/null 2>&1; then
  open "$LOGIN_URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$LOGIN_URL" >/dev/null 2>&1 || true
else
  echo "Open this URL to log in: $LOGIN_URL"
fi

echo "Waiting for IBKR login at $LOGIN_URL"
uv run scripts/wait_for_login.py \
  --base-url "$API_BASE_URL" \
  --timeout "$LOGIN_TIMEOUT_SECONDS"

uv run scripts/read_only_check.py --base-url "$API_BASE_URL"
