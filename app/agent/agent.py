
from app.tools.overpass import search
from app.agent.planner import enrich_lead
from app.memory.vector_store import is_duplicate
from app.services.sheets import append_row
from app.tools.scraper import fetch_text
from app.tools.email import extract as extract_email
import time
import uuid

AGENT_STATS = {
    "status": "idle",
    "last_query": None,
    "started_at": None,
    "finished_at": None,
    "pages_processed": 0,
    "leads_written": 0,
    "skipped_duplicates": 0,
    "errors": 0,
}

def run_agent(query: str):
    global AGENT_STATS
    AGENT_STATS.update({
        "status": "running",
        "last_query": query,
        "started_at": time.time(),
        "finished_at": None,
        "pages_processed": 0,
        "leads_written": 0,
        "skipped_duplicates": 0,
        "errors": 0,
    })

    try:
        results = search(query, limit=50)
        for raw in results:
            enriched = enrich_lead(raw)
            if not enriched:
                continue
            if (not enriched.get("email")) or enriched.get("email") in {"N/A", "na", "none", "null", ""}:
                website = enriched.get("website") or ""
                if website.startswith("http"):
                    html_text = fetch_text(website)
                    scraped_email = extract_email(html_text)
                    if scraped_email and scraped_email != "N/A":
                        enriched["email"] = scraped_email
            if is_duplicate(enriched):
                AGENT_STATS["skipped_duplicates"] += 1
                continue
            row = [
                str(uuid.uuid4()),
                enriched.get("name", ""),
                enriched.get("address", ""),
                enriched.get("phone", ""),
                enriched.get("website", ""),
                enriched.get("email", ""),
            ]
            append_row(row)
            AGENT_STATS["leads_written"] += 1
        AGENT_STATS["pages_processed"] = 1
        AGENT_STATS["status"] = "done"
    except Exception as e:
        print("AGENT ERROR:", e)
        AGENT_STATS["errors"] += 1
        AGENT_STATS["status"] = "error"
    finally:
        AGENT_STATS["finished_at"] = time.time()
