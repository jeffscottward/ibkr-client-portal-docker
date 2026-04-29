#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo: sudo ./scripts/setup-kali-host.sh" >&2
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_USER="${SUDO_USER:-root}"

write_proxy_drop_in() {
  local service_dir="$1"
  local wrote_proxy=false

  mkdir -p "${service_dir}"
  {
    echo "[Service]"
    for proxy_var in HTTP_PROXY HTTPS_PROXY NO_PROXY http_proxy https_proxy no_proxy; do
      if [[ -n "${!proxy_var:-}" ]]; then
        printf 'Environment="%s=%s"\n' "${proxy_var}" "${!proxy_var}"
        wrote_proxy=true
      fi
    done
  } >"${service_dir}/proxy.conf"

  if [[ "${wrote_proxy}" != true ]]; then
    rm -f "${service_dir}/proxy.conf"
  fi
}

apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates \
  docker.io \
  git \
  pipx \
  python3 \
  python3-pip \
  python3-venv \
  sudo \
  x11vnc \
  xdg-utils \
  xvfb

if ! docker compose version >/dev/null 2>&1; then
  if ! apt-cache policy docker-compose-plugin | grep -q "Candidate: (none)"; then
    apt-get install -y --no-install-recommends docker-compose-plugin
  else
    apt-get install -y --no-install-recommends docker-compose
  fi
fi

if ! command -v websockify >/dev/null 2>&1 || [[ ! -d /usr/share/novnc ]]; then
  apt-get install -y --no-install-recommends novnc websockify
fi

write_proxy_drop_in "/etc/systemd/system/docker.service.d"
systemctl daemon-reload
systemctl enable --now docker
systemctl restart docker

if [[ "${TARGET_USER}" != "root" ]]; then
  usermod -aG docker "${TARGET_USER}"
fi

if ! command -v uv >/dev/null 2>&1; then
  PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install uv
fi

if [[ "${TARGET_USER}" != "root" ]]; then
  sudo -u "${TARGET_USER}" -H uv sync --project "${REPO_DIR}"
  sudo -u "${TARGET_USER}" -H uv run --project "${REPO_DIR}" python -m playwright install chromium
else
  uv sync --project "${REPO_DIR}"
  uv run --project "${REPO_DIR}" python -m playwright install chromium
fi

echo "Kali host setup complete."
echo "If ${TARGET_USER} was newly added to the docker group, reconnect SSH before running Docker as that user."
