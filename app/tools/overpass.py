import os

import requests
from dotenv import load_dotenv

# Overpass-based place search for OSM data.
# We keep the same public `search()` signature that the rest of the app expects,
# but internally call the Overpass API.

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "OSMAgenticAI/1.0"),
}

OVERPASS_URL = os.getenv(
    "OVERPASS_URL",
    "https://overpass-api.de/api/interpreter",
)


def _build_overpass_query(query: str, limit: int, offset: int) -> str:
    """
    Build an Overpass QL query that searches for any OSM object whose `name`
    roughly matches the free-text query.

    We search nodes, ways and relations, and request their center coordinates.
    """
    safe = query.replace('"', r"\"")
    return f"""
    [out:json][timeout:25];
    (
      node["name"~"{safe}", i];
      way["name"~"{safe}", i];
      relation["name"~"{safe}", i];
    );
    out center {limit} {offset};
    """


def search(query: str, limit: int = 10, offset: int = 0):
    """Search OSM via Overpass and return the raw `elements` list."""
    payload = {"data": _build_overpass_query(query, limit, offset)}
    resp = requests.post(OVERPASS_URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("elements", [])


