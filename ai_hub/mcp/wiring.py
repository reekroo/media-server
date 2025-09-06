from .tools import weather, sys_digest, media, news, gaming, log_digest, news_tr, entertainment, dinner

def get_tool_functions():
    return {
        "weather.summary": weather.weather_summary,
        "sys.digest": sys_digest.system_digest,
        "media.digest": media.media_digest,
        "news.digest": news.news_digest,
        "gaming.digest": gaming.gaming_digest,
        "logs.analytics": log_digest.analytics_digest,
        "news.tr.digest": news_tr.turkish_news_digest,
        "entertainment.digest": entertainment.entertainment_digest,
        "dinner.suggest": dinner.dinner_ideas,
    }