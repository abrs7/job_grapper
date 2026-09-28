from __future__ import annotations

import xml.etree.ElementTree as ET

from job_grabber.models import Job
from job_grabber.sources.base import Source
from job_grabber.text import parse_date


class WeWorkRemotelySource(Source):
    """We Work Remotely public RSS feed for back-end programming jobs."""

    name = "weworkremotely"
    homepage = "https://weworkremotely.com"
    attribution = "Jobs from We Work Remotely (https://weworkremotely.com)"
    feed_url = "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss"

    def search(self, keywords: list[str], limit: int = 100) -> list[Job]:
        root = ET.fromstring(self._fetch_text(self.feed_url))
        return [self.parse(item) for item in root.iter("item")][:limit]

    def parse(self, item: ET.Element) -> Job:
        raw_title = (item.findtext("title") or "").strip()
        # Titles look like "Company: Role".
        company, _, title = raw_title.partition(": ")
        if not title:
            company, title = "", raw_title
        link = (item.findtext("link") or "").strip()
        return Job(
            source=self.name,
            source_id=(item.findtext("guid") or link).strip(),
            title=title.strip(),
            company=company.strip(),
            url=link,
            # WWR's region tag ("Anywhere in the World") is not always accurate; the eligibility
            # check also reads the description.
            location=(item.findtext("region") or "").strip(),
            posted_at=parse_date(item.findtext("pubDate")),
            tags=[t for t in [(item.findtext("category") or "").strip()] if t],
            description=item.findtext("description") or "",
        )
