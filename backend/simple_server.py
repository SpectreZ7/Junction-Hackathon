#!/usr/bin/env python3
"""
🚗🤖 UBER DRIVER AI COMPANION - SIMPLE BACKEND API SERVER 🤖🚗

Simplified FastAPI server with mock data for frontend integration testing.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
from datetime import datetime, timedelta
import logging

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

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/api/v1/dashboard/{driver_id}")
async def get_dashboard_data(driver_id: str):
    """Get comprehensive dashboard data for a driver"""
    try:
        # Mock data for demo
        return {
            "driver_id": driver_id,
            "status": {
                "is_online": True,
                "earnings_today": 248.50,
                "hours_worked": 6.5,
                "wellbeing_score": 85
            },
            "recommendations": [
                {
                    "type": "digital_twin",
                    "title": "Early Bird Strategy",
                    "message": "Switch to Early Bird schedule for 18% earnings boost",
                    "projected_earnings": 312,
                    "improvement": 18
                },
                {
                    "type": "airport",
                    "title": "Airport Opportunity",
                    "message": "AMS peak in 45 minutes - 12 arrivals expected",
                    "peak_time": "45 minutes",
                    "expected_arrivals": 12
                },
                {
                    "type": "wellbeing",
                    "title": "Wellbeing Alert",
                    "message": "Take a 15-minute break soon - fatigue level rising",
                    "score": 85,
                    "status": "good"
                }
            ],
            "quick_stats": {
                "rides_today": 18,
                "rating": 4.9,
                "acceptance_rate": 94,
                "avg_per_hour": 38
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
    return {
        "driver_id": driver_id,
        "profile": {
            "preferred_hours": [7, 8, 9, 16, 17, 18, 19, 20],
            "peak_days": ["Monday", "Tuesday", "Friday", "Saturday"],
            "avg_earnings_per_hour": 42.50,
            "surge_responsiveness": 0.85,
            "fatigue_threshold": 8,
            "consistency_score": 0.78,
            "total_weekly_hours": 35,
            "preferred_zones": ["Airport", "Business District", "University Area"]
        },
        "learning_status": "complete",
        "last_updated": datetime.now().isoformat()
    }

@app.post("/api/v1/digital-twin/optimize")
async def optimize_schedule(request: DriverRequest):
    """Generate optimization scenarios for a driver"""
    return {
        "driver_id": request.driver_id,
        "current_performance": {
            "weekly_earnings": 1250.00,
            "weekly_hours": 35
        },
        "scenarios": [
            {
                "name": "Current Pattern (Optimized)",
                "projected_earnings": 1312.50,
                "improvement": 5.0,
                "feasibility": 0.95,
                "description": "Optimized version of your current schedule",
                "schedule": {}
            },
            {
                "name": "Early Bird",
                "projected_earnings": 1475.00,
                "improvement": 18.0,
                "feasibility": 0.78,
                "description": "Start 2 hours earlier to catch morning rush",
                "schedule": {}
            },
            {
                "name": "Surge Optimizer",
                "projected_earnings": 1625.00,
                "improvement": 30.0,
                "feasibility": 0.65,
                "description": "Focus on peak surge times and events",
                "schedule": {}
            },
            {
                "name": "Consistent Grind",
                "projected_earnings": 1400.00,
                "improvement": 12.0,
                "feasibility": 0.88,
                "description": "Regular 9-6 schedule with consistent hours",
                "schedule": {}
            },
            {
                "name": "Weekend Warrior",
                "projected_earnings": 1550.00,
                "improvement": 24.0,
                "feasibility": 0.72,
                "description": "Maximize weekend earnings potential",
                "schedule": {}
            }
        ],
        "best_scenario": "Weekend Warrior",
        "analysis_date": datetime.now().isoformat()
    }

# ============================================================================
# AIRPORT INTELLIGENCE ENDPOINTS
# ============================================================================

@app.get("/api/v1/airport/live-demand/{city}")
async def get_airport_demand(city: str):
    """Get live airport demand predictions for a city"""
    # Mock airport data based on city
    airports_by_city = {
        "amsterdam": [
            {
                "airport_code": "AMS",
                "airport_name": "Amsterdam Schiphol",
                "city": city,
                "peak_intensity": 8.5,
                "expected_wait_time": 15,
                "potential_earnings_per_hour": 65,
                "recommendation_priority": 9.2,
                "next_peak_time": "45 minutes",
                "flight_arrivals_next_hour": 12
            }
        ],
        "london": [
            {
                "airport_code": "LHR",
                "airport_name": "London Heathrow",
                "city": city,
                "peak_intensity": 9.1,
                "expected_wait_time": 22,
                "potential_earnings_per_hour": 58,
                "recommendation_priority": 8.8,
                "next_peak_time": "1 hour 15 minutes",
                "flight_arrivals_next_hour": 18
            },
            {
                "airport_code": "LGW",
                "airport_name": "London Gatwick",
                "city": city,
                "peak_intensity": 7.2,
                "expected_wait_time": 18,
                "potential_earnings_per_hour": 52,
                "recommendation_priority": 7.5,
                "next_peak_time": "2 hours",
                "flight_arrivals_next_hour": 8
            }
        ]
    }
    
    city_lower = city.lower()
    airports = airports_by_city.get(city_lower, airports_by_city["amsterdam"])
    
    return {
        "city": city,
        "airports": airports,
        "last_updated": datetime.now().isoformat(),
        "data_source": "mock_data"
    }

@app.get("/api/v1/airport/cities")
async def get_supported_cities():
    """Get list of supported cities for airport intelligence"""
    return {
        "cities": [
            {"name": "Amsterdam", "airports": ["AMS"]},
            {"name": "London", "airports": ["LHR", "LGW", "STN"]},
            {"name": "Paris", "airports": ["CDG", "ORY"]},
            {"name": "New York", "airports": ["JFK", "LGA", "EWR"]},
            {"name": "Los Angeles", "airports": ["LAX", "BUR", "LGB"]}
        ]
    }

# ============================================================================
# WELLBEING ENDPOINTS
# ============================================================================

@app.post("/api/v1/wellbeing/check-in")
async def wellbeing_checkin(checkin: WellbeingCheckIn):
    """Submit wellbeing check-in data"""
    # Simple wellbeing calculation
    sleep_score = min(checkin.sleep_hours / 8.0 * 100, 100)
    fatigue_score = (6 - checkin.fatigue_level) / 5.0 * 100
    stress_score = (6 - checkin.stress_level) / 5.0 * 100
    comfort_score = (6 - checkin.body_discomfort) / 5.0 * 100
    mood_score = checkin.mood / 5.0 * 100
    
    overall_score = (sleep_score + fatigue_score + stress_score + comfort_score + mood_score) / 5
    
    # Risk assessment
    if overall_score >= 80:
        risk_band = "Low Risk"
        status = "safe"
    elif overall_score >= 60:
        risk_band = "Medium Risk" 
        status = "caution"
    elif overall_score >= 40:
        risk_band = "High Risk"
        status = "warning"
    else:
        risk_band = "Critical Risk"
        status = "danger"
    
    # Generate suggestions
    suggestions = []
    if checkin.fatigue_level >= 4:
        suggestions.append("Take a 20-minute break to rest")
    if checkin.stress_level >= 4:
        suggestions.append("Try some deep breathing exercises")
    if checkin.body_discomfort >= 4:
        suggestions.append("Stretch and adjust your seating position")
    if checkin.sleep_hours < 6:
        suggestions.append("Consider getting more sleep tonight")
    if not suggestions:
        suggestions.append("Keep up the good work!")
    
    return {
        "driver_id": checkin.driver_id,
        "wellbeing_score": round(overall_score, 1),
        "risk_band": risk_band,
        "status": status,
        "suggestions": suggestions,
        "timestamp": datetime.now().isoformat(),
        "should_take_break": overall_score < 60,
        "can_drive_safely": overall_score >= 40
    }

@app.get("/api/v1/wellbeing/status/{driver_id}")
async def get_wellbeing_status(driver_id: str):
    """Get current wellbeing status for a driver"""
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

# ============================================================================
# PERFORMANCE ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/v1/analytics/performance/{driver_id}")
async def get_performance_analytics(driver_id: str):
    """Get comprehensive performance analytics for a driver"""
    return {
        "driver_id": driver_id,
        "priority_score": 8.7,
        "performance_metrics": {
            "total_rides": 1247,
            "total_earnings": 15847.50,
            "avg_earnings_per_ride": 12.71,
            "weekly_rides": 89,
            "weekly_earnings": 1125.30
        },
        "ratings": {
            "current_rating": 4.9,
            "rating_trend": "increasing",
            "acceptance_rate": 94,
            "cancellation_rate": 2
        },
        "efficiency": {
            "rides_per_hour": 2.2,
            "earnings_per_hour": 28.13,
            "efficiency_score": 87
        },
        "analysis_date": datetime.now().isoformat()
    }

# ============================================================================
# DRIVER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/v1/drivers")
async def get_all_drivers():
    """Get list of all available drivers"""
    return {
        "drivers": [
            {"driver_id": "E10156", "total_rides": 1247, "status": "active"},
            {"driver_id": "E20234", "total_rides": 892, "status": "active"},
            {"driver_id": "E30445", "total_rides": 1456, "status": "active"},
            {"driver_id": "E40567", "total_rides": 678, "status": "active"},
            {"driver_id": "E50789", "total_rides": 2341, "status": "active"}
        ],
        "total_count": 5
    }

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
    print("🚗🤖 Starting Uber Driver AI Companion API Server (Mock Mode)...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔄 Health Check: http://localhost:8000/health")
    print("📱 Ready for frontend integration!")
    
    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )