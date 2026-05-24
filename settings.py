from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Secrets
    apify_token: str = ""

    # Search
    keywords: list[str] = ["data engineer", "data architect"]
    max_age_days: int = 21
    max_pages: int = 5

    # HTTP
    request_delay: float = 1.0
    request_timeout: int = 15
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # Location filter
    location_terms: list[str] = ["barcelona", "bcn", "spain", "españa", "remote", "worldwide", "anywhere"]

    # Company boards
    greenhouse_companies: list[str] = [
        # Original (verified working)
        "airbnb", "stripe", "twilio", "dbtlabs", "fivetran", "hashicorp",
        "gitlab", "elastic", "grafana", "mattermost",
        "typeform", "cabify", "holaluz", "flywire", "paack", "clarity-ai",
        "zendesk", "hubspot", "brex", "plaid", "rippling", "notion",
        # Data & infrastructure
        "databricks", "clickhouse", "amplitude", "contentful", "commercetools",
        # European / remote-friendly
        "n26", "amenitiz", "xapo61", "nearform", "remotecom",
        # US remote (high data eng volume)
        "discord", "dropbox", "gusto", "robinhood", "lyft",
        "lattice", "smarterdx",
    ]
    lever_companies: list[str] = [
        "coursera", "duolingo", "asana", "amplitude", "mixpanel",
        "reddit", "airtable", "remote", "hotjar", "workable", "personio",
    ]

    @computed_field
    @property
    def headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent}

    def matches_keywords(self, title: str) -> bool:
        t = title.lower()
        return any(kw in t for kw in self.keywords)

    def is_relevant_location(self, location: str, remote: bool) -> bool:
        if remote:
            return True
        loc = location.lower()
        if not loc:
            return True
        return any(term in loc for term in self.location_terms)


settings = Settings()
