import json
from pathlib import Path
from urllib.parse import urlencode
from apify_client import ApifyClient
from .base import JobOffer
from settings import settings

ACTOR_ID = "curious_coder/linkedin-jobs-scraper"
RESULTS_PER_KEYWORD = 1000
CACHE_FILE = Path(__file__).parent.parent / "linkedin_cache.json"

# geoId=105646813 → Spain | f_PP=105088894 → Barcelona pinpoint (from LinkedIn URL)
# f_WT=2 → remote  |  f_TPR=r2592000 → last 30 days
def _build_urls() -> list[str]:
    urls = []
    for kw in settings.keywords:
        urls.append(
            "https://www.linkedin.com/jobs/search?"
            + urlencode({
                "keywords": kw,
                "location": "España",
                "geoId": "105646813",
                "f_PP": "105088894",
                "f_TPR": "r2592000",
            })
        )
        urls.append(
            "https://www.linkedin.com/jobs/search?"
            + urlencode({
                "keywords": kw,
                "f_WT": "2",
                "f_TPR": "r2592000",
            })
        )
    return urls


def _fetch_from_apify() -> list[dict]:
    token = settings.apify_token
    if not token:
        raise RuntimeError("APIFY_TOKEN not set in .env")

    client = ApifyClient(token)
    run = client.actor(ACTOR_ID).call(run_input={
        "urls": _build_urls(),
        "count": RESULTS_PER_KEYWORD,
    })
    items = list(client.dataset(run.default_dataset_id).iterate_items())
    CACHE_FILE.write_text(json.dumps(items, default=str), encoding="utf-8")
    return items


def _to_job_offers(items: list[dict]) -> list[JobOffer]:
    jobs = []
    seen_urls = set()
    for item in items:
        url = item.get("link") or item.get("jobUrl") or item.get("url") or ""
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = item.get("title") or ""
        company = item.get("companyName") or ""
        location = item.get("location") or ""
        posted_at = item.get("postedAt") or None
        workplace = item.get("workplaceTypes") or []
        input_url = item.get("inputUrl") or ""
        remote = (
            bool(item.get("workRemoteAllowed"))
            or "Remote" in workplace
            or "remote" in location.lower()
            or ("f_WT=2" in input_url and "On-site" not in workplace)
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


def scrape() -> list[JobOffer]:
    if CACHE_FILE.exists():
        items = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    else:
        items = _fetch_from_apify()
    return _to_job_offers(items)
