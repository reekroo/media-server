import configs as config
from weather_logger import get_logger
from providers.openweathermap import OpenWeatherMapProvider
from providers.weatherapi import WeatherApiProvider
from outputs.console_output import ConsoleOutput
from outputs.socket_output import SocketOutput
from weather_controller import WeatherController

log = get_logger(__name__)

def main():
    log.info("Weather Service application starting...")

    output_strategies = []
    output_factories = {
        'console': ConsoleOutput,
        'socket': lambda: SocketOutput(socket_path=config.SOCKET_FILE)
    }
    
    for mode in config.OUTPUT_MODES:
        if mode in output_factories:
            output_strategies.append(output_factories[mode]())
            log.info(f"Output mode enabled: {mode}")
    
    if not output_strategies:
        log.warning("No output modes configured. Service will run silently.")

    providers = [
        OpenWeatherMapProvider(api_key=config.OPENWEATHERMAP_API_KEY),
        WeatherApiProvider(api_key=config.WEATHERAPI_API_KEY)
    ]

    controller = WeatherController(
        providers=providers,
        outputs=output_strategies,
        lat=config.LATITUDE,
        lon=config.LONGITUDE
    )
    
    controller.run(interval_seconds=config.INTERVAL_SECONDS)

if __name__ == "__main__":
    main()