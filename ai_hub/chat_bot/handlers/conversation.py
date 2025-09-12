from telegram import Update
from telegram.ext import ContextTypes
from langdetect import detect, LangDetectException

from chat_bot.messaging import reply_text_with_markdown
from chat_bot.rpc_client import call_mcp
from chat_bot.state import CONVERSATION_STATE, CONVERSATION_HISTORY
from chat_bot.models.chat_state import ConversationTurn, ChatState
from core.settings import Settings

async def on_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_text = update.message.text
    state = CONVERSATION_STATE.setdefault(chat_id, ChatState())
    
    if not state.lang:
        try:
            state.lang = detect(user_text)
        except LangDetectException:
            state.lang = Settings().DEFAULT_LANG

    if reply := update.message.reply_to_message:
        prompt = f"Context:\n---\n{reply.text}\n---\nUser question: {user_text}"
        response = await call_mcp("assist.raw_prompt", prompt=prompt)
    else:
        state.history.append(ConversationTurn(user=user_text, assistant=""))
        
        if len(state.history) > CONVERSATION_HISTORY:
            state.history.pop(0)

        response = await call_mcp("assist.chat", history=[turn.model_dump() for turn in state.history])        
        state.history[-1].assistant = response

    await reply_text_with_markdown(update, response)