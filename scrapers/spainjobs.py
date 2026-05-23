import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from .base import JobOffer
from config import HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT, MAX_PAGES

BASE_URL = "https://spainjobs.io/jobs/c/data"
SITE = "https://spainjobs.io"

_RELATIVE_DATE_RE = re.compile(r"Published (\d+)\s+(day|week|month)s?\s+ago", re.IGNORECASE)


def _parse_date(text: str) -> str | None:
    m = _RELATIVE_DATE_RE.search(text)
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    delta = {"day": timedelta(days=n), "week": timedelta(weeks=n), "month": timedelta(days=30 * n)}[unit]
    return (datetime.now(timezone.utc) - delta).date().isoformat()


def _parse_article(art) -> JobOffer | None:
    link = art.select_one("a[aria-label]")
    if not link:
        return None

    href = link.get("href", "")
    url = f"{SITE}{href}" if href.startswith("/") else href

    texts = [t.strip() for t in art.get_text(separator="|").split("|") if t.strip()]
    if len(texts) < 3:
        return None

    company = texts[0]
    date_text = next((t for t in texts if "Published" in t), "")
    title = texts[2]
    location = texts[3] if len(texts) > 3 else ""

    remote = "remote" in location.lower()

    return JobOffer(
        title=title,
        company=company,
        location=location,
        url=url,
        source="spainjobs",
        remote=remote,
        posted_at=_parse_date(date_text),
    )


def scrape() -> list[JobOffer]:
    jobs = []
    seen_urls = set()
    session = requests.Session()
    session.headers.update(HEADERS)

    for page in range(1, MAX_PAGES + 1):
        params = {"page": page} if page > 1 else {}
        resp = session.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "lxml")
        articles = soup.select("article")
        if not articles:
            break

        for art in articles:
            job = _parse_article(art)
            if job and job.url not in seen_urls:
                seen_urls.add(job.url)
                jobs.append(job)

        if len(articles) < 10:
            break

        time.sleep(REQUEST_DELAY)

    return jobs
