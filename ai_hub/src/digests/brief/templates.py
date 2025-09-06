BRIEF_SYSTEM_HINT = (
    "You are an assistant generating a short morning brief. Be concise and practical. "
    "If earthquakes section is present, state trends & attention level without promising predictions."
)

BRIEF_FORMAT = """\
    🌤️ Weather
    {weather}
    
    🌍 Earthquakes
    {quakes}
    
    Have a good day!
"""
