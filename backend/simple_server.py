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
        # Get target income data for this driver
        import json
        target_income_data = None
        try:
            with open("driver_target_income.json", "r") as f:
                data = json.load(f)
            target_income_data = next((d for d in data["drivers"] if d["driver_id"] == driver_id), None)
        except FileNotFoundError:
            pass
        
        # Mock data for demo with target income integration
        current_earnings = target_income_data["current_daily_income"] if target_income_data else 248.50
        target_earnings = target_income_data["target_daily_income"] if target_income_data else 280
        goal_status = target_income_data["income_goal_status"] if target_income_data else "achieved"
        
        return {
            "driver_id": driver_id,
            "status": {
                "is_online": True,
                "earnings_today": current_earnings,
                "target_earnings_today": target_earnings,
                "earnings_progress": round((current_earnings / target_earnings) * 100, 1),
                "income_goal_status": goal_status,
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
                    "type": "hotspots",
                    "title": "Hotspot Opportunity",
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
            "preferred_hours": [0, 21, 10, 12, 6],
            "peak_days": ["Friday", "Tuesday", "Sunday"],
            "avg_earnings_per_hour": 28.14,
            "surge_responsiveness": -0.29,
            "fatigue_threshold": 8,
            "consistency_score": 0.12,
            "total_weekly_hours": 3.3,
            "preferred_zones": ["City Center", "Airport", "Business District"],
            "ride_statistics": {
                "total_rides": 33,
                "avg_ride_duration": 18.5,
                "busiest_hour": "0:00 (12AM)",
                "earnings_per_minute_all": 0.63,
                "earnings_per_minute_long": 0.33,
                "earnings_per_minute_short": 1.50
            },
            "weekly_breakdown": {
                "Monday": 5,
                "Tuesday": 5,
                "Wednesday": 4,
                "Thursday": 4,
                "Friday": 6,
                "Saturday": 4,
                "Sunday": 5
            }
        },
        "learning_status": "complete",
        "data_quality": "high",
        "confidence_score": 0.87,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v1/digital-twin/drivers")
async def get_available_drivers():
    """Get list of available drivers for analysis"""
    return {
        "total_drivers": 160,
        "top_drivers": [
            {"driver_id": "E10156", "rides": 33, "status": "most_active"},
            {"driver_id": "E10057", "rides": 30, "status": "active"},
            {"driver_id": "E10121", "rides": 29, "status": "active"},
            {"driver_id": "E10086", "rides": 28, "status": "active"},
            {"driver_id": "E10134", "rides": 28, "status": "active"},
            {"driver_id": "E10113", "rides": 28, "status": "active"},
            {"driver_id": "E10034", "rides": 26, "status": "active"},
            {"driver_id": "E10027", "rides": 26, "status": "active"},
            {"driver_id": "E10149", "rides": 26, "status": "active"},
            {"driver_id": "E10074", "rides": 26, "status": "active"}
        ],
        "sample_ids": ["E10111", "E10152", "E10157", "E10024", "E10146", "E10131", "E10037", "E10139", "E10020", "E10147"]
    }

@app.post("/api/v1/digital-twin/compare")
async def compare_drivers(driver_ids: List[str]):
    """Compare multiple drivers"""
    comparisons = []
    
    for i, driver_id in enumerate(driver_ids[:3]):  # Limit to 3 drivers
        # Mock comparison data
        mock_data = [
            {
                "driver_id": "E10156",
                "avg_earnings_per_hour": 28.14,
                "surge_response": -0.29,
                "consistency": 0.12,
                "best_strategy": "surge_optimizer",
                "current_weekly": 74.11,
                "optimized_weekly": 572.02
            },
            {
                "driver_id": "E10057", 
                "avg_earnings_per_hour": 25.14,
                "surge_response": 0.39,
                "consistency": 0.13,
                "best_strategy": "surge_optimizer",
                "current_weekly": 70.94,
                "optimized_weekly": 690.49
            },
            {
                "driver_id": "E10121",
                "avg_earnings_per_hour": 31.22,
                "surge_response": 0.45,
                "consistency": 0.28,
                "best_strategy": "weekend_warrior",
                "current_weekly": 89.33,
                "optimized_weekly": 634.12
            }
        ]
        
        data = mock_data[i] if i < len(mock_data) else mock_data[0]
        data["driver_id"] = driver_id
        comparisons.append(data)
    
    return {
        "comparison_date": datetime.now().isoformat(),
        "drivers": comparisons,
        "insights": [
            "All drivers show significant optimization potential",
            "Surge timing is consistently the best strategy",
            "Weekend optimization varies by driver profile"
        ]
    }

@app.post("/api/v1/digital-twin/optimize")
async def optimize_schedule(request: DriverRequest):
    """Generate optimization scenarios for a driver"""
    # Enhanced mock data based on actual demo output
    mock_scenarios = [
        {
            "name": "current_pattern",
            "display_name": "Current Pattern (Optimized)",
            "projected_earnings": 363.02,
            "improvement": 389.9,
            "feasibility": 0.523,
            "description": "Your current driving pattern optimized for maximum efficiency",
            "schedule": {
                "Friday": "0:00-1:00, 10:00-11:00, 12:00-13:00, 21:00-22:00",
                "Tuesday": "0:00-1:00, 10:00-11:00, 12:00-13:00, 21:00-22:00", 
                "Sunday": "0:00-1:00, 10:00-11:00, 12:00-13:00, 21:00-22:00"
            },
            "weekly_hours": 12,
            "is_recommended": False,
            "confidence": "Medium",
            "earnings_breakdown": {
                "base_fare": 280.50,
                "surge_multiplier": 82.52
            }
        },
        {
            "name": "early_bird",
            "display_name": "Early Bird",
            "projected_earnings": 259.85,
            "improvement": 250.6,
            "feasibility": 0.273,
            "description": "Start earlier to catch morning commuters and business travelers",
            "schedule": {
                "Friday": "8:00-9:00, 10:00-11:00, 19:00-20:00",
                "Tuesday": "8:00-9:00, 10:00-11:00, 19:00-20:00",
                "Sunday": "8:00-9:00, 10:00-11:00, 19:00-20:00"
            },
            "weekly_hours": 9,
            "is_recommended": False,
            "confidence": "Low",
            "earnings_breakdown": {
                "base_fare": 195.50,
                "surge_multiplier": 64.35
            }
        },
        {
            "name": "surge_optimizer",
            "display_name": "Surge Optimizer ⭐",
            "projected_earnings": 572.02,
            "improvement": 671.9,
            "feasibility": 0.648,
            "description": "Focus on high-surge periods and peak demand times for maximum earnings",
            "schedule": {
                "Friday": "17:00-23:00",
                "Tuesday": "0:00-1:00, 10:00-11:00, 12:00-13:00, 21:00-22:00",
                "Sunday": "0:00-1:00, 10:00-11:00, 12:00-13:00, 21:00-22:00",
                "Saturday": "17:00-23:00"
            },
            "weekly_hours": 16,
            "is_recommended": True,
            "confidence": "High",
            "earnings_breakdown": {
                "base_fare": 340.20,
                "surge_multiplier": 231.82
            }
        },
        {
            "name": "consistent_grind",
            "display_name": "Consistent Grind",
            "projected_earnings": 819.18,
            "improvement": 1005.4,
            "feasibility": 0.273,
            "description": "Regular 9-5 schedule with consistent daily patterns - highest earnings but demanding",
            "schedule": {
                "Monday": "9:00-12:00, 16:00-19:00",
                "Tuesday": "9:00-12:00, 16:00-19:00",
                "Wednesday": "9:00-12:00, 16:00-19:00",
                "Thursday": "9:00-12:00, 16:00-19:00",
                "Friday": "9:00-12:00, 16:00-19:00"
            },
            "weekly_hours": 30,
            "is_recommended": False,
            "confidence": "Low",
            "earnings_breakdown": {
                "base_fare": 615.50,
                "surge_multiplier": 203.68
            }
        },
        {
            "name": "weekend_warrior",
            "display_name": "Weekend Warrior",
            "projected_earnings": 591.01,
            "improvement": 697.5,
            "feasibility": 0.398,
            "description": "Maximize weekend earnings when demand and surge pricing are highest",
            "schedule": {
                "Friday": "16:00-23:00",
                "Saturday": "12:00-15:00, 18:00-23:00",
                "Sunday": "12:00-15:00, 17:00-20:00"
            },
            "weekly_hours": 18,
            "is_recommended": False,
            "confidence": "Medium",
            "earnings_breakdown": {
                "base_fare": 425.75,
                "surge_multiplier": 165.26
            }
        }
    ]
    
    return {
        "driver_id": request.driver_id,
        "current_performance": {
            "weekly_earnings": 74.11,
            "weekly_hours": 3.3,
            "weekly_rides": 8,
            "avg_earnings_per_hour": 22.46,
            "efficiency_score": 65
        },
        "behavioral_profile": {
            "preferred_hours": [0, 21, 10, 12, 6],
            "peak_days": ["Friday", "Tuesday", "Sunday"],
            "avg_earnings_per_hour": 28.14,
            "surge_responsiveness": -0.29,
            "fatigue_threshold": 8,
            "consistency_score": 0.12
        },
        "scenarios": mock_scenarios,
        "best_scenario": "surge_optimizer",
        "potential_increase": 497.91,
        "key_insights": [
            "Current weekly earnings are significantly below potential",
            "Surge timing optimization offers the best ROI",
            "Weekend and evening hours show highest demand",
            "Short rides (< 15 min) yield highest per-minute earnings"
        ],
        "analysis_date": datetime.now().isoformat(),
        "confidence_level": "High",
        "data_points_analyzed": 33
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

@app.get("/api/v1/drivers/target-income")
async def get_all_driver_target_income():
    """Get target income data for all drivers"""
    import json
    try:
        with open("driver_target_income.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        # Fallback to mock data if file not found
        return {
            "drivers": [
                {
                    "driver_id": "E10156",
                    "driver_name": "Marcus Chen",
                    "target_daily_income": 280,
                    "current_daily_income": 248.50,
                    "income_goal_status": "achieved",
                    "target_weekly_income": 1960,
                    "target_monthly_income": 7840,
                    "performance_tier": "top_performer",
                    "city": "Amsterdam",
                    "experience_years": 3.5,
                    "vehicle_type": "Premium Sedan",
                    "specializations": ["airport_runs", "surge_hours", "weekend_shifts"]
                }
            ],
            "summary": {
                "total_drivers": 1,
                "average_target_daily": 280,
                "average_current_daily": 248.50,
                "performance_distribution": {"top_performer": 1},
                "income_goal_achievement_rate": 100,
                "last_updated": datetime.now().isoformat()
            }
        }

@app.get("/api/v1/drivers/{driver_id}/target-income")
async def get_driver_target_income(driver_id: str):
    """Get target income data for a specific driver"""
    import json
    try:
        with open("driver_target_income.json", "r") as f:
            data = json.load(f)
        
        # Find the specific driver
        driver_data = next((d for d in data["drivers"] if d["driver_id"] == driver_id), None)
        if driver_data:
            return driver_data
        else:
            raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found")
    except FileNotFoundError:
        # Fallback mock data
        mock_driver = {
            "driver_id": driver_id,
            "driver_name": f"Driver {driver_id}",
            "target_daily_income": 250,
            "current_daily_income": 230.50,
            "income_goal_status": "achieved",
            "target_weekly_income": 1750,
            "target_monthly_income": 7000,
            "performance_tier": "high_performer",
            "city": "Amsterdam",
            "experience_years": 3.0,
            "vehicle_type": "Standard Sedan",
            "specializations": ["business_district", "evening_shifts"]
        }
        return mock_driver

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