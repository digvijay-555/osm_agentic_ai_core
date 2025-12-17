# Planning logic

import json
from app.llm.ollama_client import call_llm
from app.agent.prompt import SYSTEM_PROMPT

def enrich_lead(raw):
    prompt = SYSTEM_PROMPT + f"\nRAW DATA:\n{raw}"
    try:
        return json.loads(call_llm(prompt))
    except:
        return None
