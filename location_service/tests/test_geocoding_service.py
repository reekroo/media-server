import logging
from unittest.mock import MagicMock

from services.geocoding_service import GeocodingService

logger = logging.getLogger('test_logger')

def test_geocode_city_calls_provider_correctly():
    # Arrange
    mock_provider = MagicMock()
    mock_provider.determine_location.return_value = {"status": "success", "lat": 50.0, "lon": 30.0}
    
    service = GeocodingService(provider=mock_provider, logger=logger)
    city_to_test = "Kyiv"
    
    # Act
    result = service.geocode_city(city_to_test)
    
    # Assert
    mock_provider.determine_location.assert_called_once_with(city_name=city_to_test)
    assert result == {"status": "success", "lat": 50.0, "lon": 30.0}