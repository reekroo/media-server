from __future__ import annotations
from typing import Optional, Callable, Union, Any, Dict

ChatId = Union[int, str]

class TargetLanguageResolver:
    def __init__(self, default_lang: str, chat_lang_lookup: Callable[[ChatId], Optional[str]]):
        self.default_lang = (default_lang or "en").lower()
        self.lookup = chat_lang_lookup

    def resolve(self, conversation_lang: Optional[str], chat_id: Optional[ChatId]) -> str:
        if conversation_lang and conversation_lang.strip():
            return conversation_lang.strip().lower()
        if chat_id is not None:
            lang = self.lookup(chat_id)
            if lang:
                return lang
        return self.default_lang
