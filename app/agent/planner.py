# Planning logic


import json
from typing import Dict, Optional

from app.llm.ollama_client import call_llm
from app.agent.prompt import SYSTEM_PROMPT

def enrich_lead(raw: Dict) -> Optional[Dict]:
    tags = raw.get("tags", {})
    
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
    }
    
    if not base_lead["name"]:
        return None
    
    # LLM enrichment (optional)
    prompt = SYSTEM_PROMPT + "\nRAW DATA:\n" + json.dumps(raw, indent=2)
    try:
        llm_response = call_llm(prompt)
        if llm_response:
            parsed = json.loads(llm_response)
            for key in base_lead:
                value = parsed.get(key)
                if isinstance(value, str) and value.strip():
                    base_lead[key] = value.strip()
    except Exception as e:
        print("⚠️ LLM enrichment failed:", e)
    
    return base_lead
