from src.topics.weather import WeatherSummary

def test_weather_prompt_builds():
    h = WeatherSummary()
    p = h.build_prompt({"temp_c": 25})
    assert "temp_c" in p
