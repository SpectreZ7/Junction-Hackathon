# Event Intelligence Agent - Production Version

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

CITY = "New York"
HOURS_AHEAD = 12
PEAK_THRESHOLD = 500
USE_DEMO_MODE = True

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.4
MAX_TOKENS = 1500

POST_EVENT_DELAY_MINUTES = 15
AVG_EVENT_FARE = 150
WAITING_COST_PER_MINUTE = 0.8

DEMO_VENUES = {
    "New York": [
        {"name": "Madison Square Garden", "lat": 40.7505, "lng": -73.9934, "capacity": 20000},
        {"name": "Barclays Center", "lat": 40.6826, "lng": -73.9754, "capacity": 17732},
        {"name": "Yankee Stadium", "lat": 40.8296, "lng": -73.9262, "capacity": 46537},
        {"name": "Radio City Music Hall", "lat": 40.7599, "lng": -73.9799, "capacity": 6000},
        {"name": "Brooklyn Steel", "lat": 40.7183, "lng": -73.9571, "capacity": 1800},
        {"name": "Terminal 5", "lat": 40.7677, "lng": -73.9887, "capacity": 3000},
        {"name": "Webster Hall", "lat": 40.7298, "lng": -73.9891, "capacity": 1500}
    ]
}

class EventAIAgentConfig:
    def __init__(self, city: str, hours_ahead: int):
        self.groq_api_key = GROQ_API_KEY
        self.groq_model = GROQ_MODEL
        self.city = city
        self.hours_ahead = hours_ahead
        self.peak_threshold = PEAK_THRESHOLD
        self.post_event_delay_minutes = POST_EVENT_DELAY_MINUTES
        self.avg_event_fare = AVG_EVENT_FARE
        self.waiting_cost_per_minute = WAITING_COST_PER_MINUTE
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS
        self.system_prompt = "You are an AI agent specialized in revenue optimization for Uber drivers. Respond ONLY in valid JSON."

config = EventAIAgentConfig(city=CITY, hours_ahead=HOURS_AHEAD)

