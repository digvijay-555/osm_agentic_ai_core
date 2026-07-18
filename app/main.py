from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI

from app.agent.agent import AGENT_STATS, run_agent
from app.db.sqlite import count_leads, get_all_leads, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/run")
async def run(query: str, bg: BackgroundTasks):
    bg.add_task(run_agent, query)
    return {"status": "Agent started"}


@app.get("/leads")
async def get_leads():
    """
    Return all leads stored in SQLite (source of truth).
    """
    return get_all_leads()


@app.get("/leads/count")
async def get_leads_count():
    return {"count": count_leads()}


@app.get("/stats")
async def get_stats():
    """Return in-memory agent statistics for progress tracking."""
    return AGENT_STATS

