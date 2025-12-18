#3 overpass logic 
## removed pagination code 

import os
import requests
import time
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "OSMAgenticAI/1.0"),
}

OVERPASS_URL = os.getenv(
    "OVERPASS_URL",
    "https://overpass-api.de/api/interpreter",
)

def _build_overpass_query(query: str, limit: int) -> str:
    safe = query.replace('"', r'\"')
    return f"""
    [out:json][timeout:60];
    (
      node["name"~"{safe}", i];
      way["name"~"{safe}", i];
      relation["name"~"{safe}", i];
    );
    out center {limit};
    """

def search(query: str, limit: int = 50, retries: int = 3):
    payload = {"data": _build_overpass_query(query, limit)}
    for attempt in range(retries):
        try:
            resp = requests.post(OVERPASS_URL, data=payload, headers=HEADERS, timeout=90)
            resp.raise_for_status()
            return resp.json().get("elements", [])
        except RequestException as e:
            print(f"Overpass attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise e
    return []
