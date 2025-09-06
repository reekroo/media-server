import logging
from telegram.error import BadRequest
from ...core.agents.base import Agent

logger = logging.getLogger(__name__)

async def on_message(update, context):
    """Handles general text messages, including replies for context."""
    agent: Agent = context.bot_data["agent"]
    
    user_text = update.message.text
    
    # --- НОВАЯ ЛОГИКА: ПРОВЕРКА НА REPLY ---
    prompt = user_text
    reply_message = update.message.reply_to_message

    # Если это ответ и в оригинальном сообщении есть текст
    if reply_message and reply_message.text:
        # Мы создаем более сложный промпт для AI
        original_digest_text = reply_message.text
        user_question = user_text
        
        prompt = (
            "You are a helpful assistant. A user is asking a follow-up question about a message you previously sent. "
            "Use the 'Original Message' as context to answer the 'User's Question'.\n\n"
            f"--- Original Message ---\n{original_digest_text}\n\n"
            f"--- User's Question ---\n{user_question}\n\n"
            "Your Answer:"
        )
        logger.info("Handling a reply, providing context to the agent.")

    # --- КОНЕЦ НОВОЙ ЛОГИКИ ---

    response_msg = await update.message.reply_text("…")
    
    full_response = ""
    try:
        # Отправляем наш новый (или старый) промпт агенту
        async for chunk in agent.stream(prompt):
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