from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class CurrentWeather:
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    description: str
    icon: str
    sunrise: datetime
    sunset: datetime
    timezone_offset: int

@dataclass
class DailyForecast:
    date: str
    day_name: str
    temp_min: float
    temp_max: float
    description: str
    icon: str


@dataclass
class WeatherData:
    current: CurrentWeather
    forecast: List[DailyForecast]