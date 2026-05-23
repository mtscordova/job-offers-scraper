import time
import requests
from .base import JobOffer
from settings import settings

API_URL = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"


def scrape() -> list[JobOffer]:
    jobs = []
    session = requests.Session()
    session.headers.update({**settings.headers, "Accept": "application/json"})

    for company in settings.greenhouse_companies:
        resp = session.get(API_URL.format(company=company), timeout=settings.request_timeout)
        if resp.status_code != 200:
            time.sleep(settings.request_delay)
            continue

        for item in resp.json().get("jobs", []):
            title = item.get("title", "")
            if not settings.matches_keywords(title):
                continue
            jobs.append(JobOffer(
                title=title,
                company=company.replace("-", " ").title(),
                location=item.get("location", {}).get("name", ""),
                url=item.get("absolute_url", ""),
                source="greenhouse",
                posted_at=item.get("updated_at"),
            ))

        time.sleep(settings.request_delay)

    return jobs
