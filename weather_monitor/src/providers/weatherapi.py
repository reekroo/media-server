import logging
from datetime import date

from .base import IWeatherProvider
from utils.http_client import HttpClient
from models.weather_data import WeatherData

class WeatherApiProvider(IWeatherProvider):
    BASE_URL = 'http://api.weatherapi.com/v1'

    def __init__(self, api_key: str, http_client: HttpClient, logger: logging.Logger):
        self._api_key = api_key
        self._http_client = http_client
        self.log = logger

    def get_current_weather(self, lat: float, lon: float) -> WeatherData | None:
        url = f"{self.BASE_URL}/current.json"
        params = {
            'key': self._api_key,
            'q': f"{lat},{lon}",
            'lang': 'ru'
        }
        try:
            self.log.info(f"Request to WeatherAPI for location {lat},{lon}...")
            data = self._http_client.get_json(url, params=params)
            self.log.info("WeatherAPI data received successfully.")
            
            current_weather = {
                "date": date.today().strftime('%Y-%m-%d'),
                "avg_temp_c": data['current']['temp_c'],
                "condition": data['current']['condition']['text'],
                "wind_speed_mps": round(data['current']['wind_kph'] * 1000 / 3600, 2),
                "humidity": data['current']['humidity'],
            }
            return [current_weather]
        except Exception as e:
            self.log.error(f"Failed to get weather from WeatherAPI: {e}")
            return None

    def get_forecast(self, lat: float, lon: float, days: int = 7) -> dict | None:
        url = f"{self.BASE_URL}/forecast.json"
        params = {
            'key': self._api_key,
            'q': f"{lat},{lon}",
            'days': days,
            'lang': 'ru'
        }
        try:
            self.log.info(f"Requesting {days}-day forecast from WeatherAPI for {lat},{lon}...")
            data = self._http_client.get_json(url, params=params)

            simplified_forecast = []
            raw_forecast_days = data.get('forecast', {}).get('forecastday', [])

            for day_data in raw_forecast_days:
                day_info = day_data.get('day', {})
                simplified_forecast.append({
                    "date": day_data.get('date'),
                    "max_temp_c": day_info.get('maxtemp_c'),
                    "min_temp_c": day_info.get('mintemp_c'),
                    "condition": day_info.get('condition', {}).get('text'),
                    "chance_of_rain_percent": day_info.get('daily_chance_of_rain'),
                })

            self.log.info(f"Successfully processed and simplified forecast data.")
            return simplified_forecast
        
        except Exception as e:
            self.log.error(f"Failed to get forecast from WeatherAPI: {e}")
            return None

    def get_historical(self, lat: float, lon: float, requested_date: date) -> dict | None:
        url = f"{self.BASE_URL}/history.json"
        params = {
            'key': self._api_key,
            'q': f"{lat},{lon}",
            'dt': requested_date.strftime('%Y-%m-%d')
        }
        try:
            self.log.info(f"Requesting historical data from WeatherAPI for {lat},{lon} on {requested_date}...")
            data = self._http_client.get_json(url, params=params)
            forecast_day = data.get('forecast', {}).get('forecastday', [{}])[0]
            day_info = forecast_day.get('day', {})
            
            simplified_historical = {
                "date": forecast_day.get('date'),
                "max_temp_c": day_info.get('maxtemp_c'),
                "min_temp_c": day_info.get('mintemp_c'),
                "avg_temp_c": day_info.get('avgtemp_c'),
                "condition": day_info.get('condition', {}).get('text'),
                "total_precip_mm": day_info.get('totalprecip_mm'),
            }
            return [simplified_historical]
            
        except Exception as e:
            self.log.error(f"Failed to get historical data from WeatherAPI: {e}")
            return None