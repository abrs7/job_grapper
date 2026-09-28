from job_grabber.contacts import extract_emails, linkedin_recruiter_search_url
from job_grabber.filters import BLOCKED, ELIGIBLE, UNKNOWN, Criteria
from job_grabber.models import Job


def job(**kwargs):
    base = {"source": "t", "source_id": "1", "title": "Backend Engineer", "company": "X", "url": ""}
    base.update(kwargs)
    return Job(**base)


def test_eligibility_classes():
    c = Criteria()
    assert c.eligibility(job(location="Worldwide")) == ELIGIBLE
    assert c.eligibility(job(location="EMEA")) == ELIGIBLE
    assert c.eligibility(job(location="USA Only")) == BLOCKED
    assert c.eligibility(job(location="Berlin")) == UNKNOWN
    eu_text = "Must have the right to work in the EU"
    assert c.eligibility(job(location="", description=eu_text)) == BLOCKED
    assert c.eligibility(job(location="", description="EU only, sorry")) == BLOCKED


def test_worldwide_tag_contradicted_by_text_is_unknown():
    c = Criteria()
    j = job(location="Anywhere in the World", description="<p>US only applicants.</p>")
    assert c.eligibility(j) == UNKNOWN


def test_eat_does_not_match_inside_words():
    c = Criteria()
    assert c.eligibility(job(location="Seattle")) == UNKNOWN


def test_score_requires_title_or_tag_match():
    c = Criteria()
    assert c.score(job(title="Office Manager", tags=[], description="python")) == 0
    assert c.score(job(title="Senior Frontend Developer", tags=["python"])) == 0
    assert c.score(job(title="Python Backend Engineer")) > c.score(
        job(title="Engineer", tags=["python"])
    )


def test_custom_keywords():
    c = Criteria(keywords=["rust"])
    assert c.score(job(title="Rust Engineer")) > 0
    assert c.score(job(title="Python Engineer")) == 0


def test_extract_emails():
    text = "Mail jobs@acme.example, noreply@acme.example or logo@2x.png. Also JOBS@acme.example."
    assert extract_emails(text) == ["jobs@acme.example"]


def test_linkedin_search_url_is_a_plain_link():
    url = linkedin_recruiter_search_url("Acme Cloud")
    assert url.startswith("https://www.linkedin.com/search/results/people/?keywords=")
    assert "Acme%20Cloud" in url
    assert linkedin_recruiter_search_url("") == ""


def test_restricted_location_lists_block_unless_allowed():
    c = Criteria()
    us = job(location="United States (UTC-8, UTC-5)", location_restricted=True)
    assert c.eligibility(us) == BLOCKED
    ours = job(location="Worldwide (UTC+2, UTC+3)", location_restricted=True)
    assert c.eligibility(ours) == ELIGIBLE
