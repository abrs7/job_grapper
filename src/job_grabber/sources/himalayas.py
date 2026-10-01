from __future__ import annotations

from urllib.parse import urlencode

from job_grabber.models import Job
from job_grabber.sources.base import Source
from job_grabber.text import parse_date

PAGE_SIZE = 20  # Himalayas caps each page at 20 results.


class HimalayasSource(Source):
    """https://himalayas.app/jobs/api (public API; requires a link back to Himalayas)."""

    name = "himalayas"
    homepage = "https://himalayas.app"
    attribution = "Jobs from Himalayas (https://himalayas.app)"
    api_url = "https://himalayas.app/jobs/api"

    def search(self, keywords: list[str], limit: int = 100) -> list[Job]:
        jobs: list[Job] = []
        offset = 0
        while len(jobs) < limit:
            query = urlencode({"limit": PAGE_SIZE, "offset": offset})
            page = self._fetch_json(f"{self.api_url}?{query}").get("jobs", [])
            if not page:
                break
            jobs.extend(self.parse(item) for item in page)
            offset += len(page)
        return jobs[:limit]

    def parse(self, item: dict) -> Job:
        locations = item.get("locationRestrictions") or []
        location = ", ".join(str(loc) for loc in locations) or "Worldwide"
        timezones = item.get("timezoneRestrictions") or []
        if timezones:
            location += " (" + ", ".join(f"UTC{tz:+g}" for tz in timezones) + ")"
        salary = ""
        if item.get("minSalary") or item.get("maxSalary"):
            salary = (
                f"{item.get('minSalary') or '?'}-{item.get('maxSalary') or '?'} "
                f"{item.get('currency') or ''}"
            ).strip()
        return Job(
            source=self.name,
            source_id=str(item.get("guid") or item.get("applicationLink", "")),
            title=item.get("title", "").strip(),
            company=item.get("companyName", "").strip(),
            url=item.get("applicationLink") or item.get("guid", ""),
            location=location,
            location_restricted=bool(locations or timezones),
            posted_at=parse_date(item.get("pubDate")),
            tags=list(item.get("categories") or []),
            salary=salary,
            description=item.get("description") or item.get("excerpt", "") or "",
        )
