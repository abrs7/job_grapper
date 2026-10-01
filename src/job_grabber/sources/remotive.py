from __future__ import annotations

from urllib.parse import urlencode

from job_grabber.models import Job
from job_grabber.sources.base import Source
from job_grabber.text import parse_date


class RemotiveSource(Source):
    """https://remotive.com/api/remote-jobs (public API; asks for at most ~4 calls a day)."""

    name = "remotive"
    homepage = "https://remotive.com"
    attribution = "Jobs from Remotive (https://remotive.com)"
    api_url = "https://remotive.com/api/remote-jobs"

    def search(self, keywords: list[str], limit: int = 100) -> list[Job]:
        params = {"category": "software-dev", "limit": limit}
        payload = self._fetch_json(f"{self.api_url}?{urlencode(params)}")
        return [self.parse(item) for item in payload.get("jobs", [])]

    def parse(self, item: dict) -> Job:
        return Job(
            source=self.name,
            source_id=str(item.get("id", "")),
            title=item.get("title", "").strip(),
            company=item.get("company_name", "").strip(),
            url=item.get("url", ""),
            location=item.get("candidate_required_location", "") or "",
            posted_at=parse_date(item.get("publication_date")),
            tags=list(item.get("tags") or []),
            salary=item.get("salary", "") or "",
            description=item.get("description", "") or "",
        )
