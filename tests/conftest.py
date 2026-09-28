import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_text():
    def load(name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8")

    return load


@pytest.fixture
def fake_fetch(fixture_text):
    """Map URLs to fixture files so no test touches the network."""

    routes = {
        "remotive.com": "remotive.json",
        "remoteok.com": "remoteok.json",
        "arbeitnow.com": "arbeitnow.json",
        "weworkremotely.com": "weworkremotely.rss",
        "himalayas.app": "himalayas.json",
    }

    def fetch_text(url: str) -> str:
        if "himalayas.app" in url and "offset=0" not in url:
            return json.dumps({"jobs": []})
        for host, name in routes.items():
            if host in url:
                return fixture_text(name)
        raise AssertionError(f"unexpected URL {url}")

    def fetch_json(url: str):
        return json.loads(fetch_text(url))

    return fetch_json, fetch_text
