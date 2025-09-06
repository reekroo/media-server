from .tools import weather, sys_digest, media, news, gaming

def get_tool_functions():
    return {
        "weather.summary": weather.weather_summary,
        "sys.digest": sys_digest.system_digest,
        "media.digest": media.media_digest,
        "news.digest": news.news_digest,
        "gaming.digest": gaming.gaming_digest,
    }