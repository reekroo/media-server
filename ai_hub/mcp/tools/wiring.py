from .tools import weather, sys_digest, media

def get_tools():
    return {
        "weather.summary": weather.weather_summary,
        "sys.digest": sys_digest.system_digest,
        "media.digest": media.media_digest,
    }
