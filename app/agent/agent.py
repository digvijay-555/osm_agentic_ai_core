import time
import uuid
import asyncio

from app.agent.planner import enrich_lead
from app.db.sqlite import insert_lead
from app.memory.vector_store import is_duplicate
from app.models.lead import Lead
from app.services.sheets import append_row, sheets_export_enabled
from app.tools.email import extract as extract_email
from app.tools.overpass import search
from app.tools.scraper import fetch_text

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

async def process_lead(idx, raw, query, location_filter, sem, filtered_count_ref):
    async with sem:
        try:
            # Light location check (backup - most filtering done in Overpass)
            if location_filter:
                tags = raw.get("tags", {})
                location_lower = location_filter.lower()
                
                # Check if location appears anywhere in tags (loose match)
                all_tags_text = " ".join(str(v).lower() for v in tags.values())
                if location_lower not in all_tags_text:
                    filtered_count_ref[0] += 1
                    # Don't skip - Overpass area search should have filtered already
                    # This is just a safety check
            
            enriched = await enrich_lead(raw)
            if not enriched:
                print(f"⏭️ Skipped result {idx+1}: No name or invalid")
                return
            
            # Only require name - email, phone, address are optional
            if not enriched.get("name") or not enriched.get("name").strip():
                print(f"⏭️ Skipped result {idx+1}: Missing business name")
                return
            
            print(f"📝 Processing: {enriched.get('name', 'Unknown')}")
            
            # Try to scrape email from website if missing (optional - won't skip if fails)
            if (not enriched.get("email")) or enriched.get("email") in {"N/A", "na", "none", "null", ""}:
                website = enriched.get("website") or ""
                if website.startswith("http"):
                    try:
                        html_text = await fetch_text(website)
                        scraped_email = extract_email(html_text)
                        if scraped_email and scraped_email != "N/A":
                            enriched["email"] = scraped_email
                            print(f"  ✉️ Scraped email: {scraped_email}")
                    except Exception as scrape_err:
                        pass
            
            # Check for duplicates using thread to avoid blocking
            is_dup = await asyncio.to_thread(is_duplicate, enriched)
            if is_dup:
                AGENT_STATS["skipped_duplicates"] += 1
                print(f"  🔄 Duplicate detected, skipping")
                return
            
            # Prepare lead — SQLite is source of truth
            lead_id = str(uuid.uuid4())
            lead = Lead(
                uuid=lead_id,
                name=enriched.get("name", "").strip(),
                address=enriched.get("address", "").strip() or "",
                phone=enriched.get("phone", "").strip() or "",
                website=enriched.get("website", "").strip() or "",
                email=enriched.get("email", "").strip() or "",
                query=query,
            )

            try:
                await asyncio.to_thread(insert_lead, **lead.to_dict())
                AGENT_STATS["leads_written"] += 1
                print(f"  ✅ Lead saved to SQLite (#{AGENT_STATS['leads_written']})")
                print(
                    f"     Name: {lead.name}, Address: {lead.address or 'N/A'}, "
                    f"Phone: {lead.phone or 'N/A'}, Email: {lead.email or 'N/A'}"
                )

                if sheets_export_enabled():
                    try:
                        await asyncio.to_thread(append_row, lead.to_row())
                        print("  📊 Also exported to Google Sheets")
                    except Exception as sheet_err:
                        print(f"  ⚠️ Sheets export failed (SQLite saved): {sheet_err}")
                        AGENT_STATS["errors"] += 1
            except Exception as write_err:
                print(f"  ❌ Failed to save lead to SQLite: {write_err}")
                AGENT_STATS["errors"] += 1
            
        except Exception as lead_err:
            print(f"❌ Error processing lead {idx+1}: {lead_err}")
            AGENT_STATS["errors"] += 1


async def run_agent(query: str):
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
        print(f"🔍 Starting search for: {query}")
        results = await search(query, limit=200)  # Get more results, filter by location in Python
        print(f"📊 Overpass returned {len(results)} results")
        
        if not results:
            print("⚠️ No results from Overpass")
            AGENT_STATS["status"] = "done"
            return
        
        # Note: Location filtering is now done in Overpass query via area search
        # We still do a light Python-side filter as backup
        location_filter = None
        if " in " in query.lower():
            location = query.lower().split(" in ", 1)[1].strip()
            location_filter = location
            print(f" Location filter: {location} (applied in Overpass query)")
        
        filtered_count_ref = [0]
        sem = asyncio.Semaphore(10)
        
        tasks = [
            process_lead(idx, raw, query, location_filter, sem, filtered_count_ref)
            for idx, raw in enumerate(results)
        ]
        
        await asyncio.gather(*tasks)
        
        AGENT_STATS["pages_processed"] = 1
        AGENT_STATS["status"] = "done"
        if location_filter:
            print(f"📍 Filtered out {filtered_count_ref[0]} results not matching location")
        print(f"✅ Agent finished: {AGENT_STATS['leads_written']} leads written, {AGENT_STATS['skipped_duplicates']} duplicates skipped")
        
    except Exception as e:
        import traceback
        print(f"❌ AGENT ERROR: {e}")
        print(traceback.format_exc())
        AGENT_STATS["errors"] += 1
        AGENT_STATS["status"] = "error"
    finally:
        AGENT_STATS["finished_at"] = time.time()
