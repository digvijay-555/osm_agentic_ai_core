from fastapi import BackgroundTasks, FastAPI

from app.agent.agent import run_agent
from app.services.sheets import read_all


app = FastAPI()


@app.post("/run")
async def run(query: str, bg: BackgroundTasks):
    bg.add_task(run_agent, query)
    return {"status": "Agent started"}


@app.get("/leads")
async def get_leads():
    """
    Return all leads currently stored in Google Sheets.
    Each record is a dict with keys matching the sheet headers.
    """
    return read_all()

