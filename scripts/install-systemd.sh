#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo: sudo ./scripts/install-systemd.sh" >&2
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_PATH="/etc/systemd/system/ibkr-client-portal-docker-gateway.service"
GATEWAY_ZIP_URL="${IBKR_GATEWAY_ZIP_URL:-https://download2.interactivebrokers.com/portal/clientportal.beta.gw.zip}"
GATEWAY_CONFIG="${IBKR_GATEWAY_CONFIG:-root/conf.yaml}"
PROXY_ENVIRONMENT=""

for proxy_var in HTTP_PROXY HTTPS_PROXY NO_PROXY http_proxy https_proxy no_proxy; do
  if [[ -n "${!proxy_var:-}" ]]; then
    PROXY_ENVIRONMENT+="Environment=\"${proxy_var}=${!proxy_var}\""$'\n'
  fi
done

if docker compose version >/dev/null 2>&1; then
  COMPOSE_COMMAND="$(command -v docker) compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_COMMAND="$(command -v docker-compose)"
else
  echo "Docker Compose is required. Run sudo ./scripts/setup-kali-host.sh first." >&2
  exit 1
fi

cat >"${SERVICE_PATH}" <<SERVICE
[Unit]
Description=IBKR Client Portal Docker Gateway
After=docker.service network-online.target
Wants=docker.service network-online.target

[Service]
Type=simple
WorkingDirectory=${REPO_DIR}
Environment=IBKR_GATEWAY_ZIP_URL=${GATEWAY_ZIP_URL}
Environment=IBKR_GATEWAY_CONFIG=${GATEWAY_CONFIG}
${PROXY_ENVIRONMENT}ExecStart=${COMPOSE_COMMAND} up --build
ExecStop=${COMPOSE_COMMAND} down
Restart=always
RestartSec=10
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable ibkr-client-portal-docker-gateway.service

echo "Installed ${SERVICE_PATH}"
echo "Start with: sudo systemctl start ibkr-client-portal-docker-gateway"
