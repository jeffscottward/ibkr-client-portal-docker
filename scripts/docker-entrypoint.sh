#!/bin/sh
set -eu

append_java_proxy() {
  scheme="$1"
  proxy_url="$2"

  if [ -z "$proxy_url" ]; then
    return 0
  fi

  without_scheme="$proxy_url"
  case "$without_scheme" in
    *://*) without_scheme="${without_scheme#*://}" ;;
  esac

  without_auth="${without_scheme#*@}"
  host_port="${without_auth%%/*}"
  host="${host_port%:*}"
  port="${host_port##*:}"

  if [ -z "$host" ]; then
    return 0
  fi

  if [ "$host" = "$port" ]; then
    if [ "$scheme" = "https" ]; then
      port="443"
    else
      port="80"
    fi
  fi

  JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -D${scheme}.proxyHost=${host} -D${scheme}.proxyPort=${port}"
  export JAVA_TOOL_OPTIONS
}

proxy_https="${HTTPS_PROXY:-${https_proxy:-${HTTP_PROXY:-${http_proxy:-}}}}"
proxy_http="${HTTP_PROXY:-${http_proxy:-$proxy_https}}"

append_java_proxy "https" "$proxy_https"
append_java_proxy "http" "$proxy_http"
gateway_config="${IBKR_GATEWAY_CONFIG:-root/conf.yaml}"

non_proxy="${NO_PROXY:-${no_proxy:-}}"
if [ -n "$non_proxy" ]; then
  java_non_proxy="$(printf '%s' "$non_proxy" | tr ',' '|' | sed 's/[[:space:]]//g')"
  JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Dhttp.nonProxyHosts=${java_non_proxy}"
  export JAVA_TOOL_OPTIONS
fi

if [ "${IBKR_ENTRYPOINT_DRY_RUN:-}" = "1" ]; then
  printf '%s\n' "${JAVA_TOOL_OPTIONS:-}"
  printf 'IBKR_GATEWAY_CONFIG=%s\n' "$gateway_config"
  exit 0
fi

if [ "$#" -eq 0 ]; then
  set -- sh bin/run.sh "$gateway_config"
fi

exec "$@"
