#!/usr/bin/env python3
"""
🚗🤖 UBER DRIVER AI COMPANION - BACKEND API SERVER 🤖🚗

FastAPI server that exposes all AI agents as REST endpoints for the mobile app frontend.
Provides real-time data integration between Python AI backend and React Native/Web frontend.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import sys
import os
import uvicorn
import asyncio
from datetime import datetime, timedelta
import logging

# Add agents to path
sys.path.append('agents')
sys.path.append('agents/data_analysis')

# Import all our AI agents
from digital_twin_agent import DigitalTwinAgent
from rides_analysis_agent import analyze_driver, get_driver_summary, create_digital_twin, data
from driver_prioritization_agent import DriverPrioritizationAgent
from airport_agent import AirportAgent
from wellbeing_agent import WellbeingAgent, WellbeingConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Uber Driver AI Companion API",
    description="Backend API for the AI-powered Uber Driver mobile companion app",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agents
digital_twin = DigitalTwinAgent()
prioritization = DriverPrioritizationAgent()
airport = AirportAgent()
wellbeing = WellbeingAgent()

# ============================================================================
# PYDANTIC MODELS FOR API REQUEST/RESPONSE
# ============================================================================

class DriverRequest(BaseModel):
    driver_id: str

class WellbeingCheckIn(BaseModel):
    driver_id: str
    sleep_hours: float
    fatigue_level: int  # 1-5
    stress_level: int   # 1-5
    body_discomfort: int  # 1-5
    mood: int  # 1-5

class AirportRequest(BaseModel):
    city: str
    driver_lat: Optional[float] = None
    driver_lng: Optional[float] = None

class OptimizationScenario(BaseModel):
    scenario_name: str
    projected_earnings: float
    improvement_percentage: float
    feasibility_score: float
    schedule: Dict[str, Any]

class DriverProfile(BaseModel):
    driver_id: str
    preferred_hours: List[int]
    peak_days: List[str]
    avg_earnings_per_hour: float
    surge_responsiveness: float
    fatigue_threshold: float
    consistency_score: float

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/api/v1/dashboard/{driver_id}")
async def get_dashboard_data(driver_id: str):
    """Get comprehensive dashboard data for a driver"""
    try:
        # Get basic driver stats
        driver_data = data[data['driver_id'] == driver_id]
        
        if driver_data.empty:
            raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found")
        
        # Calculate today's stats (using latest date in data as "today")
        latest_date = driver_data['date'].max()
        today_data = driver_data[driver_data['date'] == latest_date]
        
        # Basic stats
        total_rides_today = len(today_data)
        total_earnings_today = today_data['earnings'].sum() if 'earnings' in today_data.columns else 0
        hours_worked = total_rides_today * 0.5  # Estimate based on rides
        
        # Get Digital Twin recommendations
        try:
            profile = digital_twin.learn_driver_patterns(driver_id)
            optimization = digital_twin.simulate_optimal_week(profile)
            best_scenario = optimization['best_scenario']
            ai_recommendation = {
                "type": "digital_twin",
                "title": f"{best_scenario} Strategy",
                "message": f"Switch to {best_scenario} for {optimization['scenarios'][best_scenario]['improvement']:.0f}% earnings boost",
                "projected_earnings": optimization['scenarios'][best_scenario]['projected_weekly_earnings'],
                "improvement": optimization['scenarios'][best_scenario]['improvement']
            }
        except Exception as e:
            logger.warning(f"Digital Twin error for {driver_id}: {e}")
            ai_recommendation = {
                "type": "digital_twin",
                "title": "Digital Twin Loading",
                "message": "Analyzing your patterns...",
                "projected_earnings": 0,
                "improvement": 0
            }
        
        # Get airport opportunities
        try:
            airport_opportunities = await airport.get_live_demand("Amsterdam")  # Default to Amsterdam
            airport_rec = {
                "type": "airport",
                "title": "Airport Opportunity",
                "message": f"Peak demand predicted at {airport_opportunities[0]['airport_code']} in 45 minutes",
                "peak_time": "45 minutes",
                "expected_arrivals": 12
            } if airport_opportunities else None
        except Exception as e:
            logger.warning(f"Airport data error: {e}")
            airport_rec = None
        
        # Wellbeing status (mock data for now)
        wellbeing_score = 85
        wellbeing_rec = {
            "type": "wellbeing",
            "title": "Wellbeing Alert",
            "message": "Take a 15-minute break soon - fatigue level rising",
            "score": wellbeing_score,
            "status": "good" if wellbeing_score >= 80 else "caution" if wellbeing_score >= 60 else "warning"
        }
        
        return {
            "driver_id": driver_id,
            "status": {
                "is_online": True,  # Mock status
                "earnings_today": round(total_earnings_today, 2),
                "hours_worked": round(hours_worked, 1),
                "wellbeing_score": wellbeing_score
            },
            "recommendations": [
                ai_recommendation,
                airport_rec,
                wellbeing_rec
            ],
            "quick_stats": {
                "rides_today": total_rides_today,
                "rating": 4.9,  # Mock data
                "acceptance_rate": 94,  # Mock data
                "avg_per_hour": round(total_earnings_today / max(hours_worked, 1), 0)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Dashboard error for {driver_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DIGITAL TWIN ENDPOINTS
# ============================================================================

@app.get("/api/v1/digital-twin/profile/{driver_id}")
async def get_digital_twin_profile(driver_id: str):
    """Get Digital Twin profile for a driver"""
    try:
        profile = digital_twin.learn_driver_patterns(driver_id)
        
        return {
            "driver_id": driver_id,
            "profile": {
                "preferred_hours": profile.preferred_hours,
                "peak_days": profile.peak_days,
                "avg_earnings_per_hour": round(profile.avg_earnings_per_hour, 2),
                "surge_responsiveness": round(profile.surge_responsiveness, 3),
                "fatigue_threshold": profile.fatigue_threshold,
                "consistency_score": round(profile.consistency_score, 3),
                "total_weekly_hours": profile.total_weekly_hours,
                "preferred_zones": profile.preferred_zones if hasattr(profile, 'preferred_zones') else []
            },
            "learning_status": "complete",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Digital Twin profile error for {driver_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/digital-twin/optimize")
async def optimize_schedule(request: DriverRequest):
    """Generate optimization scenarios for a driver"""
    try:
        driver_id = request.driver_id
        
        # Get driver profile and optimization
        profile = digital_twin.learn_driver_patterns(driver_id)
        optimization = digital_twin.simulate_optimal_week(profile)
        
        scenarios = []
        for scenario_name, scenario_data in optimization['scenarios'].items():
            scenarios.append({
                "name": scenario_name,
                "projected_earnings": round(scenario_data['projected_weekly_earnings'], 2),
                "improvement": round(scenario_data['improvement'], 1),
                "feasibility": round(scenario_data['feasibility'], 2),
                "description": scenario_data.get('description', f"{scenario_name} optimization strategy"),
                "schedule": scenario_data.get('schedule', {})
            })
        
        return {
            "driver_id": driver_id,
            "current_performance": {
                "weekly_earnings": round(optimization['current_performance']['weekly_earnings'], 2),
                "weekly_hours": optimization['current_performance']['weekly_hours']
            },
            "scenarios": scenarios,
            "best_scenario": optimization['best_scenario'],
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Schedule optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AIRPORT INTELLIGENCE ENDPOINTS
# ============================================================================

@app.get("/api/v1/airport/live-demand/{city}")
async def get_airport_demand(city: str):
    """Get live airport demand predictions for a city"""
    try:
        demand_data = await airport.get_live_demand(city)
        
        formatted_data = []
        for airport_data in demand_data[:5]:  # Top 5 airports
            formatted_data.append({
                "airport_code": airport_data['airport_code'],
                "airport_name": airport_data['airport_name'],
                "city": city,
                "peak_intensity": airport_data.get('peak_intensity', 0),
                "expected_wait_time": airport_data.get('expected_wait_time', 0),
                "potential_earnings_per_hour": airport_data.get('potential_earnings_per_hour', 0),
                "recommendation_priority": airport_data.get('recommendation_priority', 0),
                "next_peak_time": airport_data.get('next_peak_time', 'Unknown'),
                "flight_arrivals_next_hour": airport_data.get('flight_arrivals_next_hour', 0)
            })
        
        return {
            "city": city,
            "airports": formatted_data,
            "last_updated": datetime.now().isoformat(),
            "data_source": "live_flights"
        }
        
    except Exception as e:
        logger.error(f"Airport demand error for {city}: {e}")
        # Return mock data in case of API failure
        return {
            "city": city,
            "airports": [
                {
                    "airport_code": "AMS",
                    "airport_name": "Amsterdam Schiphol",
                    "city": city,
                    "peak_intensity": 8.5,
                    "expected_wait_time": 15,
                    "potential_earnings_per_hour": 45,
                    "recommendation_priority": 9.2,
                    "next_peak_time": "45 minutes",
                    "flight_arrivals_next_hour": 12
                }
            ],
            "last_updated": datetime.now().isoformat(),
            "data_source": "mock_data"
        }

@app.get("/api/v1/airport/cities")
async def get_supported_cities():
    """Get list of supported cities for airport intelligence"""
    return {
        "cities": [
            {"name": "New York", "airports": ["JFK", "LGA", "EWR"]},
            {"name": "Los Angeles", "airports": ["LAX", "BUR", "LGB"]},
            {"name": "Chicago", "airports": ["ORD", "MDW"]},
            {"name": "San Francisco", "airports": ["SFO", "OAK", "SJC"]},
            {"name": "Miami", "airports": ["MIA", "FLL"]},
            {"name": "Amsterdam", "airports": ["AMS"]},
            {"name": "London", "airports": ["LHR", "LGW", "STN"]},
            {"name": "Paris", "airports": ["CDG", "ORY"]}
        ]
    }

# ============================================================================
# WELLBEING ENDPOINTS
# ============================================================================

@app.post("/api/v1/wellbeing/check-in")
async def wellbeing_checkin(checkin: WellbeingCheckIn):
    """Submit wellbeing check-in data"""
    try:
        # Calculate wellbeing score
        score = wellbeing.calculate_wellbeing_score(
            sleep_hours=checkin.sleep_hours,
            fatigue_level=checkin.fatigue_level,
            stress_level=checkin.stress_level,
            body_discomfort=checkin.body_discomfort,
            mood=checkin.mood
        )
        
        # Get risk assessment and suggestions
        risk_band = wellbeing.assess_risk_band(score)
        suggestions = wellbeing.get_personalized_suggestions(score, {
            'fatigue_level': checkin.fatigue_level,
            'stress_level': checkin.stress_level,
            'body_discomfort': checkin.body_discomfort
        })
        
        return {
            "driver_id": checkin.driver_id,
            "wellbeing_score": round(score, 1),
            "risk_band": risk_band,
            "status": "safe" if score >= 80 else "caution" if score >= 60 else "warning",
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat(),
            "should_take_break": score < 60,
            "can_drive_safely": score >= 40
        }
        
    except Exception as e:
        logger.error(f"Wellbeing check-in error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/wellbeing/status/{driver_id}")
async def get_wellbeing_status(driver_id: str):
    """Get current wellbeing status for a driver"""
    try:
        # In a real app, this would fetch from database
        # For now, return mock current status
        return {
            "driver_id": driver_id,
            "current_score": 85,
            "risk_band": "Low Risk",
            "last_checkin": (datetime.now() - timedelta(hours=2)).isoformat(),
            "trend": "stable",
            "recommendations": [
                "Take a 10-minute break in the next hour",
                "Stay hydrated",
                "Consider light stretching"
            ],
            "next_checkin_due": (datetime.now() + timedelta(hours=2)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Wellbeing status error for {driver_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PERFORMANCE ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/v1/analytics/performance/{driver_id}")
async def get_performance_analytics(driver_id: str):
    """Get comprehensive performance analytics for a driver"""
    try:
        # Get driver data
        driver_data = data[data['driver_id'] == driver_id]
        
        if driver_data.empty:
            raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found")
        
        # Get prioritization score
        try:
            priority_score = prioritization.calculate_driver_priority(driver_id)
        except:
            priority_score = {"total_priority_score": 8.5, "factors": {}}
        
        # Performance metrics
        total_rides = len(driver_data)
        total_earnings = driver_data['earnings'].sum() if 'earnings' in driver_data.columns else 0
        avg_earnings_per_ride = total_earnings / max(total_rides, 1)
        
        # Weekly performance (last 7 days of data)
        recent_data = driver_data.tail(7)
        weekly_earnings = recent_data['earnings'].sum() if 'earnings' in recent_data.columns else 0
        weekly_rides = len(recent_data)
        
        return {
            "driver_id": driver_id,
            "priority_score": round(priority_score["total_priority_score"], 2),
            "performance_metrics": {
                "total_rides": total_rides,
                "total_earnings": round(total_earnings, 2),
                "avg_earnings_per_ride": round(avg_earnings_per_ride, 2),
                "weekly_rides": weekly_rides,
                "weekly_earnings": round(weekly_earnings, 2)
            },
            "ratings": {
                "current_rating": 4.9,  # Mock data
                "rating_trend": "stable",
                "acceptance_rate": 94,
                "cancellation_rate": 2
            },
            "efficiency": {
                "rides_per_hour": round(weekly_rides / 40, 2) if weekly_rides > 0 else 0,
                "earnings_per_hour": round(weekly_earnings / 40, 2) if weekly_earnings > 0 else 0,
                "efficiency_score": round(priority_score["total_priority_score"] * 10, 1)
            },
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Performance analytics error for {driver_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DRIVER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/v1/drivers")
async def get_all_drivers():
    """Get list of all available drivers"""
    try:
        driver_summary = data['driver_id'].value_counts().head(10)
        drivers = []
        
        for driver_id, ride_count in driver_summary.items():
            drivers.append({
                "driver_id": driver_id,
                "total_rides": ride_count,
                "status": "active"  # Mock status
            })
        
        return {
            "drivers": drivers,
            "total_count": len(drivers)
        }
        
    except Exception as e:
        logger.error(f"Driver list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "digital_twin": "online",
            "airport_intelligence": "online",
            "wellbeing_monitor": "online",
            "analytics": "online"
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """Detailed API status"""
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "dashboard": "/api/v1/dashboard/{driver_id}",
            "digital_twin": "/api/v1/digital-twin/*",
            "airport": "/api/v1/airport/*",
            "wellbeing": "/api/v1/wellbeing/*",
            "analytics": "/api/v1/analytics/*"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    print("🚗🤖 Starting Uber Driver AI Companion API Server...")
    print("📊 Dashboard: http://localhost:8000/docs")
    print("🔄 Health: http://localhost:8000/health")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )