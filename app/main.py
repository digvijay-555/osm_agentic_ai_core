# Main application entry point
from fastapi import FastAPI, BackgroundTasks
from app.agent.agent import run_agent

app = FastAPI()

@app.post("/run")
async def run(query: str, bg: BackgroundTasks):
    bg.add_task(run_agent, query)
    return {"status": "Agent started"}

