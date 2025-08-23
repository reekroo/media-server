from location_logger import get_logger
from location_controller import LocationController
from providers.ipinfo_provider import IpInfoProvider
from providers.config_provider import ConfigFallbackProvider

log = get_logger(__name__)

def main():
    log.info("Starting Location Service...")
    
    providers = [
        IpInfoProvider(),
        ConfigFallbackProvider()
    ]
    
    service = LocationController(providers=providers)
    service.run()
    
    log.info("Location Service has stopped.")

if __name__ == "__main__":
    main()