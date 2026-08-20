# Overpass logic - smart query parsing for "X in Y" patterns

import os
import httpx
import time
import asyncio
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "OSMAgenticAI/1.0"),
}

OVERPASS_URL = os.getenv(
    "OVERPASS_URL",
    "https://overpass-api.de/api/interpreter",
)

# Common amenity mappings for better search
AMENITY_MAP = {
    "cafe": "cafe",
    "coffee": "cafe",
    "restaurant": "restaurant",
    "dentist": "dentist",
    "dentists": "dentist",
    "clinic": "clinic",
    "hospital": "hospital",
    "pharmacy": "pharmacy",
    "shop": "shop",
    "store": "shop",
    "hotel": "hotel",
    "bank": "bank",
    "atm": "atm",
    "bar": "bar",
    "pub": "pub",
    "gym": "gym",
    "fitness": "gym",
    "school": "school",
    "university": "university",
    "gas": "fuel",
    "petrol": "fuel",
    "parking": "parking",
}

def _parse_query(query: str):
    """Parse query to extract amenity type and location."""
    query_lower = query.lower().strip()
    
    # Try "X in Y" pattern
    if " in " in query_lower:
        parts = query_lower.split(" in ", 1)
        amenity_part = parts[0].strip()
        location = parts[1].strip()
        
        # Map common terms to OSM amenity values
        amenity = None
        for key, value in AMENITY_MAP.items():
            if key in amenity_part:
                amenity = value
                break
        
        return {"type": "amenity_area", "amenity": amenity, "location": location, "original": query}
    
    # Try "X near Y" pattern
    if " near " in query_lower:
        parts = query_lower.split(" near ", 1)
        amenity_part = parts[0].strip()
        location = parts[1].strip()
        
        amenity = None
        for key, value in AMENITY_MAP.items():
            if key in amenity_part:
                amenity = value
                break
        
        return {"type": "amenity_area", "amenity": amenity, "location": location, "original": query}
    
    # Fallback: treat as name search
    return {"type": "name_search", "query": query}

def _build_overpass_query(query: str, limit: int) -> str:
    """Build Overpass QL query based on parsed query structure."""
    parsed = _parse_query(query)
    
    if parsed["type"] == "amenity_area" and parsed.get("amenity"):
        # Use area-based search - find the area first, then search within it
        amenity = parsed["amenity"]
        location_safe = parsed["location"].replace('"', r'\"')
        
        return f"""
        [out:json][timeout:120];
        (
          // First, find the area (city/region) by name
          area["name"~"{location_safe}", i]["admin_level"~"[2-8]"]->.searchArea;
          
          // Then find amenities within that area
          (
            node["amenity"="{amenity}"](area.searchArea);
            way["amenity"="{amenity}"](area.searchArea);
          );
        );
        out center {limit};
        """
    
    # Fallback: name-based search (works for queries like "Starbucks" or "McDonald's")
    safe = query.replace('"', r'\"')
    return f"""
    [out:json][timeout:120];
    (
      node["name"~"{safe}", i];
      way["name"~"{safe}", i];
      relation["name"~"{safe}", i];
    );
    out center {limit};
    """

_query_cache = {}

async def search(query: str, limit: int = 50, retries: int = 3):
    """Search OSM via Overpass API with retry logic and caching."""
    if query in _query_cache:
        print(f"⚡ Returning cached results for query: {query}")
        return _query_cache[query]

    query_str = _build_overpass_query(query, limit)
    payload = {"data": query_str}
    
    # Debug: print the query (first 200 chars)
    print(f"🔍 Overpass query: {query_str[:200]}...")
    
    async with httpx.AsyncClient(timeout=130.0) as client:
        for attempt in range(retries):
            try:
                resp = await client.post(OVERPASS_URL, data=payload, headers=HEADERS)
                resp.raise_for_status()
                data = resp.json()
                elements = data.get("elements", [])
                
                # Check for Overpass errors in response
                if "remark" in data:
                    print(f"⚠️ Overpass remark: {data['remark']}")
                
                _query_cache[query] = elements
                return elements
            except httpx.HTTPError as e:
                print(f"❌ Overpass attempt {attempt+1} failed: {e}")
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                        wait_time = 15 * (attempt + 1)  # Longer backoff for rate limits
                        print(f"🐢 Rate limited (429)! Retrying in {wait_time} seconds...")
                    else:
                        print(f"⏳ Retrying in {wait_time} seconds...")
                    
                    await asyncio.sleep(wait_time)
                    continue
                
                # On final failure, try a simpler query as fallback
                print("⚠️ Trying fallback name-based search...")
                fallback_results = await _fallback_search(query, limit)
                if fallback_results:
                    _query_cache[query] = fallback_results
                return fallback_results
    return []

async def _fallback_search(query: str, limit: int) -> list:
    """Fallback to simple name-based search if area search fails."""
    safe = query.replace('"', r'\"')
    fallback_query = f"""
    [out:json][timeout:30];
    (
      node["name"~"{safe}", i];
      way["name"~"{safe}", i];
    );
    out center {limit};
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(OVERPASS_URL, data={"data": fallback_query}, headers=HEADERS)
            resp.raise_for_status()
            return resp.json().get("elements", [])
    except Exception as e:
        print(f"❌ Fallback search also failed: {e}")
        return []
