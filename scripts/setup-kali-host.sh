#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo: sudo ./scripts/setup-kali-host.sh" >&2
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_USER="${SUDO_USER:-root}"

apt-get update
apt-get install -y \
  ca-certificates \
  chromium \
  docker.io \
  git \
  openbox \
  pipx \
  python3 \
  python3-pip \
  python3-venv \
  sudo \
  x11vnc \
  xdg-utils \
  xvfb

if ! docker compose version >/dev/null 2>&1; then
  if apt-cache show docker-compose-plugin >/dev/null 2>&1; then
    apt-get install -y docker-compose-plugin
  else
    apt-get install -y docker-compose
  fi
fi

if ! command -v websockify >/dev/null 2>&1 || [[ ! -d /usr/share/novnc ]]; then
  apt-get install -y novnc websockify
fi

systemctl enable --now docker

if [[ "${TARGET_USER}" != "root" ]]; then
  usermod -aG docker "${TARGET_USER}"
fi

if ! command -v uv >/dev/null 2>&1; then
  PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install uv
fi

if [[ "${TARGET_USER}" != "root" ]]; then
  sudo -u "${TARGET_USER}" -H uv sync --project "${REPO_DIR}"
else
  uv sync --project "${REPO_DIR}"
fi

echo "Kali host setup complete."
echo "If ${TARGET_USER} was newly added to the docker group, reconnect SSH before running Docker as that user."
