# job-grabber

Find remote backend and software-engineering roles on public job boards, keep only the ones
you can actually take from where you live, and collect the contact details each posting
publishes, ready for tailored resumes and outreach.

v1 is a small Python CLI with no runtime dependencies. Outreach drafting and resume
tailoring are planned next and will plug into the same `Job` records.

## What it does

1. **Fetches** jobs from five boards through their official public APIs or RSS feeds:

   | Source | Endpoint | Notes |
   | --- | --- | --- |
   | Remotive | `remotive.com/api/remote-jobs` | Asks for no more than ~4 calls a day; link back required |
   | Remote OK | `remoteok.com/api` | Link back required |
   | We Work Remotely | back-end programming RSS feed | Region tag is sometimes wrong, so the text is checked too |
   | Himalayas | `himalayas.app/jobs/api` | Gives explicit country and timezone restrictions |
   | Arbeitnow | `arbeitnow.com/api/job-board-api` | Mostly Europe; only remote roles are kept |

2. **Filters** by keyword (title and tags must match), drops excluded titles (frontend, iOS,
   sales, ...) and postings older than 30 days.
3. **Checks location eligibility.** Defaults suit someone in Addis Ababa (UTC+3):
   `worldwide`, `anywhere`, `EMEA`, `Africa`, `UTC+3` count as eligible; `US only`,
   `EU only`, `right to work in the UK`, and country lists that leave you out count as
   blocked. Blocked roles are dropped; unclear ones are kept and marked `unknown`.
4. **Collects contacts**: emails printed in the posting, plus a LinkedIn people-search link
   for recruiters and engineering managers at the company, which you open yourself.
5. **Dedupes** the same role across boards, **ranks** eligible and best-matching roles first,
   and **writes** CSV or JSON.

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/abrs7/job_grapper.git
cd job_grapper
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Usage

```bash
# All boards, default backend keywords, results in output/jobs-<date>.csv
job-grabber search

# Only roles that clearly include your location, as JSON with full descriptions
job-grabber search --eligible-only --out output/jobs.json --include-description

# Narrow the keywords and boards
job-grabber search --keywords "python,django,fastapi" --sources remotive,himalayas

# Adjust location rules (e.g. you are fine with CET +/- 3h roles)
job-grabber search --allow "cet,europe timezones" --block "latam"

# List boards
job-grabber sources
```

Also runnable without installing: `python -m job_grabber search` (from `src/`, or after
`pip install -e .`).

Output columns: `score, eligibility, title, company, location, salary, posted_at, url,
contact_emails, recruiter_search_url, tags, source, source_id`.

Run it on a schedule (cron, a GitHub Action, or any job runner) at most a few times a day to
stay within the boards' fair-use limits.

## Limitations and ground rules

- **No LinkedIn scraping.** LinkedIn's terms forbid automated access, and it has no public
  jobs API. The tool only builds a people-search URL for you to open while signed in.
- **No private contact lookup.** Emails come only from the posting text. Most postings
  publish none; apply through the posting's form and use the LinkedIn link to find the
  recruiter.
- **Attribution.** Remote OK, Remotive and Himalayas require a link back if you republish
  their listings. The CLI prints the attribution line after each run.
- **Location detection is heuristic.** Always open the posting before applying; `unknown`
  means the board did not say clearly.
- A board that is down or changes its format is skipped with a warning; the rest still run.

## Development

```bash
ruff check . && ruff format --check .
pytest
```

Tests use saved fixtures in `tests/fixtures/` and never touch the network.

### Adding a source

Subclass `job_grabber.sources.base.Source`, implement `search()` to return `Job` objects,
and register the class in `job_grabber/sources/__init__.py`. Use the injected
`self._fetch_json` / `self._fetch_text` so tests can feed fixtures.

## Layout

```
src/job_grabber/
  cli.py          argparse entry point
  pipeline.py     fetch -> filter -> enrich -> dedupe -> rank
  filters.py      keyword scoring and location eligibility
  contacts.py     email extraction and LinkedIn search links
  output.py       CSV / JSON writers
  models.py       Job dataclass
  sources/        one module per job board
tests/            fixture-based tests
```

## License

MIT
