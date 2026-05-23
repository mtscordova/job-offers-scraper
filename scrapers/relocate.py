import re
import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer
from config import KEYWORDS, HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT, MAX_PAGES

BASE_URL = "https://relocate.me/search"
JOB_URL_RE = re.compile(r"^/[^/]+/[^/]+/[^/]+/[^/]+-\d+$")


def _matches_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in KEYWORDS)


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
        job_links = [
            a for a in soup.find_all("a", href=True)
            if JOB_URL_RE.match(a.get("href", ""))
        ]
        if not job_links:
            break

        for a in job_links:
            href = a["href"]
            if href in seen_urls:
                continue

            title_el = a.find("b")
            title = title_el.get_text(strip=True) if title_el else a.get_text(strip=True)

            if not _matches_keywords(title):
                continue

            seen_urls.add(href)
            parts = href.strip("/").split("/")
            city = parts[1].replace("-", " ").title() if len(parts) > 1 else ""
            country = parts[0].replace("-", " ").title() if parts else ""
            company = parts[2].replace("-", " ").title() if len(parts) > 2 else ""

            jobs.append(JobOffer(
                title=title,
                company=company,
                location=f"{city}, {country}",
                url=f"https://relocate.me{href}",
                source="relocate",
                remote=False,
            ))

        time.sleep(REQUEST_DELAY)
        if len(job_links) < 15:
            break

    return jobs
