from ...core.agents.factory import agent_factory
from ...core.settings import Settings

async def on_message(update, context):
    text = update.message.text
    agent = agent_factory(Settings().GEMINI_API_KEY)
    msg = await update.message.reply_text("…")
    acc = ""
    async for chunk in agent.stream(text):
        acc = chunk
        try:
            await context.bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=acc[:4000])
        except Exception:
            pass
