import requests
from typing import Dict, Any

from src.config import (
    OPENWEATHER_API_KEY,
    CURRENT_WEATHER_URL,
    FORECAST_URL,
    DEFAULT_UNITS,
    DEFAULT_LANG
)
class WeatherService:
    def __init__(self):
        if not OPENWEATHER_API_KEY:
            raise ValueError("OpenWeatherMap API key is missing. Please set it in the .env file.")

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": DEFAULT_UNITS,
            "lang": DEFAULT_LANG
        }
        response = requests.get(CURRENT_WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_forecast(self, city: str) -> Dict[str, Any]:
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": DEFAULT_UNITS,
            "lang": DEFAULT_LANG
        }
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    def get_weather_data(self, city: str) -> Dict[str, Any]:
        current = self.get_current_weather(city)
        forecast = self.get_forecast(city)
        return {
            "current": current,
            "forecast": forecast
        }