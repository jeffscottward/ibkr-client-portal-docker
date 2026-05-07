import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_compose_passes_proxy_environment_to_docker_build() -> None:
    compose = (ROOT / "docker-compose.yaml").read_text()

    for name in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy"):
        assert f"{name}: ${{{name}:-}}" in compose


def test_compose_passes_proxy_environment_to_gateway_container() -> None:
    compose = (ROOT / "docker-compose.yaml").read_text()
    environment_index = compose.index("environment:")

    for name in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy"):
        assert compose.index(f"{name}: ${{{name}:-}}", environment_index) > environment_index


def test_compose_defaults_to_standard_gateway_runtime_config() -> None:
    compose = (ROOT / "docker-compose.yaml").read_text()

    assert "IBKR_GATEWAY_CONFIG: ${IBKR_GATEWAY_CONFIG:-root/conf.yaml}" in compose


def test_dockerfile_copies_standard_and_beta_gateway_configs() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()

    assert "COPY conf.yaml /app/root/conf.yaml" in dockerfile
    assert "COPY conf.beta.yaml /app/root/conf.beta.yaml" in dockerfile


def test_beta_config_uses_beta_backend_and_docker_allowlist() -> None:
    beta_config = (ROOT / "conf.beta.yaml").read_text()

    assert 'proxyRemoteHost: "https://ndcdyn.interactivebrokers.com"' in beta_config
    assert 'svcEnvironment: "v1"' in beta_config
    assert 'ip2loc: "off"' in beta_config
    assert 'portalBaseURL: ""' in beta_config
    assert "ccp: false" in beta_config
    assert "    - 127.0.0.1" in beta_config
    assert "    - 172.*" in beta_config


def test_dockerfile_declares_proxy_args_before_networked_gateway_build_step() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()
    build_step_index = dockerfile.index("RUN apk add")

    for name in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy"):
        assert dockerfile.index(f"ARG {name}") < build_step_index


def test_gateway_entrypoint_translates_proxy_env_to_java_proxy_options() -> None:
    env = {
        "PATH": os.environ.get("PATH", ""),
        "IBKR_ENTRYPOINT_DRY_RUN": "1",
        "HTTPS_PROXY": "http://user:password@proxy.local:18080",
        "NO_PROXY": "localhost,127.0.0.1",
    }

    result = subprocess.run(
        ["sh", str(ROOT / "scripts/docker-entrypoint.sh")],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "-Dhttps.proxyHost=proxy.local" in result.stdout
    assert "-Dhttps.proxyPort=18080" in result.stdout
    assert "-Dhttp.nonProxyHosts=localhost|127.0.0.1" in result.stdout
    assert "IBKR_GATEWAY_CONFIG=root/conf.yaml" in result.stdout
    assert "user:password" not in result.stdout
