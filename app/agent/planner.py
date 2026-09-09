# Planning logic


import json
from typing import Dict, Optional

from app.llm.ollama_client import call_llm
from app.agent.prompt import SYSTEM_PROMPT

async def enrich_lead(raw: Dict) -> Optional[Dict]:
    tags = raw.get("tags", {})
    
    raw_lat = raw.get("lat") or raw.get("center", {}).get("lat")
    raw_lon = raw.get("lon") or raw.get("center", {}).get("lon")
    try:
        lat = float(raw_lat) if raw_lat is not None else None
    except (ValueError, TypeError):
        lat = None
    try:
        lon = float(raw_lon) if raw_lon is not None else None
    except (ValueError, TypeError):
        lon = None

    base_lead = {
        "name": str(tags.get("name", "")).strip(),
        "address": " ".join(filter(None, [
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", ""),
            tags.get("addr:city", ""),
            tags.get("addr:postcode", "")
        ])).strip(),
        "phone": str(tags.get("phone", "") or tags.get("contact:phone", "")).strip(),
        "website": str(tags.get("website", "") or tags.get("contact:website", "")).strip(),
        "email": str(tags.get("email", "") or tags.get("contact:email", "")).strip(),
        "lat": lat,
        "lon": lon,
    }
    
    if not base_lead["name"]:
        return None
    
    # LLM enrichment (optional)
    prompt = SYSTEM_PROMPT + "\nRAW DATA:\n" + json.dumps(raw, indent=2)
    try:
        llm_response = await call_llm(prompt)
        if llm_response:
            cleaned_text = llm_response.strip()
            if cleaned_text.startswith("```"):
                lines = cleaned_text.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned_text = "\n".join(lines).strip()
            parsed = json.loads(cleaned_text)
            for key in ("name", "address", "phone", "website", "email"):
                value = parsed.get(key)
                if isinstance(value, str) and value.strip():
                    base_lead[key] = value.strip()
    except Exception as e:
        print("⚠️ LLM enrichment failed:", e)
    
    return base_lead

