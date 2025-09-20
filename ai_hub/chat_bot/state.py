import json
import logging
from pathlib import Path
from typing import Dict

from core.settings import Settings
from .models.chat_state import ChatState

log = logging.getLogger(__name__)

class StateManager:
    def __init__(self, settings: Settings):
        self._state_file: Path = settings.STATE_DIR / "chat_state.json"
        self._state: Dict[int, ChatState] = self._load()
        self.history_limit = 25
        log.info(f"StateManager initialized. Loaded {len(self._state)} chats from {self._state_file}")

    def _load(self) -> Dict[int, ChatState]:
        if not self._state_file.exists():
            return {}
        try:
            with self._state_file.open("r", encoding="utf-8") as f:
                raw_data = json.load(f)
                return {int(k): ChatState(**v) for k, v in raw_data.items()}
        except (json.JSONDecodeError, IOError, TypeError) as e:
            log.error(f"Could not load or parse state file {self._state_file}. Re-creating. Error: {e}")
            return {}

    def _save(self):
        try:
            serializable_state = {k: v.dict() for k, v in self._state.items()}
            with self._state_file.open("w", encoding="utf-8") as f:
                json.dump(serializable_state, f, indent=2, ensure_ascii=False)
        except IOError as e:
            log.error(f"Could not write to state file {self._state_file}: {e}")

    def get_chat_state(self, chat_id: int) -> ChatState:
        return self._state.setdefault(chat_id, ChatState())

    def save_chat_state(self, chat_id: int, state: ChatState):
        self._state[chat_id] = state
        self._save()

    def pop_chat_state(self, chat_id: int) -> ChatState | None:
        state = self._state.pop(chat_id, None)
        if state:
            self._save()
        return state

def get_available_digests(settings: Settings) -> list[str]:
    try:
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