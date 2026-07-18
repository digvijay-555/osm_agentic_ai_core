from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Lead:
    uuid: str
    name: str
    address: str = ""
    phone: str = ""
    website: str = ""
    email: str = ""
    query: str = ""
    created_at: Optional[str] = field(default=None)

    def to_row(self) -> list:
        """Row format for optional Google Sheets export."""
        return [
            self.uuid,
            self.name,
            self.address,
            self.phone,
            self.website,
            self.email,
        ]

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "email": self.email,
            "query": self.query,
            "created_at": self.created_at,
        }
