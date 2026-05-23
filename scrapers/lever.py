import time
import requests
from datetime import datetime, timezone
from .base import JobOffer
from settings import settings

API_URL = "https://api.lever.co/v0/postings/{company}?mode=json"


def scrape() -> list[JobOffer]:
    jobs = []
    session = requests.Session()
    session.headers.update({**settings.headers, "Accept": "application/json"})

    for company in settings.lever_companies:
        resp = session.get(API_URL.format(company=company), timeout=settings.request_timeout)
        if resp.status_code != 200:
            time.sleep(settings.request_delay)
            continue

        for item in resp.json():
            title = item.get("text", "")
            if not settings.matches_keywords(title):
                continue

            created_ms = item.get("createdAt")
            posted_at = (
                datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc).isoformat()
                if created_ms else None
            )

            jobs.append(JobOffer(
                title=title,
                company=company.replace("-", " ").title(),
                location=item.get("categories", {}).get("location", ""),
                url=item.get("hostedUrl", ""),
                source="lever",
                posted_at=posted_at,
            ))

        time.sleep(settings.request_delay)

    return jobs
