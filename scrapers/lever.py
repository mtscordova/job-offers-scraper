import time
import requests
from .base import JobOffer
from config import LEVER_COMPANIES, KEYWORDS, HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT

API_URL = "https://api.lever.co/v0/postings/{company}?mode=json"


def _matches_keywords(title: str) -> bool:
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in KEYWORDS)


def scrape() -> list[JobOffer]:
    jobs = []
    session = requests.Session()
    session.headers.update({**HEADERS, "Accept": "application/json"})

    for company in LEVER_COMPANIES:
        resp = session.get(
            API_URL.format(company=company),
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            time.sleep(REQUEST_DELAY)
            continue

        for item in resp.json():
            title = item.get("text", "")
            if not _matches_keywords(title):
                continue

            categories = item.get("categories", {})
            location = categories.get("location", "")
            url = item.get("hostedUrl", "")

            created_ms = item.get("createdAt")
            posted_at = None
            if created_ms:
                from datetime import datetime, timezone
                posted_at = datetime.fromtimestamp(
                    created_ms / 1000, tz=timezone.utc
                ).isoformat()

            jobs.append(JobOffer(
                title=title,
                company=company.replace("-", " ").title(),
                location=location,
                url=url,
                source="lever",
                posted_at=posted_at,
            ))

        time.sleep(REQUEST_DELAY)

    return jobs
