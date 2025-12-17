# Web scraping tool

import requests
from bs4 import BeautifulSoup

def fetch_text(url):
    try:
        soup = BeautifulSoup(requests.get(url, timeout=8).text, "lxml")
        return soup.get_text()
    except:
        return ""
