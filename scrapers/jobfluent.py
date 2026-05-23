import time
import requests
from bs4 import BeautifulSoup
from .base import JobOffer
from config import KEYWORDS, HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT, MAX_PAGES

BASE_URL = "https://www.jobfluent.com/jobs"


def scrape() -> list[JobOffer]:
    jobs = []
    seen_urls = set()
    session = requests.Session()
    session.headers.update(HEADERS)

    for keyword in KEYWORDS:
        for page in range(1, MAX_PAGES + 1):
            params = {"q": keyword}
            if page > 1:
                params["page"] = page

            resp = session.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                break

            soup = BeautifulSoup(resp.text, "lxml")
            rows = soup.select("table tr")
            if not rows:
                break

            found_any = False
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue

                link = cells[0].find("a", href=True)
                if not link:
                    continue

                url = link["href"]
                if not url.startswith("http"):
                    url = f"https://www.jobfluent.com{url}"

                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title = link.get_text(strip=True)
                company = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                location = cells[2].get_text(strip=True) if len(cells) > 2 else ""

                jobs.append(JobOffer(
                    title=title,
                    company=company,
                    location=location,
                    url=url,
                    source="jobfluent",
                ))
                found_any = True

            if not found_any:
                break

            time.sleep(REQUEST_DELAY)

    return jobs
