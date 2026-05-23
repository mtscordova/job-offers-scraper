import time
import requests
from .base import JobOffer
from config import GREENHOUSE_COMPANIES, KEYWORDS, HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT

API_URL = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"


def _matches_keywords(title: str) -> bool:
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in KEYWORDS)


def scrape() -> list[JobOffer]:
    jobs = []
    session = requests.Session()
    session.headers.update({**HEADERS, "Accept": "application/json"})

    for company in GREENHOUSE_COMPANIES:
        resp = session.get(
            API_URL.format(company=company),
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            time.sleep(REQUEST_DELAY)
            continue

        data = resp.json()
        for item in data.get("jobs", []):
            title = item.get("title", "")
            if not _matches_keywords(title):
                continue

            location = item.get("location", {}).get("name", "")
            url = item.get("absolute_url", "")

            jobs.append(JobOffer(
                title=title,
                company=company.replace("-", " ").title(),
                location=location,
                url=url,
                source="greenhouse",
                posted_at=item.get("updated_at"),
            ))

        time.sleep(REQUEST_DELAY)

    return jobs
