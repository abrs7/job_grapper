import csv
import json
from datetime import datetime, timezone

from job_grabber import cli
from job_grabber.filters import Criteria
from job_grabber.pipeline import fetch_all, process
from job_grabber.sources import SOURCES

NOW = datetime(2026, 9, 28, tzinfo=timezone.utc)


def all_sources(fake_fetch):
    fetch_json, fetch_text = fake_fetch
    return [cls(fetch_json=fetch_json, fetch_text=fetch_text) for cls in SOURCES.values()]


def test_process_filters_dedupes_and_ranks(fake_fetch):
    raw = fetch_all(all_sources(fake_fetch), [], limit=100)
    jobs = process(raw, Criteria(), max_age_days=30, now=NOW)
    titles = [(j.company, j.title) for j in jobs]

    assert ("US Corp", "Backend Engineer (Go)") not in titles  # US only
    assert ("Pixel Co", "Senior Frontend Developer") not in titles  # excluded title
    assert ("Old Co", "Backend Developer") not in titles  # too old
    assert ("Munich AG", "Python Developer") not in titles  # on-site
    # Acme appears on two boards but only once in the output, with emails merged.
    acme = [j for j in jobs if j.company == "Acme Cloud"]
    assert len(acme) == 1
    assert acme[0].contact_emails == ["jobs@acme.example", "hiring@acme.example"]
    # Eligible roles rank ahead of unknown ones.
    assert jobs[-1].eligibility == "unknown"
    assert all(j.recruiter_search_url for j in jobs)


def test_eligible_only(fake_fetch):
    raw = fetch_all(all_sources(fake_fetch), [], limit=100)
    jobs = process(raw, Criteria(), eligible_only=True, now=NOW)
    assert jobs and all(j.eligibility == "eligible" for j in jobs)


def test_failing_source_is_skipped(capsys):
    class Broken(SOURCES["remotive"]):
        def search(self, keywords, limit=100):
            raise OSError("boom")

    assert fetch_all([Broken()], [], limit=10) == []
    assert "remotive failed: boom" in capsys.readouterr().err


def test_cli_writes_csv_and_json(tmp_path, monkeypatch, fake_fetch):
    fetch_json, fetch_text = fake_fetch
    monkeypatch.setattr("job_grabber.http.get_json", fetch_json)
    monkeypatch.setattr("job_grabber.http.get_text", fetch_text)

    out_csv = tmp_path / "jobs.csv"
    assert cli.main(["search", "--out", str(out_csv), "--max-age-days", "0"]) == 0
    rows = list(csv.DictReader(out_csv.open(encoding="utf-8")))
    assert rows and {"title", "company", "contact_emails", "recruiter_search_url"} <= rows[0].keys()

    out_json = tmp_path / "jobs.json"
    assert cli.main(["search", "--sources", "remotive", "--out", str(out_json)]) == 0
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert isinstance(data, list)


def test_cli_rejects_unknown_source(capsys):
    assert cli.main(["search", "--sources", "linkedin"]) == 2
    assert "unknown source" in capsys.readouterr().err
