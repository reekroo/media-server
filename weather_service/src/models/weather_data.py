from collections import namedtuple

WeatherData = namedtuple(
    'WeatherData',
    [
        'location_name',
        'temperature',
        'feels_like',
        'pressure',
        'humidity',
        'description',
        'source'
    ]
)