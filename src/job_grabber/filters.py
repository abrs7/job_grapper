"""Relevance scoring and location eligibility.

Defaults are tuned for a backend engineer based in Addis Ababa (UTC+3): "worldwide",
EMEA, Africa and CET-ish timezone roles qualify, while US-only or EU-residency roles do not.
Everything is overridable from the CLI.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from job_grabber.models import Job
from job_grabber.text import strip_html

DEFAULT_KEYWORDS = [
    "backend",
    "back-end",
    "back end",
    "python",
    "django",
    "fastapi",
    "golang",
    "node",
    "node.js",
    "java",
    "spring",
    "software engineer",
    "software developer",
    "api",
]

DEFAULT_EXCLUDE = [
    "frontend",
    "front-end",
    "front end",
    "ios",
    "android",
    "designer",
    "marketing",
    "sales",
    "recruiter",
]

DEFAULT_ALLOW = [
    "worldwide",
    "anywhere",
    "global",
    "emea",
    "africa",
    "ethiopia",
    "utc+3",
    "utc +3",
    "gmt+3",
    "eat",
]

DEFAULT_BLOCK = [
    "us only",
    "usa only",
    "u.s. only",
    "united states only",
    "us-based",
    "must be based in the us",
    "must reside in the us",
    "north america only",
    "americas only",
    "canada only",
    "uk only",
    "eu only",
    "europe only",
    "eu residents",
    "right to work in the uk",
    "right to work in the eu",
    "latam only",
    "apac only",
]

ELIGIBLE = "eligible"
BLOCKED = "blocked"
UNKNOWN = "unknown"


def _pattern(terms: Iterable[str]) -> re.Pattern[str] | None:
    terms = [t.strip().lower() for t in terms if t.strip()]
    if not terms:
        return None
    alternation = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
    return re.compile(rf"(?<![a-z0-9])(?:{alternation})(?![a-z0-9])")


@dataclass
class Criteria:
    keywords: list[str] = field(default_factory=lambda: list(DEFAULT_KEYWORDS))
    exclude: list[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDE))
    allow: list[str] = field(default_factory=lambda: list(DEFAULT_ALLOW))
    block: list[str] = field(default_factory=lambda: list(DEFAULT_BLOCK))

    def __post_init__(self) -> None:
        self._keywords = _pattern(self.keywords)
        self._exclude = _pattern(self.exclude)
        self._allow = _pattern(self.allow)
        self._block = _pattern(self.block)

    def eligibility(self, job: Job) -> str:
        """Classify where the role can be done from."""
        location = job.location.lower()
        if self._block and self._block.search(location):
            return BLOCKED
        if self._allow and self._allow.search(location):
            # Boards often tag roles "worldwide" and then restrict them in the text.
            description = strip_html(job.description).lower()
            if self._block and self._block.search(description):
                return UNKNOWN
            return ELIGIBLE
        if job.location_restricted:
            return BLOCKED
        description = strip_html(job.description).lower()
        if self._block and self._block.search(description):
            return BLOCKED
        return UNKNOWN

    def score(self, job: Job) -> int:
        """Relevance score; 0 means the job does not match the keywords at all."""
        if not self._keywords:
            return 1
        title = job.title.lower()
        if self._exclude and self._exclude.search(title):
            return 0
        tags = " | ".join(job.tags).lower()
        title_hits = len(set(self._keywords.findall(title)))
        tag_hits = len(set(self._keywords.findall(tags)))
        if not title_hits and not tag_hits:
            return 0
        description_hits = len(set(self._keywords.findall(strip_html(job.description).lower())))
        return title_hits * 3 + tag_hits * 2 + min(description_hits, 5)
