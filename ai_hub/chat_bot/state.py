from pathlib import Path
from core.settings import Settings

CONVERSATION_HISTORY: dict[int, list[dict[str, str]]] = {}

def get_available_digests() -> list[str]:
    try:
        settings = Settings()
        configs_path = settings.BASE_DIR / "configs"
        excluded_files = {"schedule.toml", "chat.toml"}
        digest_names = []
        if configs_path.is_dir():
            for f in configs_path.glob("*.toml"):
                if f.name not in excluded_files:
                    digest_names.append(f.stem)
        return sorted(digest_names)
    except Exception:
        return []