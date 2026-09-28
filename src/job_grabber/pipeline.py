"""Fetch from every source, then filter, enrich, dedupe and rank."""

from __future__ import annotations

import sys
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone

from job_grabber.contacts import enrich
from job_grabber.filters import BLOCKED, ELIGIBLE, Criteria
from job_grabber.models import Job
from job_grabber.sources import Source


def fetch_all(sources: Iterable[Source], keywords: list[str], limit: int) -> list[Job]:
    jobs: list[Job] = []
    for source in sources:
        try:
            found = source.search(keywords, limit=limit)
        except Exception as exc:  # one broken board must not stop the run
            print(f"warning: {source.name} failed: {exc}", file=sys.stderr)
            continue
        print(f"{source.name}: {len(found)} jobs fetched", file=sys.stderr)
        jobs.extend(found)
    return jobs


def process(
    jobs: Iterable[Job],
    criteria: Criteria,
    max_age_days: int | None = None,
    eligible_only: bool = False,
    now: datetime | None = None,
) -> list[Job]:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max_age_days) if max_age_days else None
    kept: dict[tuple[str, str], Job] = {}
    for job in jobs:
        if cutoff and job.posted_at and job.posted_at < cutoff:
            continue
        job.score = criteria.score(job)
        if job.score <= 0:
            continue
        job.eligibility = criteria.eligibility(job)
        if job.eligibility == BLOCKED or (eligible_only and job.eligibility != ELIGIBLE):
            continue
        enrich(job)
        existing = kept.get(job.dedupe_key)
        if existing is None:
            kept[job.dedupe_key] = job
        else:
            # Same role on two boards: keep the first, but merge anything new it lacks.
            for email in job.contact_emails:
                if email not in existing.contact_emails:
                    existing.contact_emails.append(email)
    epoch = datetime.min.replace(tzinfo=timezone.utc)
    return sorted(
        kept.values(),
        key=lambda j: (j.eligibility == ELIGIBLE, j.score, j.posted_at or epoch),
        reverse=True,
    )
