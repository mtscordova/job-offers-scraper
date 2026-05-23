from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobOffer:
    title: str
    company: str
    location: str
    url: str
    source: str
    remote: bool = False
    description: Optional[str] = None
    posted_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "source": self.source,
            "remote": int(self.remote),
            "description": self.description,
            "posted_at": self.posted_at,
        }
