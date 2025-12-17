# Nominatim geocoding tool

import requests
import os
from dotenv import load_dotenv

load_dotenv()

HEADERS = {"User-Agent": os.getenv("USER_AGENT")}

def search(query, limit=10, offset=0):
    return requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": query,
            "format": "json",
            "limit": limit,
            "offset": offset,
            "addressdetails": 1,
            "extratags": 1
        },
        headers=HEADERS
    ).json()
