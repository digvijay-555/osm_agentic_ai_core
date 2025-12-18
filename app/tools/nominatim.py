"""
Backward-compat shim for code that still imports `app.tools.nominatim`.

The actual implementation now lives in `app.tools.overpass`.
"""

from app.tools.overpass import search  # noqa: F401


