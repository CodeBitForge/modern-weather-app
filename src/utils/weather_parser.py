from datetime import datetime, timezone, timedelta
from collections import Counter
from typing import Dict, Any, List

from src.models.weather import CurrentWeather, DailyForecast, WeatherData

def parse_current_weather(data: Dict[str, Any]) -> CurrentWeather:
    main = data["main"]
    weather = data["weather"][0]
    wind = data["wind"]
    sys_info = data["sys"]
    timezone_offset = data["timezone"]

    local_offset = timedelta(seconds=timezone_offset)
    sunrise = datetime.fromtimestamp(sys_info["sunrise"], tz=timezone.utc) + local_offset
    sunset = datetime.fromtimestamp(sys_info["sunset"], tz=timezone.utc) + local_offset
    return CurrentWeather(
        city=data["name"],
        country=sys_info["country"],
        temperature=main["temp"],
        feels_like=main["feels_like"],
        humidity=main["humidity"],
        wind_speed=wind["speed"],
        description=weather["description"].capitalize(),
        icon=weather["main"],
        sunrise=sunrise,
        sunset=sunset,
        timezone_offset=timezone_offset
    )

def parse_forecast(data: Dict[str, Any]) -> List[DailyForecast]:
    daily = {}

    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        temp_min = item["main"]["temp_min"]
        temp_max = item["main"]["temp_max"]
        main_weather = item["weather"][0]["main"]

        if date not in daily:
            daily[date] = {
                "temp_min": temp_min,
                "temp_max": temp_max,
                "weathers": []
            }

        daily[date]["temp_min"] = min(daily[date]["temp_min"], temp_min)
        daily[date]["temp_max"] = max(daily[date]["temp_max"], temp_max)
        daily[date]["weathers"].append(main_weather)

    result = []
    persian_days = {
        "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه",
        "Wednesday": "چهارشنبه",
        "Thursday": "پنج‌شنبه",
        "Friday": "جمعه",
        "Saturday": "شنبه",
        "Sunday": "یکشنبه"
    }

    for date, values in list(daily.items())[:5]:
        counter = Counter(values["weathers"])
        important = ["Snow", "Thunderstorm", "Rain", "Drizzle"]

        if any(cond in counter for cond in important):
            important_counter = {k: counter[k] for k in counter if k in important}
            dominant = max(important_counter, key=important_counter.get)
        else:
            dominant = counter.most_common(1)[0][0]

        dt = datetime.strptime(date, "%Y-%m-%d")
        day_name = persian_days.get(dt.strftime("%A"), dt.strftime("%A"))

        result.append(DailyForecast(
            date=date,
            day_name=day_name,
            temp_min=values["temp_min"],
            temp_max=values["temp_max"],
            description=dominant,
            icon=dominant
        ))

    return result

def parse_weather_data(current_data: Dict[str, Any], forecast_data: Dict[str, Any]) -> WeatherData:
    current = parse_current_weather(current_data)
    forecast = parse_forecast(forecast_data)
    return WeatherData(current=current, forecast=forecast)