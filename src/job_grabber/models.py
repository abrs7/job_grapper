"""Core data model shared by every source."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass
class Job:
    source: str
    source_id: str
    title: str
    company: str
    url: str
    location: str = ""
    # True when the board lists the only countries/timezones allowed, so anything not
    # explicitly allowed is out of reach.
    location_restricted: bool = False
    posted_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    salary: str = ""
    description: str = ""
    # Filled in by the enrichment step.
    eligibility: str = "unknown"
    contact_emails: list[str] = field(default_factory=list)
    recruiter_search_url: str = ""
    score: int = 0

    @property
    def dedupe_key(self) -> tuple[str, str]:
        return (_norm(self.company), _norm(self.title))

    def to_dict(self, include_description: bool = False) -> dict:
        data = asdict(self)
        data["posted_at"] = self.posted_at.isoformat() if self.posted_at else ""
        if not include_description:
            data.pop("description")
        return data


def _norm(value: str) -> str:
    return " ".join(value.lower().split())
