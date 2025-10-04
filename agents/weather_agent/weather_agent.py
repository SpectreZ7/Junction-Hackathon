import requests
import json
from datetime import datetime

class WeatherAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1"
    
    def get_forecast(self, city, days=1):
        """Fetch weather forecast for a city for a number of days (1–3 on free plan)."""
        url = f"{self.base_url}/forecast.json"
        params = {
            "key": self.api_key,
            "q": city,
            "days": days,
            "aqi": "no",
            "alerts": "no"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    
    def get_hourly_forecast_24h(self, data):
        """Get hourly weather data for the next 24 hours."""
        location = data["location"]["name"]
        hourly_forecasts = []
        
        # Get current time from API response
        current_time = datetime.fromisoformat(data["location"]["localtime"])
        current_hour = current_time.hour
        
        hours_collected = 0
        
        # Iterate through forecast days
        for forecast_day in data["forecast"]["forecastday"]:
            date = forecast_day["date"]
            
            # Iterate through hours in each day
            for hour_data in forecast_day["hour"]:
                # Parse the hour from the time string (format: "YYYY-MM-DD HH:MM")
                hour_time = datetime.fromisoformat(hour_data["time"])
                
                # Only include future hours and limit to 24 hours
                if hour_time >= current_time and hours_collected < 24:
                    hourly_forecasts.append({
                        "location": location,
                        "datetime": hour_data["time"],
                        "hour": hour_time.strftime("%H:%M"),
                        "temp_c": hour_data["temp_c"],
                        "feels_like_c": hour_data["feelslike_c"],
                        "condition": hour_data["condition"]["text"],
                        "wind_kph": hour_data["wind_kph"],
                        "wind_dir": hour_data["wind_dir"],
                        "pressure_mb": hour_data["pressure_mb"],
                        "humidity_percent": hour_data["humidity"],
                        "cloud_percent": hour_data["cloud"],
                        "rain_chance_percent": hour_data["chance_of_rain"],
                        "precip_mm": hour_data["precip_mm"],
                        "visibility_km": hour_data["vis_km"],
                        "uv_index": hour_data["uv"]
                    })
                    hours_collected += 1
                
                # Stop if we have 24 hours
                if hours_collected >= 24:
                    break
            
            if hours_collected >= 24:
                break
        
        return hourly_forecasts
    
    def estimate_best_uber_hours(self, hourly_data, top_n=5):
        """Return the top N hours with highest likelihood of Uber demand based on cold + rain."""
        scored_hours = []
        
        for hour in hourly_data:
            temp_c = hour["temp_c"]
            rain_chance = hour["rain_chance_percent"]
            # Score basé sur la pluie et le froid (plus c'est élevé, plus la demande est forte)
            score = rain_chance + max(0, 15 - temp_c)
            
            scored_hours.append({
                "hour": hour["hour"],
                "datetime": hour["datetime"],
                "score": round(score, 2),
                "temp_c": temp_c,
                "rain_chance_percent": rain_chance,
                "condition": hour["condition"]
            })
        
        # Trier par score décroissant
        scored_hours.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_hours[:top_n]
    
    def get_weather_analysis(self, city):
        """Get complete weather analysis for optimal ride scheduling."""
        forecast_data = self.get_forecast(city, days=2)
        hourly_forecast = self.get_hourly_forecast_24h(forecast_data)
        best_hours = self.estimate_best_uber_hours(hourly_forecast, top_n=5)
        
        analysis = {
            "city": city,
            "forecast_generated_at": datetime.now().isoformat(),
            "hourly_forecast_24h": hourly_forecast,
            "optimal_ride_hours": best_hours,
            "summary": {
                "total_hours_analyzed": len(hourly_forecast),
                "avg_temp_c": round(sum(h["temp_c"] for h in hourly_forecast) / len(hourly_forecast), 1),
                "avg_rain_chance": round(sum(h["rain_chance_percent"] for h in hourly_forecast) / len(hourly_forecast), 1),
                "best_hour_recommendation": best_hours[0]["datetime"] if best_hours else None
            }
        }
        
        return analysis

if __name__ == "__main__":
    # Configuration en dur
    api_key = "7a22cd490a5046d9b48120123250410"
    city = "New York"  # Changez la ville ici
    
    if not api_key:
        raise ValueError("You must provide a Weather API key")
    
    agent = WeatherAgent(api_key)
    weather_analysis = agent.get_weather_analysis(city)
    
    # Sortie JSON uniquement
    print(json.dumps(weather_analysis, indent=2, ensure_ascii=False))