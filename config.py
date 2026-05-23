KEYWORDS = ["data engineer", "data architect"]

GREENHOUSE_COMPANIES = [
    "airbnb",
    "stripe",
    "twilio",
    "dbtlabs",
    "fivetran",
    "hashicorp",
    "zendesk",
    "hubspot",
    "intercom",
    "squarespace",
    "brex",
    "gusto",
    "plaid",
    "rippling",
    "lattice",
    "benchling",
    "figma",
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
]

SPAIN_TERMS = [
    "spain", "españa", "madrid", "barcelona", "valencia",
    "bilbao", "sevilla", "malaga", "málaga", "zaragoza",
    "alicante", "granada", "murcia", "palma", "remote",
    "worldwide", "anywhere",
]


def is_spain_or_remote(location: str, remote: bool) -> bool:
    if remote:
        return True
    loc_lower = location.lower()
    if not loc_lower:
        return True  # sin ubicación, no descartamos
    return any(term in loc_lower for term in SPAIN_TERMS)


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
