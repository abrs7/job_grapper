"""Collect the contact details a posting publishes itself.

Only emails printed in the posting are extracted. For recruiters, the tool builds a LinkedIn
people-search link you open yourself; it never visits or scrapes LinkedIn.
"""

from __future__ import annotations

import html
import re
from urllib.parse import quote

from job_grabber.models import Job

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_IGNORED_PREFIXES = ("noreply", "no-reply", "donotreply", "do-not-reply")
_IGNORED_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")


def extract_emails(text: str) -> list[str]:
    found: list[str] = []
    for match in _EMAIL_RE.findall(html.unescape(text or "")):
        email = match.strip(".").lower()
        if email.startswith(_IGNORED_PREFIXES) or email.endswith(_IGNORED_SUFFIXES):
            continue
        if email not in found:
            found.append(email)
    return found


def linkedin_recruiter_search_url(company: str) -> str:
    if not company:
        return ""
    keywords = f'"{company}" (recruiter OR "talent acquisition" OR "engineering manager")'
    return f"https://www.linkedin.com/search/results/people/?keywords={quote(keywords)}"


def enrich(job: Job) -> Job:
    job.contact_emails = extract_emails(job.description)
    job.recruiter_search_url = linkedin_recruiter_search_url(job.company)
    return job
