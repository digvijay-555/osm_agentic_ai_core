# Web scraping tool

import httpx
from bs4 import BeautifulSoup

async def fetch_text(url):
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, "lxml")
            return soup.get_text()
    except Exception:
        return ""
