"""Command-line entry point: `job-grabber search` and `job-grabber sources`."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from job_grabber import __version__
from job_grabber.filters import (
    DEFAULT_ALLOW,
    DEFAULT_BLOCK,
    DEFAULT_EXCLUDE,
    DEFAULT_KEYWORDS,
    Criteria,
)
from job_grabber.output import save
from job_grabber.pipeline import fetch_all, process
from job_grabber.sources import SOURCES


def _csv_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-grabber",
        description="Find remote backend roles on public job boards.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sources", help="list the supported job boards")

    search = sub.add_parser("search", help="fetch, filter and save matching jobs")
    search.add_argument(
        "--sources",
        type=_csv_list,
        default=list(SOURCES),
        help=f"comma-separated boards to query (default: all: {', '.join(SOURCES)})",
    )
    search.add_argument(
        "--keywords",
        type=_csv_list,
        default=None,
        help="comma-separated keywords matched against title and tags "
        "(default: backend, python, django, golang, node, java, ...)",
    )
    search.add_argument(
        "--exclude", type=_csv_list, default=None, help="title terms that drop a job"
    )
    search.add_argument(
        "--allow", type=_csv_list, default=[], help="extra location terms you can work from"
    )
    search.add_argument(
        "--block", type=_csv_list, default=[], help="extra location terms you cannot work from"
    )
    search.add_argument(
        "--eligible-only",
        action="store_true",
        help="keep only roles whose location clearly includes you (drop 'unknown')",
    )
    search.add_argument(
        "--max-age-days", type=int, default=30, help="drop postings older than this (0 = off)"
    )
    search.add_argument("--limit", type=int, default=100, help="max jobs fetched per source")
    search.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output file, .csv or .json (default: output/jobs-<date>.csv)",
    )
    search.add_argument(
        "--include-description",
        action="store_true",
        help="include the full posting text (JSON output only)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "sources":
        for name, cls in SOURCES.items():
            print(f"{name:16} {cls.homepage}")
        return 0

    unknown = [name for name in args.sources if name not in SOURCES]
    if unknown:
        print(f"error: unknown source(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    criteria = Criteria(
        keywords=args.keywords or list(DEFAULT_KEYWORDS),
        exclude=args.exclude if args.exclude is not None else list(DEFAULT_EXCLUDE),
        allow=DEFAULT_ALLOW + args.allow,
        block=DEFAULT_BLOCK + args.block,
    )

    sources = [SOURCES[name]() for name in args.sources]
    raw = fetch_all(sources, criteria.keywords, limit=args.limit)
    jobs = process(
        raw,
        criteria,
        max_age_days=args.max_age_days or None,
        eligible_only=args.eligible_only,
    )

    out = args.out or Path("output") / f"jobs-{date.today():%Y%m%d}.csv"
    save(jobs, out, include_description=args.include_description)

    eligible = sum(1 for job in jobs if job.eligibility == "eligible")
    with_email = sum(1 for job in jobs if job.contact_emails)
    print(
        f"{len(jobs)} matching jobs ({eligible} clearly open to your location, "
        f"{with_email} with a public contact email) -> {out}"
    )
    for job in jobs[:10]:
        print(f"  [{job.score:>2}] {job.title} @ {job.company} ({job.location or '?'})")
    print("Sources: " + "; ".join(SOURCES[name].attribution for name in args.sources))
    return 0
