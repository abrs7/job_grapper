from datetime import timezone

from job_grabber.sources import SOURCES


def make(name, fake_fetch):
    fetch_json, fetch_text = fake_fetch
    return SOURCES[name](fetch_json=fetch_json, fetch_text=fetch_text)


def test_remotive_parses_jobs(fake_fetch):
    jobs = make("remotive", fake_fetch).search([])
    assert len(jobs) == 3
    first = jobs[0]
    assert first.title == "Senior Python Backend Engineer"
    assert first.company == "Acme Cloud"
    assert first.location == "Worldwide"
    assert first.posted_at.tzinfo == timezone.utc
    assert "django" in first.tags


def test_remoteok_skips_legal_notice(fake_fetch):
    jobs = make("remoteok", fake_fetch).search([])
    assert [j.source_id for j in jobs] == ["201", "202"]
    assert jobs[0].salary == "90000-120000 USD"


def test_arbeitnow_keeps_remote_only(fake_fetch):
    jobs = make("arbeitnow", fake_fetch).search([])
    assert [j.company for j in jobs] == ["Berlin GmbH"]


def test_weworkremotely_splits_company_and_title(fake_fetch):
    jobs = make("weworkremotely", fake_fetch).search([])
    assert jobs[0].company == "Enveritas"
    assert jobs[0].title == "Senior Software Engineer (Python)"
    assert jobs[0].location == "Anywhere in the World"


def test_himalayas_formats_location_and_paginates(fake_fetch):
    jobs = make("himalayas", fake_fetch).search([], limit=50)
    assert len(jobs) == 1
    assert jobs[0].location == "Worldwide (UTC+0, UTC+1, UTC+2, UTC+3)"
    assert jobs[0].salary == "80000-110000 USD"
    assert jobs[0].location_restricted
