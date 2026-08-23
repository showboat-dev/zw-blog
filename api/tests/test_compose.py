from pathlib import Path

import yaml


def test_compose_only_web_and_api() -> None:
    compose = yaml.safe_load(
        (Path(__file__).resolve().parents[2] / "docker-compose.yml").read_text(encoding="utf-8")
    )
    assert sorted(compose["services"]) == ["api", "web"]
    assert "nginx" not in compose["services"]
    assert "redis" not in compose["services"]
    assert "blog_data" in compose["volumes"]
