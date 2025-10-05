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
    driver_id: Optional[str] = "E10156"
    wellbeing_score: Optional[float] = 85.0

@app.get("/")
def root():
    return {"status": "Orchestrator Intelligence Agent is running"}

@app.post("/orchestrate")
def orchestrate(req: OrchestratorRequest):
    city = req.city or "New York"
    driver_id = req.driver_id or "E10156"
    wellbeing_score = req.wellbeing_score if req.wellbeing_score is not None else 85.0
    
    config = OrchestratorConfig(city=city)
    agent = OrchestratorAgent(config)
    
    try:
        recommendation = agent.get_orchestrated_recommendation(
            driver_id=driver_id,
            wellbeing_score=wellbeing_score
        )
        return recommendation
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}


