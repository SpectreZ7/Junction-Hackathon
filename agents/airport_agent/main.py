from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime
from airport_agent import config, agent, AgentMessage
from fastapi.middleware.cors import CORSMiddleware

# Ton code existant ici (ou import depuis un module)

app = FastAPI(title="Airport Intelligence API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # ou le port de votre frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class AirportRequest(BaseModel):
    airport_code: str

@app.get("/")
def root():
    return {"message": "Airport Intelligence API is running!"}

@app.post("/analyze")
def analyze_airport(request: AirportRequest):
    airport_code = request.airport_code.upper()
    
    if airport_code not in config.airports:
        raise HTTPException(status_code=404, detail=f"Airport {airport_code} not found in {config.city}")
    
    try:
        recommendation = agent.get_recommendation(airport_code)
        formatted_msg = AgentMessage.format_for_orchestrator(agent.agent_id, recommendation)
        return formatted_msg
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/all_airports")
def analyze_all_airports():
    all_recommendations = {}
    
    for airport_code in config.airports.keys():
        recommendation = agent.get_recommendation(airport_code)
        all_recommendations[airport_code] = AgentMessage.format_for_orchestrator(
            agent_id=f"airport_agent_{airport_code.lower()}",
            recommendation=recommendation
        )
    
    return {
        "city": config.city,
        "timestamp": datetime.now().isoformat(),
        "airports": all_recommendations
    }