class DemoEventGenerator:
    def __init__(self, city: str, hours_ahead: int):
        self.city = city
        self.hours_ahead = hours_ahead
        self.venues = DEMO_VENUES.get(city, [])
    
    def generate_events(self) -> List[Dict]:
        """Generate realistic events from a pool of possibilities"""
        now = datetime.now()
        events = []
        
        # Large pool of realistic events
        event_pool = [
            # Sports
            {"type": "sports", "name": "Knicks vs Lakers", "venue": "Madison Square Garden", "duration": 150, "capacity_fill": 0.85},
            {"type": "sports", "name": "Rangers vs Bruins", "venue": "Madison Square Garden", "duration": 180, "capacity_fill": 0.80},
            {"type": "sports", "name": "Nets vs Celtics", "venue": "Barclays Center", "duration": 150, "capacity_fill": 0.75},
            {"type": "sports", "name": "Yankees vs Red Sox", "venue": "Yankee Stadium", "duration": 180, "capacity_fill": 0.90},
            {"type": "sports", "name": "Liberty Basketball", "venue": "Barclays Center", "duration": 120, "capacity_fill": 0.60},
            
            # Concerts - Big
            {"type": "concerts", "name": "Taylor Swift - Eras Tour", "venue": "Madison Square Garden", "duration": 180, "capacity_fill": 1.0},
            {"type": "concerts", "name": "The Weeknd Live", "venue": "Barclays Center", "duration": 150, "capacity_fill": 0.95},
            {"type": "concerts", "name": "Beyoncé Concert", "venue": "Madison Square Garden", "duration": 165, "capacity_fill": 1.0},
            {"type": "concerts", "name": "Drake World Tour", "venue": "Barclays Center", "duration": 150, "capacity_fill": 0.90},
            
            # Concerts - Medium
            {"type": "concerts", "name": "Indie Rock Night", "venue": "Radio City Music Hall", "duration": 120, "capacity_fill": 0.70},
            {"type": "concerts", "name": "Jazz Performance", "venue": "Radio City Music Hall", "duration": 90, "capacity_fill": 0.65},
            {"type": "concerts", "name": "Electronic Music Festival", "venue": "Brooklyn Steel", "duration": 240, "capacity_fill": 0.85},
            {"type": "concerts", "name": "Hip Hop Showcase", "venue": "Terminal 5", "duration": 150, "capacity_fill": 0.75},
            {"type": "concerts", "name": "Alternative Band Tour", "venue": "Webster Hall", "duration": 120, "capacity_fill": 0.80},
            
            # Theater & Shows
            {"type": "performing-arts", "name": "Broadway Musical", "venue": "Radio City Music Hall", "duration": 150, "capacity_fill": 0.85},
            {"type": "performing-arts", "name": "Comedy Show", "venue": "Madison Square Garden", "duration": 120, "capacity_fill": 0.70},
            {"type": "performing-arts", "name": "Stand-up Comedy Night", "venue": "Webster Hall", "duration": 90, "capacity_fill": 0.60},
            
            # Conferences
            {"type": "conferences", "name": "Tech Summit NYC", "venue": "Barclays Center", "duration": 480, "capacity_fill": 0.50},
            {"type": "conferences", "name": "Marketing Conference", "venue": "Madison Square Garden", "duration": 360, "capacity_fill": 0.45},
            {"type": "conferences", "name": "Startup Meetup", "venue": "Terminal 5", "duration": 180, "capacity_fill": 0.40},
        ]
        
        # Randomly select 4-8 events that happen today
        num_events = np.random.randint(4, 9)
        selected_events = np.random.choice(event_pool, size=min(num_events, len(event_pool)), replace=False)
        
        for i, event_data in enumerate(selected_events):
            # Find the venue details
            venue = next((v for v in self.venues if v["name"] == event_data["venue"]), self.venues[0])
            
            # Generate realistic start time within analysis window
            # Simple approach: random offset between 1 hour and hours_ahead
            hours_offset = np.random.uniform(1, self.hours_ahead)
            start_time = now + timedelta(hours=hours_offset)
            
            # Round to nearest 15 minutes for realism
            minute = (start_time.minute // 15) * 15
            start_time = start_time.replace(minute=minute, second=0, microsecond=0)
            
            # Double check it's in the future
            if start_time <= now:
                continue
            
            # Calculate attendees
            estimated_attendees = int(venue["capacity"] * event_data["capacity_fill"])
            
            events.append({
                'event_id': f'event_{i}_{int(start_time.timestamp())}',
                'name': event_data["name"],
                'type': event_data["type"],
                'venue_name': venue["name"],
                'start_time': start_time,
                'estimated_duration_minutes': event_data["duration"],
                'estimated_attendees': estimated_attendees,
                'phq_rank': min(int((estimated_attendees / 200) + 40), 95),
                'location': {
                    'lat': venue["lat"],
                    'lng': venue["lng"],
                    'address': venue["name"]
                },
                'labels': [event_data["type"]]
            })
        
        # Sort by start time
        events.sort(key=lambda x: x['start_time'])
        
        return events
    
class EventIntelligenceAgent:
    def __init__(self, config: EventAIAgentConfig):
        self.config = config
        self.agent_id = f"event_agent_{config.city.lower().replace(' ', '_')}"
        self.groq_client = Groq(api_key=config.groq_api_key)
        self.demo_generator = DemoEventGenerator(config.city, config.hours_ahead)
    
    def get_recommendation(self) -> Dict:
        events = self.demo_generator.generate_events()
        
        if not events:
            return {"status": "no_events", "city": self.config.city, "message": "No events"}
        
        return self.analyze_with_ai(events)
    
    def analyze_with_ai(self, events_data: List[Dict]) -> Dict:
        now = datetime.now()
        
        events_summary = []
        for event in events_data[:20]:
            end_time = event['start_time'] + timedelta(minutes=event['estimated_duration_minutes'])
            peak_time = end_time + timedelta(minutes=self.config.post_event_delay_minutes)
            
            events_summary.append({
                'event': event['name'],
                'venue': event['venue_name'],
                'end_time': end_time.strftime('%H:%M'),
                'peak_time': peak_time.strftime('%H:%M'),
                'attendees': event['estimated_attendees']
            })
        
        user_prompt = f"""Events in {self.config.city}:
{json.dumps(events_summary, indent=2)}

Identify ALL event peaks (end time + 15min). Respond in JSON:
{{"peaks_identified": [{{"time_window": "23:00-23:30", "event_name": "Concert", "venue_name": "MSG", "estimated_attendees": 20000, "priority": "high"}}],
"recommendation": {{"action": "go", "target_peak": "23:00-23:30", "reasoning": "Large event", "expected_revenue": 45, "waiting_time_minutes": 15, "confidence": 0.88}},
"analysis": "Summary"}}"""

        # Force mock data for testing
        if True:  # Change to False to use real AI
            # Return mock events when AI fails
            mock_peaks = [
                {
                    "time_window": "14:00-14:30",
                    "event_name": "Knicks vs Lakers",
                    "venue_name": "Madison Square Garden",
                    "estimated_attendees": 20000,
                    "priority": "high"
                },
                {
                    "time_window": "19:00-19:30", 
                    "event_name": "Taylor Swift Concert",
                    "venue_name": "Madison Square Garden",
                    "estimated_attendees": 20000,
                    "priority": "high"
                },
                {
                    "time_window": "20:00-20:30",
                    "event_name": "Broadway Show",
                    "venue_name": "Radio City Music Hall", 
                    "estimated_attendees": 6000,
                    "priority": "medium"
                }
            ]
            
            return {
                "peaks_identified": mock_peaks,
                "recommendation": {
                    "action": "go",
                    "target_peak": "14:00-14:30",
                    "reasoning": "High attendance event",
                    "expected_revenue": 45,
                    "waiting_time_minutes": 15,
                    "confidence": 0.9
                },
                "analysis": "Mock events for testing",
                "agent_id": self.agent_id,
                "city": self.config.city,
                "timestamp": now.isoformat(),
                "total_events_analyzed": len(mock_peaks),
                "avg_event_fare": self.config.avg_event_fare
            }
        
        try:
            chat_completion = self.groq_client.chat.completions.create(
                model=self.config.groq_model,
                messages=[{"role": "system", "content": self.config.system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            ai_response = chat_completion.choices[0].message.content
            cleaned = ai_response.strip()
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                cleaned = '\n'.join([l for l in lines if not l.strip().startswith('```')])
            
            json_start = cleaned.find('{')
            json_end = cleaned.rfind('}') + 1
            ai_analysis = json.loads(cleaned[json_start:json_end])
            ai_analysis['agent_id'] = self.agent_id
            ai_analysis['city'] = self.config.city
            ai_analysis['timestamp'] = now.isoformat()
            ai_analysis['total_events_analyzed'] = len(events_data)
            ai_analysis['avg_event_fare'] = self.config.avg_event_fare
            return ai_analysis
        except:
            # Return mock events when AI fails
            mock_peaks = [
                {
                    "time_window": "14:00-14:30",
                    "event_name": "Knicks vs Lakers",
                    "venue_name": "Madison Square Garden",
                    "estimated_attendees": 20000,
                    "priority": "high"
                },
                {
                    "time_window": "19:00-19:30", 
                    "event_name": "Taylor Swift Concert",
                    "venue_name": "Madison Square Garden",
                    "estimated_attendees": 20000,
                    "priority": "high"
                },
                {
                    "time_window": "20:00-20:30",
                    "event_name": "Broadway Show",
                    "venue_name": "Radio City Music Hall", 
                    "estimated_attendees": 6000,
                    "priority": "medium"
                }
            ]
            
            return {
                "peaks_identified": mock_peaks,
                "recommendation": {
                    "action": "go",
                    "target_peak": "14:00-14:30",
                    "reasoning": "High attendance event",
                    "expected_revenue": 45,
                    "waiting_time_minutes": 15,
                    "confidence": 0.9
                },
                "analysis": "Mock events for testing",
                "agent_id": self.agent_id,
                "city": self.config.city,
                "timestamp": now.isoformat(),
                "total_events_analyzed": len(mock_peaks),
                "avg_event_fare": self.config.avg_event_fare
            }

class AgentMessage:
    @staticmethod
    def format_for_orchestrator(agent_id: str, recommendation: Dict) -> Dict:
        if recommendation.get('status') in ['error', 'no_events']:
            return {"agent_id": agent_id, "agent_type": "event_intelligence", "timestamp": datetime.now().isoformat(), "priority": 0.0, "all_peaks": [], "best_recommendation": None}
        
        rec = recommendation.get('recommendation', {})
        all_peaks = recommendation.get('peaks_identified', [])
        
        confidence = rec.get('confidence', 0.5)
        revenue = rec.get('expected_revenue', 0)
        wait_time = max(rec.get('waiting_time_minutes', 60), 1)
        global_priority = min(max((revenue / wait_time) * confidence / 100, 0), 1)
        
        formatted_peaks = []
        for i, peak in enumerate(all_peaks):
            formatted_peaks.append({
                "peak_id": f"{agent_id}_peak_{i+1}",
                "time_window": peak.get('time_window', 'N/A'),
                "event_name": peak.get('event_name', 'N/A'),
                "venue_name": peak.get('venue_name', 'N/A'),
                "estimated_attendees": peak.get('estimated_attendees', 0),
                "priority": peak.get('priority', 'medium'),
                "is_recommended": (i == 0)
            })
        
        return {
            "agent_id": agent_id,
            "agent_type": "event_intelligence",
            "timestamp": datetime.now().isoformat(),
            "priority": round(global_priority, 3),
            "all_peaks": formatted_peaks,
            "best_recommendation": {"action": rec.get('action'), "target_peak": rec.get('target_peak'), "reasoning": rec.get('reasoning')},
            "metadata": {"total_peaks_detected": len(all_peaks), "events_analyzed": recommendation.get('total_events_analyzed', 0)}
        }
