from telegram import Update
from telegram.ext import ContextTypes

from ..rpc_client import call_mcp
from ..state import CONVERSATION_HISTORY

async def on_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text

    history = CONVERSATION_HISTORY.setdefault(chat_id, [])
    
    if reply := update.message.reply_to_message:
        prompt = f"Context:\n---\n{reply.text}\n---\nUser question: {user_text}"
        response = await call_mcp("assist.raw_prompt", prompt=prompt)
    else:
        history.append({"user": user_text, "assistant": ""})
        
        if len(history) > 10:
            history.pop(0)

        response = await call_mcp("assist.chat", history=history)        
        history[-1]["assistant"] = response

    await update.message.reply_text(response)