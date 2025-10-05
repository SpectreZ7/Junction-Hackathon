# Orchestrator Intelligence Agent - Production Version with Weather Integration

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

CITY = "New York"
HOURS_AHEAD = 12
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.3
MAX_TOKENS = 4000

# Driver parameters
DRIVER_START_LOCATION = {"lat": 40.7580, "lng": -73.9855, "name": "Times Square"}
AVERAGE_SPEED_MPH = 20
MIN_REVENUE_THRESHOLD = 20
MAX_PLANNING_HOURS = 12
TRAVEL_BUFFER_MINUTES = 10
TURNAROUND_TIME_MINUTES = 5

# ============================================================================

class OrchestratorConfig:
    def __init__(self, city: str):
        self.groq_api_key = GROQ_API_KEY
        self.groq_model = GROQ_MODEL
        self.city = city
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS
        self.driver_start_location = DRIVER_START_LOCATION
        self.avg_speed_mph = AVERAGE_SPEED_MPH
        self.travel_buffer = TRAVEL_BUFFER_MINUTES
        self.turnaround_time = TURNAROUND_TIME_MINUTES
        self.max_planning_hours = MAX_PLANNING_HOURS
        self.min_revenue_threshold = MIN_REVENUE_THRESHOLD
        
        self.system_prompt = """
You are a master AI orchestrator for Uber driver revenue optimization with WEATHER INTELLIGENCE.

You receive data from multiple intelligence agents (Event Agent, Airport Agent, and Weather Agent) and create an optimal route plan.

WEATHER IMPACT ON UBER DEMAND:
- Rain/Snow = HIGHER demand (people avoid walking/public transport) but LONGER trip times
- Cold weather (<10°C) = HIGHER demand, especially combined with rain
- Good weather = LOWER demand but FASTER trips
- Peak rain hours = Surge pricing likely, maximize revenue
- Bad weather at airports = Flight delays = More passengers needing rides

Your mission:
1. Analyze all detected peaks from Event, Airport, AND Weather agents
2. Use the ACTUAL weather data provided - don't invent conditions
3. Create a strategic schedule that maximizes total revenue while accounting for:
   - REAL weather conditions from the data (rain chance, temperature, wind)
   - Travel time adjustments for bad weather (+20-30% in rain/snow)
   - Surge pricing opportunities during bad weather
   - Event and airport peaks
   - Opportunity costs
4. Weight bad weather hours MORE HEAVILY when they actually exist in the data
5. Recommend staying near high-demand areas during peak rain hours

CRITICAL RULES:
- Use ONLY the actual weather conditions from the provided data
- Calculate revenue multipliers based on REAL rain_chance_percent and temp_c from data
- Use ACTUAL estimated_wait_minutes from peaks
- Use ACTUAL travel_time_from_start_minutes from peaks
- DO NOT invent weather conditions that don't exist in the data

IMPORTANT: Respond ONLY in valid JSON format with no additional text.
"""

config = OrchestratorConfig(city=CITY)

class GeospatialCalculator:
    """Calculate distances and travel times"""
    
    @staticmethod
    def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in miles using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 3959  # Earth's radius in miles
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def calculate_travel_time(distance_miles: float, avg_speed_mph: float, buffer_minutes: int = 0, weather_factor: float = 1.0) -> int:
        """Calculate travel time in minutes with weather adjustment"""
        base_travel_time = (distance_miles / avg_speed_mph) * 60
        adjusted_time = base_travel_time * weather_factor
        return int(adjusted_time + buffer_minutes)

