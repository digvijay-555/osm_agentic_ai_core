from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def _sanitize_sheet_cell(value: Any) -> Any:
    """
    Prevent Spreadsheet Formula Injection (CSV injection).
    If a string starts with '=', '+', '-', '@', '\t', or '\r', prefix with a single quote.
    """
    if isinstance(value, str):
        val = value.strip()
        if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
            return f"'{val}"
        return val
    return value


@dataclass
class Lead:
    uuid: str
    name: str
    address: str = ""
    phone: str = ""
    website: str = ""
    email: str = ""
    lat: Optional[float] = None
    lon: Optional[float] = None
    query: str = ""
    created_at: Optional[str] = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_row(self) -> list:
        """Row format for Google Sheets export with formula injection sanitization."""
        return [
            _sanitize_sheet_cell(self.uuid),
            _sanitize_sheet_cell(self.name),
            _sanitize_sheet_cell(self.address),
            _sanitize_sheet_cell(self.phone),
            _sanitize_sheet_cell(self.website),
            _sanitize_sheet_cell(self.email),
            self.lat if self.lat is not None else "",
            self.lon if self.lon is not None else "",
            _sanitize_sheet_cell(self.query),
            _sanitize_sheet_cell(self.created_at or ""),
        ]

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "email": self.email,
            "lat": self.lat,
            "lon": self.lon,
            "query": self.query,
            "created_at": self.created_at,
        }

