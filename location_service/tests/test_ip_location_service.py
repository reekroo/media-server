import logging
from unittest.mock import MagicMock

from services.ip_location_service import IpLocationService

logger = logging.getLogger('test_logger')

def test_update_location_uses_first_provider_successfully():
    # Arrange
    mock_provider1 = MagicMock()
    mock_provider1.determine_location.return_value = {"lat": 1.1, "lon": 2.2}
    
    mock_provider2 = MagicMock()

    service = IpLocationService(providers=[mock_provider1, mock_provider2], logger=logger)
    
    # Act
    service.update_location()
    cached_location = service.get_cached_location()

    # Assert
    mock_provider1.determine_location.assert_called_once()
    mock_provider2.determine_location.assert_not_called()
    assert cached_location == {"lat": 1.1, "lon": 2.2}

def test_update_location_falls_back_to_second_provider():
    # Arrange
    mock_provider1 = MagicMock()
    mock_provider1.determine_location.return_value = None
    
    mock_provider2 = MagicMock()
    mock_provider2.determine_location.return_value = {"lat": 3.3, "lon": 4.4}

    service = IpLocationService(providers=[mock_provider1, mock_provider2], logger=logger)
    
    # Act
    service.update_location()
    cached_location = service.get_cached_location()

    # Assert
    mock_provider1.determine_location.assert_called_once()
    mock_provider2.determine_location.assert_called_once()
    assert cached_location == {"lat": 3.3, "lon": 4.4}