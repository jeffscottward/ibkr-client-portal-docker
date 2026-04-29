from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_compose_passes_proxy_environment_to_docker_build() -> None:
    compose = (ROOT / "docker-compose.yaml").read_text()

    for name in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy"):
        assert f"{name}: ${{{name}:-}}" in compose


def test_dockerfile_declares_proxy_args_before_networked_gateway_build_step() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()
    build_step_index = dockerfile.index("RUN apk add")

    for name in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy"):
        assert dockerfile.index(f"ARG {name}") < build_step_index
