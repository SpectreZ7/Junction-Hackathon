import requests
import argparse
import os
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

    def summarize_forecast(self, data):
        """Make a nice summary of the forecast for hackathon use."""
        location = data["location"]["name"]
        summaries = []

        for forecast_day in data["forecast"]["forecastday"]:
            date = forecast_day["date"]
            condition = forecast_day["day"]["condition"]["text"]
            avg_temp = forecast_day["day"]["avgtemp_c"]
            max_temp = forecast_day["day"]["maxtemp_c"]
            min_temp = forecast_day["day"]["mintemp_c"]
            rain_chance = forecast_day["day"]["daily_chance_of_rain"]
            best_hour = self.estimate_best_uber_hour(forecast_day["hour"])

            summaries.append({
                "location": location,
                "date": date,
                "condition": condition,
                "avg_temp_c": avg_temp,
                "max_temp_c": max_temp,
                "min_temp_c": min_temp,
                "rain_chance_%": rain_chance,
                "best_hour_window": best_hour
            })

        return summaries
    
    def estimate_best_uber_hour(self, hourly_data):
        """Return the hour with highest likelihood of Uber demand based on cold + rain."""
        best_score = -1
        best_hour = None

        for hour in hourly_data:
            temp_c = hour["temp_c"]
            rain_chance = hour["chance_of_rain"]
            score = rain_chance + max(0, 15 - temp_c) 
            if score > best_score:
                best_score = score
                best_hour = hour["time"].split(" ")[1]

        return best_hour


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weather-key", help="Weather API key")
    parser.add_argument("--city", help="City to get weather for", required=1)
    parser.add_argument("--days", type=int, default=3, help="Number of forecast days")
    args = parser.parse_args()

    api_key = "7a22cd490a5046d9b48120123250410"
    if not api_key:
        raise ValueError("You must provide a Weather API key via --weather-key or WEATHER_API_KEY env var")

    agent = WeatherAgent(api_key)
    forecast_data = agent.get_forecast(args.city, days=args.days)
    summaries = agent.summarize_forecast(forecast_data)

    print("🌦 Weather Forecast Summary:")
    for day_summary in summaries:
        print(day_summary)
        print()
