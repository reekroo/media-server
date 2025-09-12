from pydantic import BaseModel, Field
from typing import List, Optional

class ConversationTurn(BaseModel):
    user: str
    assistant: str

class ChatState(BaseModel):
    lang: Optional[str] = None
    history: List[ConversationTurn] = Field(default_factory=list)