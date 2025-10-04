# main_orchestrator_agent.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import json
from datetime import datetime
from orchestrator import OrchestratorAgent, OrchestratorConfig  # Assure-toi que le chemin est correct

# =======================================================
# CONFIGURATION FASTAPI
# =======================================================
app = FastAPI(title="Orchestrator Intelligence Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================================================
# REQUÊTES
# =======================================================
class OrchestratorRequest(BaseModel):
    city: Optional[str] = "New York"

@app.get("/")
def root():
    return {"status": "Orchestrator Intelligence Agent is running"}

@app.post("/orchestrate")
def orchestrate(req: OrchestratorRequest):
    city = req.city or "New York"
    config = OrchestratorConfig(city=city)
    agent = OrchestratorAgent(config)
    
    try:
        recommendation = agent.get_orchestrated_recommendation()
        return recommendation
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}


