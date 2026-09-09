# Web scraping tool with SSRF protection and redirect support

import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


def is_safe_url(url: str) -> bool:
    """Validate that a URL uses safe scheme and does not point to internal/private networks."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False

        if hostname.lower() in ("localhost", "localhost.localdomain", "broadcasthost"):
            return False

        addr_info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            ):
                return False
        return True
    except Exception:
        return False


async def fetch_text(url: str) -> str:
    """Safely fetch and extract plain text from a URL."""
    if not is_safe_url(url):
        return ""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36 OSMAgenticAI/1.0"
        )
    }

    try:
        async with httpx.AsyncClient(
            timeout=8.0,
            follow_redirects=True,
            headers=headers,
        ) as client:
            response = await client.get(url)
            # Re-verify final redirect destination against SSRF
            if not is_safe_url(str(response.url)):
                return ""
            response.raise_for_status()

            # Prevent memory exhaustion on massive downloads (max 2 MB)
            if len(response.content) > 2 * 1024 * 1024:
                return ""

            soup = BeautifulSoup(response.text, "lxml")
            return soup.get_text()
    except Exception:
        return ""

