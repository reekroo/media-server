import logging
from unittest.mock import MagicMock

from services.periodic_weather_service import PeriodicWeatherService
from models.weather_data import WeatherData

logger = logging.getLogger('test_logger')

def test_execute_main_cycle_success():
    fake_weather = WeatherData(location_name='Testville', temperature=22, feels_like=22, pressure=1015, humidity=60, description='Sunny', wind_speed=10, source='MockProvider')
    
    mock_weather_provider = MagicMock()
    mock_weather_provider.get_current_weather.return_value = fake_weather

    mock_location_provider = MagicMock()
    mock_location_provider.get_location.return_value = {"lat": 50.0, "lon": 10.0}
    
    mock_output = MagicMock()

    service = PeriodicWeatherService(
        weather_providers=[mock_weather_provider],
        outputs=[mock_output],
        location_providers=[mock_location_provider],
        logger=logger
    )
    service.execute_main_cycle()

    mock_location_provider.get_location.assert_called_once()
    mock_weather_provider.get_current_weather.assert_called_once_with(50.0, 10.0)
    mock_output.output.assert_called_once_with(fake_weather)