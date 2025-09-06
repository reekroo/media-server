async def cmd_start(update, context):
    await update.message.reply_text("Hi! I'm your AI Hub bot. Use /why <incident_id> for system incident details, /reset to clear context.")
cmd_help = cmd_start
