# main_event_agent.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import json
from event_agent import EventIntelligenceAgent, EventAIAgentConfig, AgentMessage  # ton code agent
from fastapi.middleware.cors import CORSMiddleware

# =======================
# Configuration FastAPI
# =======================

app = FastAPI(title="Event Intelligence API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # ou le port de votre frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CITY = "New York"
HOURS_AHEAD = 12


config = EventAIAgentConfig(city=CITY, hours_ahead=HOURS_AHEAD)
agent = EventIntelligenceAgent(config)

# =======================
# Models
# =======================

class AnalyzeRequest(BaseModel):
    city: Optional[str] = CITY

# =======================
# Routes
# =======================

@app.get("/")
def root():
    return {"message": "Event Intelligence API is running."}

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    try:
        if request.city != CITY:
            raise HTTPException(status_code=400, detail=f"Only {CITY} is supported.")
        
        recommendation = agent.get_recommendation()
        formatted = AgentMessage.format_for_orchestrator(agent.agent_id, recommendation)
        return formatted
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/all_events")
def all_events():
    try:
        recommendation = agent.get_recommendation()
        formatted = AgentMessage.format_for_orchestrator(agent.agent_id, recommendation)
        return {
            "city": CITY,
            "timestamp": datetime.now().isoformat(),
            "events": formatted
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


