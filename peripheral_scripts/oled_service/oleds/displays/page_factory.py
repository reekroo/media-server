#!/usr/bin/env python3
import os
from typing import List

def _profile_from_env_or_name(driver) -> str:
    p = os.getenv("OLED_PROFILE")
    if p: return p.strip().lower()
    name = driver.__class__.__name__.lower()
    if "1327" in name: return "ssd1327"
    if "1306" in name: return "ssd1306"
    return "ssd1327" if getattr(driver, "height", 64) >= 96 else "ssd1306"

def _weather_enabled() -> bool:
    v = os.getenv("OLED_ENABLE_WEATHER", "1").strip().lower()
    if v in ("0","false","off","no"): return False
    path = os.getenv("WEATHER_SERVICE_SOCKET", "/tmp/weather_service.sock")
    try:
        return os.path.exists(path)
    except Exception:
        return False

def _reorder(pages: List[object]) -> List[object]:
    order = os.getenv("OLED_PAGES")
    if not order:
        return pages
    
    key_to_page = {
        "perf":      next((p for p in pages if "performance" in p.__class__.__name__.lower()), None),
        "storage":   next((p for p in pages if "storage" in p.__class__.__name__.lower()), None),
        "network":   next((p for p in pages if "network" in p.__class__.__name__.lower()), None),
        "docker":    next((p for p in pages if "docker" in p.__class__.__name__.lower()), None),
        "health":    next((p for p in pages if "health" in p.__class__.__name__.lower()), None),
        "weather":   next((p for p in pages if "weather" in p.__class__.__name__.lower()), None),
        "system":    next((p for p in pages if "system" in p.__class__.__name__.lower()), None),
        "iofocus":   next((p for p in pages if "diskio" in p.__class__.__name__.lower() or "io" in p.__class__.__name__.lower()), None),
    }
    
    result = []
    
    for token in [t.strip().lower() for t in order.split(",")]:
        pg = key_to_page.get(token)
        if pg is not None:
            result.append(pg)
    
    return result or pages

def make_pages(driver) -> List[object]:
    profile = _profile_from_env_or_name(driver)

    if profile == "ssd1327":
        from oleds.displays.screens.ssd1327.performance_screen_1327 import PerformanceScreen1327
        from oleds.displays.screens.ssd1327.storage_screen_1327 import StorageScreen1327
        from oleds.displays.screens.ssd1327.network_screen_1327 import NetworkScreen1327
        from oleds.displays.screens.ssd1327.docker_screen_1327 import DockerScreen1327
        from oleds.displays.screens.ssd1327.health_screen_1327 import HealthScreen1327
        from oleds.displays.screens.ssd1327.system_screen_1327 import SystemScreen1327
        from oleds.displays.screens.ssd1327.disk_io_screen_1327 import DiskIOScreen1327

        pages: List[object] = [
          #  PerformanceScreen1327(),
          #  StorageScreen1327(),
            NetworkScreen1327(),
          #  DockerScreen1327(),
          #  HealthScreen1327(),
          #  SystemScreen1327(),
          #  DiskIOScreen1327(),
        ]
        
        if _weather_enabled():
            from .screens.ssd1327.weather_screen_1327 import WeatherScreen1327
            pages.append(WeatherScreen1327())
    else:
        from oleds.displays.screens.ssd1306.performance_screen import PerformanceScreen
        from oleds.displays.screens.ssd1306.storage_screen import StorageScreen
        from oleds.displays.screens.ssd1306.health_screen import HealthScreen

        pages = [
            PerformanceScreen(), 
            StorageScreen(), 
            HealthScreen()
        ]

    return _reorder(pages)
