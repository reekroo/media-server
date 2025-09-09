import logging
from ...core.agents.base import Agent
from telegram.error import BadRequest

logger = logging.getLogger(__name__)

async def on_message(update, context):
    agent: Agent = context.bot_data.get("agent")
    if not agent:
        logger.error("Agent not found in bot_data context.")
        return

    user_text = update.message.text
    prompt = user_text
    reply_message = update.message.reply_to_message

    if reply_message and reply_message.text:
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

    response_msg = await update.message.reply_text("…")
    
    full_response = ""
    try:
        async for chunk in agent.stream(prompt):
            full_response = chunk
            if response_msg.text != full_response:
                await context.bot.edit_message_text(
                    chat_id=response_msg.chat.id,
                    message_id=response_msg.message_id,
                    text=full_response[:4000],
                    parse_mode='Markdown'
                )
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.warning(f"Failed to edit message: {e}")
    except Exception as e:
        logger.error(f"An error occurred during agent streaming: {e}", exc_info=True)
        try:
            await context.bot.edit_message_text(
                chat_id=response_msg.chat_id,
                message_id=response_msg.message_id,
                text="Sorry, an error occurred while processing your request.",
            )
        except Exception:
            pass