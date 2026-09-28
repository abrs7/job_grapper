"""Write results as CSV or JSON."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import TextIO

from job_grabber.models import Job

CSV_COLUMNS = [
    "score",
    "eligibility",
    "title",
    "company",
    "location",
    "salary",
    "posted_at",
    "url",
    "contact_emails",
    "recruiter_search_url",
    "tags",
    "source",
    "source_id",
]


def write_csv(jobs: list[Job], stream: TextIO) -> None:
    writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for job in jobs:
        row = job.to_dict()
        row["contact_emails"] = "; ".join(job.contact_emails)
        row["tags"] = "; ".join(job.tags)
        writer.writerow(row)


def write_json(jobs: list[Job], stream: TextIO, include_description: bool = False) -> None:
    json.dump(
        [job.to_dict(include_description=include_description) for job in jobs],
        stream,
        indent=2,
        ensure_ascii=False,
    )
    stream.write("\n")


def save(jobs: list[Job], path: Path, include_description: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        if path.suffix.lower() == ".json":
            write_json(jobs, stream, include_description=include_description)
        else:
            write_csv(jobs, stream)