class AgentDataCollector:
    """Collects data from Event, Airport, and Weather agents by importing them"""
    
    def __init__(self, city: str, hours_ahead: int):
        self.city = city
        self.hours_ahead = hours_ahead
    
    def get_event_agent_data(self) -> Dict:
        """Call Event Intelligence Agent API"""
        try:
            import requests
            
            # Call the event agent API
            response = requests.post(
                "http://localhost:1001/analyze",
                json={"city": self.city},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "agent_type": "event_intelligence", "all_peaks": [], "error": f"API returned {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "agent_type": "event_intelligence", "all_peaks": [], "error": str(e)}
    
    def get_airport_agent_data(self) -> Dict:
        """Import and run Airport Intelligence Agent"""
        try:
            import requests
            
            # Call the airport agent API for all airports
            response = requests.get(
                "http://localhost:1000/all_airports",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "agent_type": "airport_intelligence", "all_peaks_combined": [], "error": f"API returned {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "agent_type": "airport_intelligence", "all_peaks_combined": [], "error": str(e)}
    
    def get_weather_agent_data(self) -> Dict:
        """Import and run Weather Intelligence Agent"""
        try:
            try:
                from weather_agent import WeatherAgent
            except ImportError:
                import agents.weather_agent.weather_agent as weather_agent
                WeatherAgent = weather_agent.WeatherAgent
            
            weather_agent_instance = WeatherAgent(api_key=os.getenv("WEATHER_API_KEY", "7a22cd490a5046d9b48120123250410"))
            weather_data = weather_agent_instance.get_weather_analysis("New York")
            
            return weather_data
            
        except Exception as e:
            return {"status": "error", "agent_type": "weather_intelligence", "hourly_forecast_24h": [], "optimal_ride_hours": [], "error": str(e)}
    
    def collect_all_agent_data(self) -> Tuple[Dict, Dict, Dict]:
        """Run all three agents and collect their recommendations"""
        event_data = self.get_event_agent_data()
        airport_data = self.get_airport_agent_data()
        weather_data = self.get_weather_agent_data()
        
        return event_data, airport_data, weather_data

class OrchestratorAgent:
    """Master orchestrator using Groq AI to create optimal route plans with weather intelligence"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.groq_client = Groq(api_key=config.groq_api_key)
        self.geo_calc = GeospatialCalculator()
        self.collector = AgentDataCollector(config.city, config.max_planning_hours)
        self.agent_id = f"orchestrator_{config.city.lower().replace(' ', '_')}"
    
    def _convert_priority_to_score(self, priority: str) -> float:
        """Convert priority string to numeric score"""
        priority_map = {
            'high': 0.9,
            'medium': 0.6,
            'low': 0.3
        }
        return priority_map.get(priority.lower(), 0.5)
    
    def _calculate_weather_multiplier(self, hour_data: Dict) -> float:
        """Calculate revenue multiplier based on weather conditions"""
        rain_chance = hour_data.get('rain_chance_percent', 0)
        temp_c = hour_data.get('temp_c', 15)
        
        multiplier = 1.0
        
        if rain_chance > 30:
            multiplier += (rain_chance / 100) * 0.5
        
        if temp_c < 10:
            multiplier += (10 - temp_c) * 0.02
        
        return min(multiplier, 2.0)
    
    def prepare_peaks_for_ai(self, event_data: Dict, airport_data: Dict, weather_data: Dict) -> List[Dict]:
        """Extract and enrich all peaks with travel calculations and weather data"""
        
        all_peaks = []
        current_location = self.config.driver_start_location
        
        weather_hourly = {h['datetime']: h for h in weather_data.get('hourly_forecast_24h', [])}
        
        event_peaks = event_data.get('all_peaks', [])
        for peak in event_peaks:
            venue_locations = {
                "Madison Square Garden": {"lat": 40.7505, "lng": -73.9934},
                "Barclays Center": {"lat": 40.6826, "lng": -73.9754},
                "Yankee Stadium": {"lat": 40.8296, "lng": -73.9262},
                "Radio City Music Hall": {"lat": 40.7599, "lng": -73.9799},
                "Brooklyn Steel": {"lat": 40.7183, "lng": -73.9571},
                "Terminal 5": {"lat": 40.7677, "lng": -73.9887},
                "Webster Hall": {"lat": 40.7298, "lng": -73.9891}
            }
            
            venue_name = peak.get('venue_name', 'Unknown Venue')
            location = venue_locations.get(venue_name, {"lat": 40.7580, "lng": -73.9855})
            
            distance = self.geo_calc.haversine_distance(
                current_location['lat'], current_location['lng'],
                location['lat'], location['lng']
            )
            
            time_window = peak.get('time_window', '')
            peak_hour = time_window.split('-')[0] if '-' in time_window else None
            weather_for_peak = None
            weather_multiplier = 1.0
            
            if peak_hour:
                for weather_time, weather_info in weather_hourly.items():
                    if peak_hour in weather_time:
                        weather_for_peak = weather_info
                        weather_multiplier = self._calculate_weather_multiplier(weather_info)
                        break
            
            weather_factor = 1.0
            if weather_for_peak:
                rain_chance = weather_for_peak.get('rain_chance_percent', 0)
                if rain_chance > 50:
                    weather_factor = 1.3
                elif rain_chance > 20:
                    weather_factor = 1.15
            
            travel_time = self.geo_calc.calculate_travel_time(
                distance, self.config.avg_speed_mph, self.config.travel_buffer, weather_factor
            )
            
            estimated_revenue = peak.get('estimated_revenue', 
                                peak.get('expected_revenue',
                                event_data.get('avg_event_fare', 25)))
            
            adjusted_revenue = estimated_revenue * weather_multiplier
            
            all_peaks.append({
                'peak_id': peak.get('peak_id', 'event_unknown'),
                'source': 'event',
                'time_window': peak.get('time_window', 'N/A'),
                'description': f"{peak.get('event_name', 'Event')} at {venue_name}",
                'location_name': venue_name,
                'location': location,
                'base_revenue': estimated_revenue,
                'estimated_revenue': round(adjusted_revenue, 2),
                'weather_multiplier': round(weather_multiplier, 2),
                'estimated_attendees': peak.get('estimated_attendees', 0),
                'estimated_wait_minutes': peak.get('estimated_wait_minutes', 
                                                   peak.get('waiting_time_minutes', 15)),
                'priority': peak.get('priority', 'medium'),
                'priority_score': self._convert_priority_to_score(peak.get('priority', 'medium')),
                'distance_from_start_miles': round(distance, 2),
                'travel_time_from_start_minutes': travel_time,
                'weather_conditions': weather_for_peak if weather_for_peak else None
            })
        
        airport_peaks = airport_data.get('all_peaks_combined', [])
        for peak in airport_peaks:
            airport_locations = {
                'JFK': {'lat': 40.6413, 'lng': -73.7781, 'name': 'JFK Airport'},
                'LGA': {'lat': 40.7769, 'lng': -73.8740, 'name': 'LaGuardia Airport'},
                'EWR': {'lat': 40.6895, 'lng': -74.1745, 'name': 'Newark Airport'}
            }
            
            airport_code = peak.get('airport_code', 'JFK')
            location_data = airport_locations.get(airport_code, airport_locations['JFK'])
            
            distance = self.geo_calc.haversine_distance(
                current_location['lat'], current_location['lng'],
                location_data['lat'], location_data['lng']
            )
            
            time_window = peak.get('time_window', '')
            peak_hour = time_window.split('-')[0] if '-' in time_window else None
            weather_for_peak = None
            weather_multiplier = 1.0
            
            if peak_hour:
                for weather_time, weather_info in weather_hourly.items():
                    if peak_hour in weather_time:
                        weather_for_peak = weather_info
                        weather_multiplier = self._calculate_weather_multiplier(weather_info)
                        break
            
            weather_factor = 1.0
            if weather_for_peak:
                rain_chance = weather_for_peak.get('rain_chance_percent', 0)
                if rain_chance > 50:
                    weather_factor = 1.3
                elif rain_chance > 20:
                    weather_factor = 1.15
            
            travel_time = self.geo_calc.calculate_travel_time(
                distance, self.config.avg_speed_mph, self.config.travel_buffer, weather_factor
            )
            
            base_revenue = peak.get('estimated_revenue', 50)
            adjusted_revenue = base_revenue * weather_multiplier
            
            all_peaks.append({
                'peak_id': peak.get('peak_id', 'airport_unknown'),
                'source': 'airport',
                'time_window': peak.get('time_window', 'N/A'),
                'description': f"{peak.get('num_flights', 0)} flights at {peak.get('airport_name', location_data['name'])}",
                'location_name': peak.get('airport_name', location_data['name']),
                'location': {'lat': location_data['lat'], 'lng': location_data['lng']},
                'base_revenue': base_revenue,
                'estimated_revenue': round(adjusted_revenue, 2),
                'weather_multiplier': round(weather_multiplier, 2),
                'num_flights': peak.get('num_flights', 0),
                'estimated_wait_minutes': peak.get('estimated_wait_minutes', 20),
                'priority': peak.get('priority', 'medium'),
                'priority_score': self._convert_priority_to_score(peak.get('priority', 'medium')),
                'distance_from_start_miles': round(distance, 2),
                'travel_time_from_start_minutes': travel_time,
                'weather_conditions': weather_for_peak if weather_for_peak else None
            })
        
        return all_peaks
    
    def create_optimal_plan_with_ai(self, event_data: Dict, airport_data: Dict, weather_data: Dict) -> Dict:
        """Use Groq AI to analyze all peaks with weather intelligence and create optimal route plan"""
        
        now = datetime.now()
        all_peaks = self.prepare_peaks_for_ai(event_data, airport_data, weather_data)
        
        if not all_peaks:
            return {
                "status": "no_opportunities",
                "message": "No viable peaks detected",
                "agent_id": self.agent_id,
                "timestamp": now.isoformat()
            }
        
        viable_peaks = [p for p in all_peaks if p['estimated_revenue'] >= self.config.min_revenue_threshold]
        
        if not viable_peaks:
            return {
                "status": "low_revenue",
                "message": f"No peaks exceed €{self.config.min_revenue_threshold} threshold",
                "agent_id": self.agent_id,
                "timestamp": now.isoformat(),
                "all_peaks_found": len(all_peaks)
            }
        
        weather_summary = weather_data.get('summary', {})
        optimal_weather_hours = weather_data.get('optimal_ride_hours', [])[:5]
        
        peaks_with_weather = []
        for peak in viable_peaks:
            peak_data = {
                'peak_id': peak['peak_id'],
                'source': peak['source'],
                'time_window': peak['time_window'],
                'description': peak['description'],
                'location_name': peak['location_name'],
                'base_revenue': peak['base_revenue'],
                'weather_adjusted_revenue': peak['estimated_revenue'],
                'weather_multiplier': peak['weather_multiplier'],
                'estimated_wait_minutes': peak['estimated_wait_minutes'],
                'priority': peak['priority'],
                'distance_from_start_miles': peak['distance_from_start_miles'],
                'travel_time_from_start_minutes': peak['travel_time_from_start_minutes']
            }
            
            
            if peak.get('weather_conditions'):
                weather = peak['weather_conditions']
                peak_data['weather'] = {
                    'temp_c': weather.get('temp_c'),
                    'condition': weather.get('condition'),
                    'rain_chance_percent': weather.get('rain_chance_percent'),
                    'wind_kph': weather.get('wind_kph')
                }
            
            peaks_with_weather.append(peak_data)
        
        user_prompt = f"""ORCHESTRATION ANALYSIS WITH WEATHER INTELLIGENCE - {self.config.city}

CURRENT STATUS:
- Current time: {now.strftime('%H:%M')}
- Current location: {self.config.driver_start_location['name']}
- Planning horizon: {self.config.max_planning_hours} hours
- Average speed: {self.config.avg_speed_mph} mph (adjusted for weather)

WEATHER FORECAST SUMMARY:
- Average temperature: {weather_summary.get('avg_temp_c', 'N/A')}°C
- Average rain chance: {weather_summary.get('avg_rain_chance', 'N/A')}%
- Best weather hour for rides: {weather_summary.get('best_hour_recommendation', 'N/A')}

TOP 5 WEATHER OPPORTUNITIES (highest demand hours):
{json.dumps(optimal_weather_hours, indent=2)}

DETECTED OPPORTUNITIES WITH WEATHER ADJUSTMENTS ({len(viable_peaks)} viable peaks):
{json.dumps(peaks_with_weather, indent=2)}

CRITICAL INSTRUCTIONS:
1. Use ONLY the actual weather data provided above
2. For weather_conditions field, extract from the 'weather' object in each peak
3. Use the ACTUAL weather_adjusted_revenue values provided (already calculated)
4. Use the ACTUAL estimated_wait_minutes from each peak
5. Use the ACTUAL travel_time_from_start_minutes from each peak
6. DO NOT invent or modify any values - use exactly what's in the data
7. If weather shows 0% rain and sunny conditions, acknowledge this reality
8. Revenue multipliers are ALREADY calculated in weather_adjusted_revenue

YOUR MISSION:
1. Create the most profitable route using the provided weather-adjusted revenues
2. Use actual weather conditions (if it's sunny, say sunny; if rainy, say rainy)
3. Account for the provided travel times
4. Balance event + airport diversity
5. Maximize total weather-adjusted revenue

RESPOND in this exact JSON format (fill with ACTUAL values from data above):
{{
  "optimal_route": [
    {{
      "sequence": <number>,
      "peak_id": "<exact peak_id from data>",
      "source": "<event or airport>",
      "location": "<location_name from data>",
      "arrival_time": "<HH:MM>",
      "service_time_window": "<HH:MM-HH:MM>",
      "departure_time": "<HH:MM>",
      "base_revenue": <base_revenue from data>,
      "weather_adjusted_revenue": <weather_adjusted_revenue from data>,
      "weather_multiplier": <weather_multiplier from data>,
      "weather_conditions": "<condition from weather object>, <temp_c>°C",
      "estimated_wait_minutes": <estimated_wait_minutes from data>,
      "travel_to_next_minutes": <calculated based on travel times>,
      "reasoning": "<why chosen, mentioning ACTUAL weather>"
    }}
  ],
  "rejected_opportunities": [
    {{
      "peak_id": "<exact peak_id>",
      "reason": "<why rejected>",
      "potential_revenue_lost": <number>
    }}
  ],
  "summary": {{
    "total_base_revenue": <sum of base revenues>,
    "total_weather_adjusted_revenue": <sum of adjusted revenues>,
    "weather_bonus_revenue": <difference>,
    "total_active_time_hours": <calculated>,
    "revenue_per_hour": <calculated>,
    "number_of_stops": <count>,
    "total_distance_miles": <sum>,
    "total_wait_time_minutes": <sum>,
    "bad_weather_stops": <count where rain > 30%>,
    "good_weather_stops": <count where rain <= 30%>,
    "efficiency_score": <0-1>,
    "confidence": <0-1>
  }},
  "weather_strategy": "Description of how ACTUAL weather (sunny/rainy) was leveraged",
  "execution_strategy": "Step-by-step plan",
  "risk_assessment": "Risks based on ACTUAL conditions"
}}"""

        try:
            chat_completion = self.groq_client.chat.completions.create(
                model=self.config.groq_model,
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            ai_response = chat_completion.choices[0].message.content
            
            import re
            cleaned = ai_response.strip()
            
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                cleaned = '\n'.join([l for l in lines if not l.strip().startswith('```')])
            
            cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
            
            json_start = cleaned.find('{')
            json_end = cleaned.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = cleaned[json_start:json_end]
                try:
                    ai_analysis = json.loads(json_str)
                except json.JSONDecodeError:
                    json_str = json_str.replace('\n', ' ').replace('\r', '')
                    ai_analysis = json.loads(json_str)
            else:
                raise ValueError("No valid JSON in response")
            
            ai_analysis['agent_id'] = self.agent_id
            ai_analysis['agent_type'] = 'orchestrator_with_weather'
            ai_analysis['city'] = self.config.city
            ai_analysis['timestamp'] = now.isoformat()
            ai_analysis['total_peaks_analyzed'] = len(viable_peaks)
            ai_analysis['event_peaks_count'] = len([p for p in viable_peaks if p['source'] == 'event'])
            ai_analysis['airport_peaks_count'] = len([p for p in viable_peaks if p['source'] == 'airport'])
            ai_analysis['weather_data_included'] = True
            ai_analysis['weather_summary'] = weather_summary
            ai_analysis['groq_model'] = self.config.groq_model
            
            return ai_analysis
            
        except json.JSONDecodeError as e:
            return {
                "status": "parse_error",
                "error": f"Failed to parse AI response: {str(e)}",
                "agent_id": self.agent_id,
                "timestamp": now.isoformat(),
                "raw_response_preview": ai_response[:500]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": now.isoformat()
            }
    
    def get_orchestrated_recommendation(self) -> Dict:
        """Main entry point - collects data from all agents and creates optimal plan with weather intelligence"""
        event_data, airport_data, weather_data = self.collector.collect_all_agent_data()
        optimal_plan = self.create_optimal_plan_with_ai(event_data, airport_data, weather_data)
        
        return {
            "event_agent_response": event_data,
            "airport_agent_response": airport_data,
            "weather_agent_response": weather_data,
            "orchestrator_response": optimal_plan
        }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    agent = OrchestratorAgent(config)
    result = agent.get_orchestrated_recommendation()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))