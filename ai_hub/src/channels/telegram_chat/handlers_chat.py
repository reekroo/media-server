import logging
from ...core.agents.base import Agent
from telegram.error import BadRequest

logger = logging.getLogger(__name__)

async def on_message(update, context):
    agent: Agent = context.bot_data["agent"]
    
    user_text = update.message.text
    response_msg = await update.message.reply_text("…")
    
    full_response = ""
    try:
        async for chunk in agent.stream(user_text):
            full_response = chunk
            if response_msg.text != full_response:
                await context.bot.edit_message_text(
                    chat_id=response_msg.chat.id,
                    message_id=response_msg.message_id,
                    text=full_response[:4000]
                )
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.warning(f"Failed to edit message: {e}")
    except Exception as e:
        logger.error(f"An error occurred during agent streaming: {e}", exc_info=True)
        try:
            await context.bot.edit_message_text(
                chat_id=response_msg.chat.id,
                message_id=response_msg.message_id,
                text="Sorry, an error occurred while processing your request."
            )
        except Exception:
            pass