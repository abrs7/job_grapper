"""Tiny HTTP helper on top of the standard library, so the tool has no runtime dependencies."""

from __future__ import annotations

import json
import urllib.request
from typing import Any

USER_AGENT = "job-grabber/0.1 (+https://github.com/abrs7/job_grapper)"
DEFAULT_TIMEOUT = 20


def get_text(url: str, timeout: float = DEFAULT_TIMEOUT) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json, application/xml, */*"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def get_json(url: str, timeout: float = DEFAULT_TIMEOUT) -> Any:
    return json.loads(get_text(url, timeout=timeout))
