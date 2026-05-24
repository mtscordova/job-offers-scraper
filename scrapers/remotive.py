import requests
from .base import JobOffer
from settings import settings

API_URL = "https://jobicy.com/api/v2/remote-jobs"
INDUSTRIES = ["data-science"]


def scrape() -> list[JobOffer]:
    jobs = []
    seen_urls = set()
    session = requests.Session()
    session.headers.update({**settings.headers, "Accept": "application/json"})

    for industry in INDUSTRIES:
        resp = session.get(
            API_URL,
            params={"count": 100, "industry": industry},
            timeout=settings.request_timeout,
        )
        if resp.status_code != 200:
            continue

        for item in resp.json().get("jobs", []):
            url = item.get("url") or ""
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            title = item.get("jobTitle") or ""
            if not settings.matches_keywords(title):
                continue

            jobs.append(JobOffer(
                title=title,
                company=item.get("companyName") or "",
                location=item.get("jobGeo") or "",
                url=url,
                source="jobicy",
                remote=True,
                posted_at=item.get("pubDate"),
            ))

    return jobs
