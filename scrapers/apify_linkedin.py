import os
from urllib.parse import urlencode
from apify_client import ApifyClient
from .base import JobOffer
from config import KEYWORDS

ACTOR_ID = "curious_coder/linkedin-jobs-scraper"
RESULTS_PER_KEYWORD = 50

# LinkedIn URL params: past month + Barcelona, and past month + remote
def _build_urls() -> list[str]:
    urls = []
    for kw in KEYWORDS:
        # Barcelona presencial
        urls.append(
            "https://www.linkedin.com/jobs/search/?"
            + urlencode({
                "keywords": kw,
                "location": "Barcelona, Catalonia, Spain",
                "f_TPR": "r2592000",  # last 30 days
            })
        )
        # Remote worldwide
        urls.append(
            "https://www.linkedin.com/jobs/search/?"
            + urlencode({
                "keywords": kw,
                "f_WT": "2",          # remote
                "f_TPR": "r2592000",
            })
        )
    return urls


def scrape() -> list[JobOffer]:
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN env variable not set")

    client = ApifyClient(token)
    run = client.actor(ACTOR_ID).call(run_input={
        "urls": _build_urls(),
        "count": RESULTS_PER_KEYWORD,
    })

    jobs = []
    seen_urls = set()

    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        url = item.get("jobUrl") or item.get("link") or item.get("url") or ""
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = item.get("title") or item.get("jobTitle") or ""
        company = item.get("companyName") or item.get("company") or ""
        location = item.get("location") or item.get("jobLocation") or ""
        posted_at = item.get("postedAt") or item.get("publishedAt") or item.get("postingDate") or None
        remote = (
            item.get("workType", "").lower() == "remote"
            or "remote" in location.lower()
        )

        jobs.append(JobOffer(
            title=title,
            company=company,
            location=location,
            url=url,
            source="linkedin",
            remote=remote,
            posted_at=posted_at,
        ))

    return jobs
