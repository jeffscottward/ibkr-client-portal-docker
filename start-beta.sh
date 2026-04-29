#!/usr/bin/env bash
set -euo pipefail

IBKR_GATEWAY_ZIP_URL=https://download2.interactivebrokers.com/portal/clientportal.beta.gw.zip exec "$(dirname "$0")/start.sh"
