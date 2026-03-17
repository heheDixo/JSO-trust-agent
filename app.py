from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.mock_data import agencies
from core.agent import run_trust_agent

app = FastAPI()

class AnalyzeRequest(BaseModel):
    agency_id: str

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html") as f:
        return f.read()

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    agency = next((a for a in agencies if a["id"] == request.agency_id), None)
    if not agency:
        return {"error": "Agency not found"}
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, run_trust_agent, agency)
    return result