from app.tools.nominatim import search
from app.agent.planner import enrich_lead
from app.memory.vector_store import is_duplicate
from app.services.sheets import append_row
import uuid

def run_agent(query: str):
    offset = 0

    while True:
        results = search(query, limit=10, offset=offset)
        if not results:
            break

        for raw in results:
            enriched = enrich_lead(raw)
            if not enriched:
                continue

            if is_duplicate(enriched):
                continue

            row = [
                str(uuid.uuid4()),                 # UUID  -> column A
                enriched.get("name", ""),          # Name  -> column B
                enriched.get("address", ""),       # Addr  -> column C
                enriched.get("phone", ""),         # Phone -> column D
                enriched.get("website", ""),       # Web   -> column E
                enriched.get("email", ""),         # Email -> column F
            ]

            append_row(row)

        offset += 10
