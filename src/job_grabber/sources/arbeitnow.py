from __future__ import annotations

from job_grabber.models import Job
from job_grabber.sources.base import Source
from job_grabber.text import parse_date


class ArbeitnowSource(Source):
    """https://www.arbeitnow.com/api/job-board-api (free public API, mostly Europe)."""

    name = "arbeitnow"
    homepage = "https://www.arbeitnow.com"
    attribution = "Jobs from Arbeitnow (https://www.arbeitnow.com)"
    api_url = "https://www.arbeitnow.com/api/job-board-api"

    def search(self, keywords: list[str], limit: int = 100) -> list[Job]:
        payload = self._fetch_json(self.api_url)
        # Only remote roles are useful here; on-site European jobs are dropped at the source.
        items = [item for item in payload.get("data", []) if item.get("remote")]
        return [self.parse(item) for item in items[:limit]]

    def parse(self, item: dict) -> Job:
        return Job(
            source=self.name,
            source_id=str(item.get("slug", "")),
            title=item.get("title", "").strip(),
            company=item.get("company_name", "").strip(),
            url=item.get("url", ""),
            location=item.get("location", "") or "",
            posted_at=parse_date(item.get("created_at")),
            tags=list(item.get("tags") or []) + list(item.get("job_types") or []),
            description=item.get("description", "") or "",
        )
