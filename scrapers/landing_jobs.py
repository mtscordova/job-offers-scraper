import time
import requests
from .base import JobOffer
from settings import settings

API_URL = "https://landing.jobs/api/v1/jobs"
PAGE_SIZE = 20


def scrape() -> list[JobOffer]:
    jobs = []
    seen_urls = set()
    session = requests.Session()
    session.headers.update({**settings.headers, "Accept": "application/json"})

    for keyword in settings.keywords:
        for page in range(1, settings.max_pages + 1):
            resp = session.get(
                API_URL,
                params={"search": keyword, "page": page, "remote": "true"},
                timeout=settings.request_timeout,
            )
            if resp.status_code != 200:
                break

            data = resp.json()
            if not data:
                break

            for item in data:
                url = item.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                locations = item.get("locations") or []
                location = ", ".join(
                    f"{loc.get('city', '')} {loc.get('country_code', '')}".strip()
                    for loc in locations
                )
                company = (
                    item.get("company", {}).get("name", "")
                    if isinstance(item.get("company"), dict)
                    else str(item.get("company_id", ""))
                )

                jobs.append(JobOffer(
                    title=item.get("title", ""),
                    company=company,
                    location=location,
                    url=url,
                    source="landing_jobs",
                    remote=bool(item.get("remote", False)),
                    posted_at=item.get("published_at"),
                ))

            if len(data) < PAGE_SIZE:
                break
            time.sleep(settings.request_delay)

    return jobs
