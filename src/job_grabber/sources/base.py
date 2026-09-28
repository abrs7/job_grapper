"""Base class for job sources.

Every source talks to an official, public API or RSS feed that the board publishes for
exactly this kind of use. Sources never log in, never scrape HTML pages, and never touch
LinkedIn (its terms forbid automated access).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from job_grabber import http
from job_grabber.models import Job


class Source(ABC):
    name: str = ""
    homepage: str = ""
    # Attribution text that the board asks re-users to display.
    attribution: str = ""

    def __init__(
        self,
        fetch_json: Callable[[str], Any] | None = None,
        fetch_text: Callable[[str], str] | None = None,
    ) -> None:
        self._fetch_json = fetch_json or http.get_json
        self._fetch_text = fetch_text or http.get_text

    @abstractmethod
    def search(self, keywords: list[str], limit: int = 100) -> list[Job]:
        """Return jobs matching any of the keywords (sources may filter server side)."""
