# Problems Faced — Errors, Solutions & Direction

This file summarizes **what went wrong**, **what showed up in logs or the UI**, **how it was fixed**, and **what you were pushing for** at each stage. It is aligned with the real build documented in `DEVELOPMENT_JOURNEY.md` and `DESIGN_NOTES_INTERNAL.md`.

---

## How to read “your ideas / direction”

Chat transcripts are not stored in the repo, so “your ideas” here means **the goals and pain points implied by each problem**: what you would have been trying to do when that failure appeared (e.g. run in Docker, get rows in Sheets, parse “cafe in Berlin”). If you want a version with exact quotes from a specific chat, you can paste those into a new section at the bottom.

---

## 1. Python package layout

| Difficulty | Python did not treat folders as importable packages. |
| Error | `ModuleNotFoundError: No module named 'app'` |
| Cause | Missing `__init__.py` in package directories. |
| Solution | Added `__init__.py` under `app/`, `app/agent/`, `app/tools/`, `app/services/`, `app/memory/`, `app/llm/`. |
| Your direction | Get the project runnable as a proper package so imports resolve no matter how you start the app. |

---

## 2. Import paths (relative vs absolute)

| Difficulty | Mixed or wrong import roots (`services`, `agent` without `app.`). |
| Error | `ModuleNotFoundError: No module named 'services'`, `ImportError: cannot import name 'run_agent' from 'agent.agent'` |
| Cause | Imports depended on the current working directory. |
| Solution | Standardized on absolute imports: `from app.services...`, `from app.agent.agent import run_agent`. |
| Your direction | One reliable way to run the app (CLI, IDE, Docker) without import roulette. |

---

## 3. Sheets API: wrong function name and save strategy

| Difficulty | Agent expected a `save()` API that did not exist. |
| Error | `ImportError: cannot import name 'save' from 'app.services.sheets'` |
| Cause | Implementation exposed `append_row()`, not `save()`. |
| Solution | Import and call `append_row(row)`; save **per lead** instead of batch-at-end. |
| Your direction | Actually persist leads; avoid losing everything if the run crashes mid-way. |

---

## 4. Docker: UI could not reach the API

| Difficulty | Streamlit and FastAPI run in different containers; `localhost` is wrong across containers. |
| Error / symptom | “Failed to contact the backend API”, connection refused. |
| Cause | UI used `http://localhost:8000` from inside the UI container. |
| Solution | Set `BACKEND_URL=http://api:8000` in Compose and `depends_on` the API service. |
| Your direction | Full stack in Docker with the UI talking to the backend reliably. |

---

## 5. Docker / network: external OSM APIs

| Difficulty | Container sometimes could not reach the public internet. |
| Error | `ConnectionError` / `Network is unreachable` to `nominatim.openstreetmap.org` (and similar). |
| Cause | Host VPN, firewall, or Docker network setup blocking outbound traffic. |
| Solution | Diagnose with `docker-compose exec` + `ping`/`curl`; run locally or fix host/network; not a code-only fix. |
| Your direction | Same features in Docker as on the laptop when the network allows it. |

---

## 6. Nominatim → Overpass

| Difficulty | Nominatim was a poor fit for bulk, structured POI extraction. |
| Issues | Strict rate limits (~1 req/s), weak control over bulk queries, pagination awkward for the use case. |
| Solution | Move to Overpass QL (`overpass.py`), keep `nominatim.py` as a thin shim where needed; update agent imports and docs. |
| Your direction | Pull **many** OSM features with richer tags and more control than geocoding search. |

---

## 7. Overpass: pagination and global queries

### 7a. No SQL-style offset

| Difficulty | Assumed Overpass supported `offset` like SQL. |
| Error / symptom | Invalid query or empty/broken results. |
| Solution | Drop offset; one query with a higher limit (e.g. 200); filter in Python if needed. |
| Your direction | Stable results without fighting the Overpass language. |

### 7b. “Everything on Earth” queries

| Difficulty | e.g. all `amenity=cafe` with no area → timeout or zero usable elements. |
| Symptom | `Overpass returned 0 results` or timeouts. |
| Solution | Area-based QL: resolve city/region, then `node[...](area.searchArea)`. |
| Your direction | Queries like **“cafes in Berlin”** should return real local businesses. |

### 7c. Parsing “X in Y”

| Difficulty | Raw string sent to Overpass as if it were a single name. |
| Symptom | No matches for natural language like `cafe in berlin`. |
| Solution | `_parse_query()`: split on ` in `, map amenity words via `AMENITY_MAP`, build area + tag query. |
| Your direction | Natural search phrases, not raw Overpass QL from the user. |

---

## 8. Google Sheets: nothing appeared

| Difficulty | Run “succeeded” but `leads_written` stayed 0 or sheet empty. |
| Causes | Over-strict validation, silent failures, credentials, or sheet sharing with the service account. |
| Solution | Logging in `append_row`, try/except with visible errors, per-lead handling in the agent. |
| Your direction | **Visible** failures and rows in the sheet when the pipeline runs. |

---

## 9. `credentials.json` path

| Difficulty | File in repo root but runtime CWD differed (or Docker layout differed). |
| Error | `FileNotFoundError: credentials.json not found at /app/credentials.json` |
| Solution | Resolve path relative to the module / project, with fallback to CWD. |
| Your direction | Works from project root, IDE, and Docker volume mounts. |

---

## 10. Validation: skipping almost all leads

| Difficulty | Required email/phone/address; OSM rarely has all of them. |
| Symptom | Almost every lead skipped; sheet still empty. |
| Solution | Require **name** only; allow empty strings for optional fields. |
| Your direction | Capture real-world OSM leads, not only “perfect” records. |

---

## 11. Email extraction from websites

| Difficulty | Regex did not match real addresses. |
| Symptom | No errors, just no emails. |
| Solution | Replace broken pattern with a standard email regex in `app/tools/email.py`. |
| Direction (design) | If the model/OSM gives a **website** but no email, scrape the site after LLM normalization (`DESIGN_NOTES_INTERNAL.md`). |

---

## 12. Progress and UX

| Difficulty | Background `/run` gave no feedback. |
| Symptom | No idea if the agent was stuck, done, or failing. |
| Solution | Global `AGENT_STATS`, `GET /stats`, UI polling + progress display. |
| Your direction | See status, counts, and something like a progress bar during a run. |

### Known limitation

| Difficulty | Stats live in memory only. |
| Symptom | After API restart, stats reset. |
| Mitigation / future | DB, Redis, or file; sheet remains source of truth for leads. |
| Your direction | “Good enough” visibility for a single run without new infrastructure yet. |

---

## Quick reference — errors → fixes

| Error or symptom | Typical fix |
|------------------|-------------|
| `No module named 'app'` | Add `__init__.py`; use `from app....` imports. |
| `cannot import name 'save'` | Use `append_row` from `app.services.sheets`. |
| UI cannot reach API in Docker | `BACKEND_URL=http://api:8000` in Compose. |
| Overpass empty / timeout on broad query | Area filter + parsed “X in Y”. |
| 0 leads written | Relax validation; add logging; check Sheets + service account share. |
| `credentials.json` not found | Robust path resolution + correct mount in Docker. |
| No emails from scrape | Fix regex; ensure scrape runs when website exists. |

---

## Related docs

- `DEVELOPMENT_JOURNEY.md` — full step-by-step narrative and code snippets.  
- `DESIGN_NOTES_INTERNAL.md` — why Overpass, email scraping, stats, and UI wiring were chosen.  

---

*Last updated to match the state of the repository documentation.*
