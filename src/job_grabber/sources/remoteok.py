from __future__ import annotations

from job_grabber.models import Job
from job_grabber.sources.base import Source
from job_grabber.text import parse_date


class RemoteOKSource(Source):
    """https://remoteok.com/api (public API; requires a link back to Remote OK)."""

    name = "remoteok"
    homepage = "https://remoteok.com"
    attribution = "Jobs from Remote OK (https://remoteok.com)"
    api_url = "https://remoteok.com/api"

    def search(self, keywords: list[str], limit: int = 100) -> list[Job]:
        payload = self._fetch_json(self.api_url)
        # The first element is a legal notice, not a job.
        items = [item for item in payload if isinstance(item, dict) and item.get("position")]
        return [self.parse(item) for item in items[:limit]]

    def parse(self, item: dict) -> Job:
        salary = ""
        if item.get("salary_min") or item.get("salary_max"):
            salary = f"{item.get('salary_min') or '?'}-{item.get('salary_max') or '?'} USD"
        return Job(
            source=self.name,
            source_id=str(item.get("id", "")),
            title=item.get("position", "").strip(),
            company=item.get("company", "").strip(),
            url=item.get("url") or item.get("apply_url", ""),
            location=item.get("location", "") or "",
            posted_at=parse_date(item.get("epoch") or item.get("date")),
            tags=list(item.get("tags") or []),
            salary=salary,
            description=item.get("description", "") or "",
        )
