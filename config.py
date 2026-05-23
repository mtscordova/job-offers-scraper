KEYWORDS = ["data engineer", "data architect"]

GREENHOUSE_COMPANIES = [
    # Remote-friendly / global
    "airbnb",
    "stripe",
    "twilio",
    "dbtlabs",
    "fivetran",
    "hashicorp",
    "gitlab",
    "elastic",
    "grafana",
    "mattermost",
    # EU-based or EU-hiring
    "typeform",
    "king",
    "glovo",
    "cabify",
    "factorial",
    "travelperk",
    "holaluz",
    "flywire",
    "paack",
    "clarity-ai",
    # US but remote-global
    "zendesk",
    "hubspot",
    "brex",
    "plaid",
    "rippling",
    "notion",
]

LEVER_COMPANIES = [
    "coursera",
    "duolingo",
    "asana",
    "amplitude",
    "mixpanel",
    "reddit",
    "airtable",
    "remote",
    "hotjar",
    "workable",
    "personio",
]

SPAIN_TERMS = [
    "barcelona", "bcn",
    "remote", "worldwide", "anywhere",
]


def matches_keywords(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in KEYWORDS)


def is_spain_or_remote(location: str, remote: bool) -> bool:
    if remote:
        return True
    loc_lower = location.lower()
    if not loc_lower:
        return True  # sin ubicación, no descartamos
    return any(term in loc_lower for term in SPAIN_TERMS)


MAX_AGE_DAYS = 21  # descartar ofertas con posted_at más antiguo que esto

REQUEST_DELAY = 1.0  # seconds between requests
REQUEST_TIMEOUT = 15
MAX_PAGES = 5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
